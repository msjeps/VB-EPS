#!/usr/bin/env python3
"""Génère vb-eps.pdf, le guide professeur de VB EPS.
Usage : python3 generer-guide-vb-eps.py   (reportlab requis, polices Arial de macOS)

Version lue depuis CLAUDE.md (ligne versionName). Relancer à chaque version.
Le PDF est publié sur outils-eps.fr avec l'APK."""
import os
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, 'vb-eps.pdf')

with open(os.path.join(ICI, 'CLAUDE.md'), encoding='utf-8') as f:
    m = re.search(r'versionName\s*[":]\s*"?([\d.]+)', f.read())
    VERSION = m.group(1) if m else '3.0'

POL = '/System/Library/Fonts/Supplemental/'
pdfmetrics.registerFont(TTFont('F',  POL + 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('FB', POL + 'Arial Bold.ttf'))
pdfmetrics.registerFont(TTFont('FI', POL + 'Arial Italic.ttf'))
pdfmetrics.registerFont(TTFont('FM', POL + 'Courier New Bold.ttf'))
pdfmetrics.registerFontFamily('F', normal='F', bold='FB', italic='FI', boldItalic='FB')

VIOLET    = colors.HexColor('#7c3aed')
VIOLET_BG = colors.HexColor('#f5f3ff')
VERT      = colors.HexColor('#059669')
GRIS      = colors.HexColor('#555555')

corps = ParagraphStyle('corps', fontName='F', fontSize=9.6, leading=13.4, spaceAfter=5,
                       textColor=colors.HexColor('#333333'))
puce  = ParagraphStyle('puce',  parent=corps, leftIndent=14, bulletIndent=3, spaceAfter=3)
titre = ParagraphStyle('titre', fontName='FB', fontSize=24, leading=28,
                       textColor=colors.HexColor('#222222'))
sous  = ParagraphStyle('sous',  fontName='F', fontSize=10.5, leading=14,
                       textColor=GRIS, spaceAfter=4)
h2    = ParagraphStyle('h2', fontName='FB', fontSize=13, leading=16, textColor=VIOLET,
                       spaceBefore=9, spaceAfter=4, keepWithNext=1)
note  = ParagraphStyle('note', parent=corps, fontSize=8.8, leading=12.2)
th    = ParagraphStyle('th', fontName='FB', fontSize=9, leading=12,
                       textColor=colors.white, alignment=1)
td    = ParagraphStyle('td', fontName='F', fontSize=9, leading=12,
                       textColor=colors.HexColor('#222222'), alignment=1)
td_l  = ParagraphStyle('td_l', parent=td, alignment=0)


def P(t, st=corps):
    return Paragraph(t, st)


def B(t):
    return Paragraph(t, puce, bulletText='•')


def en_tete(canvas, doc):
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(VIOLET)
    canvas.rect(0, h - 5 * mm, w, 5 * mm, stroke=0, fill=1)
    canvas.rect(0, 0, w, 5 * mm, stroke=0, fill=1)
    canvas.setFont('F', 8)
    canvas.setFillColor(GRIS)
    canvas.drawRightString(w - 20 * mm, 10 * mm,
                           'Guide professeur - VB EPS - version %s - page %d' % (VERSION, doc.page))
    canvas.restoreState()


def lien_apk():
    t = Table([[Paragraph(
        '<b>Téléchargement de l\'APK</b> (Wi-Fi, <b>avant le cours</b>) :<br/>'
        '<font name="FM" size="8.5">https://github.com/msjeps/VB-EPS/releases/latest/download/VB_EPS.apk</font><br/>'
        'Nom du fichier : <b>VB_EPS.apk</b> — version <b>%s</b>' % VERSION, corps
    )]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), VIOLET_BG),
        ('BOX',           (0, 0), (-1, -1), 1, VIOLET),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def mot_de_passe():
    t = Table([[
        Paragraph('<b>Mot de passe par défaut :</b>', corps),
        Paragraph('<font name="FM" size="14">ADMINPROF</font>', corps),
    ]], colWidths=[62 * mm, 108 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), VIOLET_BG),
        ('BOX',           (0, 0), (-1, -1), 1, VIOLET),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t


def table_bareme(titre_str, lignes):
    """lignes : liste de (geste, points)"""
    data = [[Paragraph(titre_str, th), Paragraph('Points', th)]]
    for geste, pts in lignes:
        data.append([Paragraph(geste, td_l), Paragraph(str(pts), td)])
    t = Table(data, colWidths=[138 * mm, 32 * mm])
    style = [
        ('BACKGROUND',    (0, 0), (-1, 0),  VIOLET),
        ('BACKGROUND',    (0, 1), (-1, -1), VIOLET_BG),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [VIOLET_BG, colors.white]),
        ('BOX',           (0, 0), (-1, -1), 0.5, VIOLET),
        ('INNERGRID',     (0, 0), (-1, -1), 0.3, colors.HexColor('#d8b4fe')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    t.setStyle(TableStyle(style))
    return t


def contenu():
    s = []

    # ---- En-tête ----
    s.append(P('Guide professeur', titre))
    s.append(P('VB EPS : application d\'observation en Volleyball pour l\'EPS (version %s)' % VERSION, sous))
    ligne = Table([['']], colWidths=[170 * mm], rowHeights=[2])
    ligne.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -1), 1.5, VERT)]))
    s += [ligne, Spacer(1, 4)]

    # ---- Présentation ----
    s.append(P('Présentation', h2))
    s.append(P(
        "VB EPS est une application d'observation et d'évaluation en <b>volleyball</b> pour les cours d'EPS "
        "(collège et lycée). Elle permet de noter en temps réel les gestes techniques d'un élève "
        "(service, réception, renvoi ou jeu collectif) avec des barèmes adaptés au niveau, puis d'exporter "
        "les résultats en CSV."
    ))
    s.append(P(
        "L'application fonctionne <b>entièrement hors connexion</b> : aucun accès internet n'est nécessaire "
        "pendant le cours. Les données restent uniquement sur l'appareil utilisé."
    ))

    # ---- Lancement ----
    s.append(P('Lancement', h2))
    s.append(P(
        "VB EPS est une application web (PWA) installable sur tablette ou smartphone, "
        "ou une application Android (APK) :"
    ))
    s.append(B(
        "<b>Tablette ou smartphone Android</b> : ouvrez le lien avec Chrome, puis le menu (les trois points), "
        "puis « Ajouter à l'écran d'accueil »."
    ))
    s.append(B(
        "<b>iPhone / iPad</b> : ouvrez le lien avec Safari (obligatoire), appuyez sur Partager, "
        "puis « Sur l'écran d'accueil »."
    ))
    s.append(B(
        "<b>APK Android</b> : téléchargez le fichier (voir l'encadré ci-dessous) puis ouvrez-le depuis vos "
        "téléchargements (autorisez « Installer des applications inconnues » si demandé). "
        "Une nouvelle APK s'installe par-dessus la précédente sans perdre les données."
    ))
    s.append(lien_apk())
    s.append(P(
        "Une fois lancée, l'application fonctionne sans connexion, avec l'écran maintenu allumé pendant la saisie "
        "et l'affichage en plein écran. Le numéro de version s'affiche dans le pied de page."
    ))

    # ---- Modes d'observation ----
    s.append(P("Modes d'observation", h2))
    s.append(P(
        "Chaque observation porte sur <b>un élève ou une équipe</b>, dans l'un des modes suivants :"
    ))
    s.append(B("<b>Serveur</b> : évalue les services de l'élève, notés de 0 à 4 (barèmes collège/lycée distincts)."))
    s.append(B("<b>Réceptionneur</b> : évalue les réceptions, notées de 0 à 5."))
    s.append(B("<b>Renvoyeur</b> : évalue les renvois, notés de 0 à 5 (barèmes collège/lycée distincts)."))
    s.append(B("<b>Réception + Renvoi</b> : mode combiné, deux blocs séparés dans la même observation."))
    s.append(B(
        "<b>Collectif</b> : évalue un échange collectif (nombre de touches de balle avant renvoi). "
        "Collège : de 0 à 3 pts ; lycée : de 0 à 5 pts."
    ))
    s.append(P(
        "Avant l'observation, choisissez le mode, le niveau (collège ou lycée), et si l'observation est "
        "individuelle ou collective. Un chronomètre configurable (défaut : 5 minutes) est disponible."
    ))

    # ---- Déroulement ----
    s.append(P("Déroulement d'une séance", h2))
    s.append(B("<b>Accueil</b> : saisissez votre nom, la classe et les informations de la séance."))
    s.append(B("<b>Saisie</b> : appuyez sur les boutons de geste pour chaque action observée. "
               "Le schéma terrain permet de localiser la zone de jeu."))
    s.append(B("<b>Résultats</b> : récapitulatif par élève, graphiques des actions, score total calculé."))
    s.append(B("<b>Export</b> : génération du fichier CSV et du QR code récapitulatif."))
    s.append(P(
        "Toutes les saisies sont <b>sauvegardées automatiquement</b> à chaque action et survivent à une "
        "mise en veille, une rotation d'écran ou une sortie accidentelle de l'application. "
        "Les données ne sont effacées que par le bouton « Nouvelle séance »."
    ))

    # ---- Export CSV ----
    s.append(P('Export CSV', h2))
    s.append(P(
        "Les résultats sont exportables en fichier CSV (séparateur <font name='FM'>;</font>, encodage UTF-8 avec BOM "
        "pour Excel français). Le fichier est nommé :"
    ))
    s.append(P('<font name="FM">EPS_Volleyball_[Classe]_[Date].csv</font>'))
    s.append(Spacer(1, 4))
    s.append(P(
        "L'accès professeur permet de choisir les colonnes à inclure dans l'export (via Configuration avancée)."
    ))

    # ---- Accès professeur ----
    s.append(P('Accès professeur : configuration avancée', h2))
    s.append(P(
        "L'icône de réglages (⚙) ouvre les paramètres généraux (thème, vibration) sans mot de passe. "
        "La <b>Configuration professeur</b>, protégée par mot de passe, permet :"
    ))
    s.append(B("Modifier la durée du chronomètre par défaut."))
    s.append(B("Configurer le nombre de joueurs par équipe (2 à 6)."))
    s.append(B("Choisir les colonnes de l'export CSV."))
    s.append(B("Modifier les barèmes de service, réception, renvoi et collectif."))
    s.append(B("Changer le mot de passe professeur."))
    s += [Spacer(1, 4), mot_de_passe(), Spacer(1, 6)]
    s.append(P(
        "<b>Attention</b> : ce mot de passe est distribué uniquement via ce guide pour éviter qu'un élève "
        "ne le trouve sur internet. <font color='#7c3aed'><b>Ne le communiquez pas aux élèves.</b></font> "
        "Il protège uniquement les réglages, pas les données des séances.", note
    ))
    s.append(P(
        "Le mot de passe peut être changé depuis le panneau Configuration professeur (section "
        "« Changer le mot de passe », 6 caractères minimum). Après 5 saisies incorrectes consécutives "
        "sur un mot de passe personnalisé, le mot de passe est réinitialisé au mot de passe initial. "
        "Effacer les données de l'application depuis les paramètres Android rétablit également le mot de "
        "passe initial.", note
    ))
    s.append(Spacer(1, 8))

    # ---- Barèmes ----
    s.append(P('Barèmes par défaut', h2))
    s.append(P("Les barèmes peuvent être modifiés depuis la Configuration professeur."))
    s.append(Spacer(1, 4))

    s.append(table_bareme('Service — Collège', [
        ('Tennis réussi',            4),
        ('Cuillère à 7 m réussie',   3),
        ('Cuillère à 5 m réussie',   2),
        ('Passe haute à 3 m réussie',1),
        ('Raté',                     0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Service — Lycée', [
        ('Tennis tendu et frappé',          4),
        ('Tennis assuré réussi',            3),
        ('Cuillère tendu réussi',           2),
        ('Cuillère haut / hasardeux réussi',1),
        ('Raté',                            0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Réception (collège = lycée)', [
        ('Haute sur passeur',       5),
        ('Haute vers zone avant',   3),
        ('Tendue sur passeur',      2),
        ('Tendue vers zone avant',  1),
        ('Raté',                    0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Renvoi — Collège', [
        ('Frappé en extension réussi', 5),
        ('Placé réussi',               3),
        ('Sans intention réussi',      2),
        ('Dos au filet',               1),
        ('Raté',                       0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Renvoi — Lycée', [
        ('Smasché réussi',          5),
        ('Tendu et placé réussi',   3),
        ('Sur l\'adversaire',       2),
        ('Dos au filet',            1),
        ('Raté',                    0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Collectif — Collège', [
        ('3 touches',   3),
        ('2 touches',   2),
        ('1 touche',    1),
        ('Non renvoyé', 0),
    ]))
    s.append(Spacer(1, 5))
    s.append(table_bareme('Collectif — Lycée', [
        ('Smasché',                       5),
        ('Placé tendu zone arrière',       3),
        ('Placé tendu zone avant',         2),
        ('Haut ou à l\'aveugle',           1),
        ('Non renvoyé',                    0),
    ]))
    s.append(Spacer(1, 10))

    s.append(P(
        "VB EPS, application développée par <b>Nathalie Prenois</b>, professeure EPS (Antibes), "
        "<b>https://outils-eps.fr</b>",
        ParagraphStyle('fin', parent=note, alignment=1, textColor=GRIS)
    ))
    return s


doc = BaseDocTemplate(
    SORTIE, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
    title='Guide professeur - VB EPS',
    author='Nathalie Prenois',
    subject='VB EPS version %s' % VERSION,
)
cadre = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[cadre], onPage=en_tete)])
doc.build(contenu())
print('OK', SORTIE, 'version', VERSION)
