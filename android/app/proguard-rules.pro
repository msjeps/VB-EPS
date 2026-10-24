# Règles ProGuard pour VB EPS WebView wrapper
# L'interface JS→Java doit rester visible depuis le WebView
-keepclassmembers class com.eps.vbeps.MainActivity$DownloadInterface {
    @android.webkit.JavascriptInterface <methods>;
}
