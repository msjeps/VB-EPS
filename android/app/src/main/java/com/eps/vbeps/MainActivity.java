package com.eps.vbeps;

import android.annotation.SuppressLint;
import android.Manifest;
import android.app.Activity;
import android.content.ContentValues;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

public class MainActivity extends Activity {

    private static final int REQ_STORAGE = 42;
    private static final String ASSET_HOST = "file:///android_asset/";

    private WebView webView;

    // Fichier en attente quand la permission stockage (Android 6-9) doit être demandée
    private byte[] pendingData;
    private String pendingName;
    private String pendingMime;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Plein écran immersif
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        // Écran toujours allumé (Wake Lock API pas fiable sur tablettes figées)
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        masquerBarresSysteme();

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();

        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Accès aux assets locaux uniquement — les flags d'accès inter-fichiers restent à false
        // (valeur par défaut depuis Android 4.1 ; explicitement désactivés ici pour contrer la
        // faille "WebView universal file access" identifiée par l'audit de sécurité 2026-10-24)
        settings.setAllowFileAccess(true);          // assets/ de l'app seulement
        settings.setAllowContentAccess(false);      // pas d'accès aux content:// providers
        settings.setAllowFileAccessFromFileURLs(false);      // fix sécurité audit finding #3
        settings.setAllowUniversalAccessFromFileURLs(false); // fix sécurité audit finding #3

        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(false);
        settings.setDefaultTextEncodingName("UTF-8");

        // Navigation restreinte aux assets de l'app (fix audit finding #3)
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                return !url.startsWith(ASSET_HOST);
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return !url.startsWith(ASSET_HOST);
            }
        });

        // Interface JS → Java pour les téléchargements CSV
        // (blob: URLs non gérées par WebView — AndroidDownload.saveFile() est le seul chemin fiable)
        webView.addJavascriptInterface(new DownloadInterface(), "AndroidDownload");

        webView.setWebChromeClient(new WebChromeClient());

        webView.loadUrl(ASSET_HOST + "index.html");
    }

    @SuppressWarnings("deprecation")
    private void masquerBarresSysteme() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) masquerBarresSysteme();
    }

    // Le bouton Retour est délégué à la page HTML (window.__androidBack).
    // Si la fonction retourne "quit", l'Activity se termine.
    @Override
    public void onBackPressed() {
        if (webView == null) { super.onBackPressed(); return; }
        webView.evaluateJavascript(
            "(function(){return window.__androidBack?window.__androidBack():'quit';})()",
            new ValueCallback<String>() {
                @Override
                public void onReceiveValue(String value) {
                    if (value != null && value.contains("quit")) finish();
                }
            });
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.evaluateJavascript("document.dispatchEvent(new Event('visibilitychange'));", null);
        }
    }

    /**
     * Interface JavaScript pour sauvegarder le CSV depuis le WebView.
     * Appelée via : AndroidDownload.saveFile(contenuBase64, nomFichier, typeMime)
     * Le nom de fichier et le type MIME sont assainis côté Kotlin avant écriture.
     */
    public class DownloadInterface {
        @JavascriptInterface
        public void saveFile(String base64Data, String fileName, String mimeType) {
            final byte[] data = Base64.decode(base64Data, Base64.DEFAULT);
            // Assainissement : on retire les séparateurs de chemin et caractères dangereux
            final String safeName = fileName.replaceAll("[\\\\/:*?\"<>|]", "_");
            // Type MIME limité aux types attendus pour VB EPS
            final String safeMime = (mimeType != null && mimeType.startsWith("text/")) ? mimeType : "text/csv";
            // Limite de taille : 5 Mo max (un CSV VB EPS ne dépasse pas quelques dizaines de Ko)
            if (data.length > 5 * 1024 * 1024) {
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        Toast.makeText(MainActivity.this, "❌ Fichier trop volumineux", Toast.LENGTH_LONG).show();
                    }
                });
                return;
            }
            runOnUiThread(new Runnable() {
                @Override public void run() { ecrire(data, safeName, safeMime); }
            });
        }
    }

    private void ecrire(byte[] data, String fileName, String mimeType) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, fileName);
                values.put(MediaStore.Downloads.MIME_TYPE, mimeType);
                values.put(MediaStore.Downloads.IS_PENDING, 1);
                android.net.Uri uri = getContentResolver().insert(
                        MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new Exception("création du fichier impossible");
                OutputStream os = getContentResolver().openOutputStream(uri);
                if (os == null) throw new Exception("écriture impossible");
                try { os.write(data); } finally { os.close(); }
                values.clear();
                values.put(MediaStore.Downloads.IS_PENDING, 0);
                getContentResolver().update(uri, values, null, null);
            } else {
                if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                        != PackageManager.PERMISSION_GRANTED) {
                    pendingData = data;
                    pendingName = fileName;
                    pendingMime = mimeType;
                    requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_STORAGE);
                    return;
                }
                File dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                if (!dir.exists()) dir.mkdirs();
                FileOutputStream fos = new FileOutputStream(new File(dir, fileName));
                try { fos.write(data); } finally { fos.close(); }
            }
            Toast.makeText(this, "✅ " + fileName + " sauvegardé dans Téléchargements", Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this, "❌ Erreur : " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_STORAGE) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED && pendingData != null) {
            ecrire(pendingData, pendingName, pendingMime);
        } else {
            Toast.makeText(this, "❌ Permission refusée : fichier non sauvegardé", Toast.LENGTH_LONG).show();
        }
        pendingData = null;
    }
}
