# ST Vidéo

Encodeur Windows et lecteur Atari ST / STF / STE : **320 × 200, 16 couleurs
parmi les 512 du ST, son mono et lecture PAL à 12,5 ou 25 images/s**.

Projet de **David Ascenso**, développé à partir de son encodeur, de son lecteur
et de ses premiers essais de vidéo sur Atari. Cette version ajoute une
interface, des palettes optimisées, le traitement audio et la restitution
YM anticipée sur STF. Le lecteur fourni, `STFPLAY.PRG`, est écrit en
assembleur 68000 ; l'encodeur est écrit en Python et utilise FFmpeg.

## Résultat sur un vrai STF

David Ascenso a testé la lecture sur **STF avec disque ACSI sur carte SD** :

| Réglage STV | Débit du fichier | Résultat rapporté |
| --- | --- | --- |
| 12,5 images/s | 409 600 octets/s, environ 410 ko/s | Lecture fonctionnelle, résultat jugé fluide |
| 25 images/s | 819 200 octets/s, environ 819 ko/s | Ralentissements sur ce stockage |

Ce constat concerne cette machine et ce stockage. Un débit annoncé à
800–900 ko/s laisse peu de marge à 25 images/s : les pauses de lecture,
le pilote et le système de fichiers comptent aussi. **Commencez à 12,5
images/s sur STF.** La quantité de RAM de l'essai physique n'a pas été
consignée ; les essais d'émulation ont notamment utilisé 512 Ko et 8 MHz.
Hatari avec un dossier Windows ne mesure pas les performances ACSI réelles.

Télécharger la version Windows : [installateur et version portable](https://github.com/DDRCREW-PROG/STVideo/releases/latest).

[English documentation](README.en.md)

## Installer sous Windows

Les distributions disponibles sont :

- **STVideo-1.0.1-Setup.exe** : installateur Windows 10/11 x64, pour
  l'utilisateur courant, avec raccourci dans le menu Démarrer et désinstallation.
- **STVideo-1.0.1-Windows-portable.zip** : extraire tout le dossier puis
  lancer **STVideo.exe**. Pas besoin d'installer Python ni FFmpeg.
- **STVideo-1.0.1-sources.zip** : sources de l'application et du lecteur,
  dépendances et instructions de reconstruction.

L'application propose le français et l'anglais (sélecteur Langue / Language). Les clips personnels, émulateurs et ROM TOS
ne sont pas fournis. Les fichiers de sortie sont créés dans le dossier choisi
dans l'interface ; par défaut, `Vidéos/STVideo` dans le profil Windows.

## Tutoriel STF : réglages conseillés

1. Choisir la vidéo locale ou une URL prise en charge par yt-dlp.
2. Cliquer sur **Réglages STF / ACSI conseillés**. Ce profil sélectionne
   **12,5 images/s**, **Trame fixe (stable)**, **Palette ST optimisée** et
   **Réglage audio optimisé pour STF (plus lent)**.
3. Choisir le dossier de sortie et un nom Atari de 1 à 8 caractères.
   Indiquer éventuellement un début et une durée en secondes.
4. Cliquer sur **Essayer sur 5 secondes**. L'essai est placé dans `APERCU`.
   Examiner l'aperçu puis tester ce STV sur la machine réelle.
5. Encoder le clip complet, puis copier **<NOM>.STV** et **STFPLAY.PRG**
   sur le stockage Atari. Lancer le lecteur en basse résolution couleur PAL.

Le guide complet est accessible dans l'onglet **Guide STF** de l'application
et dans [docs/GUIDE-STF.txt](docs/GUIDE-STF.txt).

À 12,5 images/s, le film conserve sa durée : l'écran est renouvelé toutes
les quatre VBL PAL au lieu de deux. La fluidité dépend du mouvement du clip.
L'audio STV est préparé à **8 192 Hz** à 12,5 images/s, et **12 288 Hz** à
25 images/s. Le réglage « plus lent » de l'audio STF désigne le **temps
d'encodage sur PC**, pas une lecture ralentie sur Atari.

## Lecture sur Atari

`STFPLAY.PRG` ouvre `VIDEO.STV` s'il existe ; sinon, il affiche un sélecteur.
**Shift droit** pendant la lecture arrête le clip et ouvre le sélecteur pour
un autre STV. **Échap** quitte ; annuler le sélecteur quitte également.
Le son est inclus dans le STV : les WAV et le LAV ne sont pas nécessaires.
Toujours conserver le lecteur récent avec les clips, surtout au format STV3.

## Couleurs et tramage

**Palette ST optimisée** cherche 16 couleurs distinctes dans la grille
matérielle de 512 couleurs, avec un critère CIELAB pondéré. Le choix n'est
pas une garantie d'optimum global. Les coupures de plan peuvent réinitialiser
la palette. La méthode **Palette classique rapide** reste disponible.

- **Trame fixe (stable)** : motif ordonné fixe ; réglage conseillé pour
  commencer en vidéo sur STF. Le motif est fixe, pas nécessairement la palette.
- **Trame adaptative** : mélanges de couleurs selon l'image, motif fixe
  et intensité réglable ; à comparer sur les dégradés.
- **Sans dithering** : utile pour dessins animés, textes et aplats.
- **Diffusion Floyd** : autre rendu possible, qui peut scintiller en vidéo.

La netteté agit avant la réduction des couleurs. **Plus nette** peut aider,
**Très nette** peut ajouter des halos. Le nettoyage vidéo atténue le grain
mais peut effacer des détails. Ces traitements se font sur le PC : ils ne
modifient pas le débit du fichier ni le nombre de couleurs du ST.

## Quel réglage audio choisir ?

| Mode | Fichier | Sur STF | Sur STE |
| --- | --- | --- | --- |
| Réglage audio optimisé pour STF (plus lent) | STV3 | YM anticipé, lecture continue | Même sortie YM ; pas de DMA |
| Audio optimisé pour STE | STV1 | Restitution YM classique | Détection du STE et sortie DMA |
| YM léger (expérimental) | STV2 | Une écriture YM par échantillon, recalage par image | Même sortie YM |

Le STF n'a pas le DAC audio DMA du STE. Le mode STF précalcule sur le PC une
suite de changements des volumes du YM2149, puis les enchaîne sans abandonner
systématiquement la fin de chaque trame audio. Certains parasites diminuent,
mais le résultat reste moins propre que le DMA du STE. **Un STV3 lu sur STE
ne retrouve pas le son DMA : il faut réencoder en mode STE pour cela.**

Le nettoyage audio Léger, Renforcé ou Voix filtre la source. Renforcé peut
retirer des aigus : commencer par Léger. Le renforcement des sources faibles
limite le gain à environ +12 dB. Ces options ne suppriment pas tous les bruits
du circuit analogique ou les retards d'interruptions.

Le profil STE propose 25 images/s et l'audio DMA. Le stockage doit toujours
suivre : le STE ne résout pas un débit disque insuffisant. On peut aussi
choisir 12,5 images/s avec l'audio STE.

## Fichiers produits et tailles

Un nom déjà présent reçoit un numéro automatiquement : `VIDEO.STV`,
`VIDEO001.STV`, etc. Les sorties existantes ne sont pas écrasées.
Le journal affiche le nom retenu. Les fichiers associés portent ce préfixe :

- `<NOM>.STV` : fichier à jouer avec STFPLAY, son inclus.
- `<NOM>.LAV` : export STEAV2 historique ; il reste à **25 images/s**, même
  si le STV est en 12,5 images/s. Il vise les lecteurs LAV compatibles.
- `<NOM>-AUDIO<fréquence>.WAV` : audio PCM mono séparé pour comparaison.
- `<NOM>-PREVIEW.png`, `-PREVIEW.gif`, `-COMPARAISON.png` : aperçus.
- `<NOM>-REPORT.json` : paramètres, cadence et débit du STV.
- `STFPLAY.PRG` : lecteur commun, copié dans le dossier de sortie.

Le STV occupe environ **24,6 Mo/minute** à 12,5 images/s, **49,2 Mo/minute**
à 25 images/s, plus un en-tête de 32 Kio. Le dossier complet est plus gros,
car le LAV et les aperçus sont aussi produits. La limite de fichier TOS de
2 Gio impose de découper les longs contenus avec Début/Durée ; l'enchaînement
automatique de plusieurs parties n'est pas implémenté.

Une URL nécessite Internet et dépend des sites, de leurs accès et du support
de yt-dlp. Le fonctionnement des fichiers locaux ne dépend pas d'Internet.
Si une URL échoue, utiliser un fichier local. L'application ne contourne pas
les restrictions d'accès à un contenu.

## Développer et reconstruire

Avec Python 3.12 x64 sous Windows :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe tools\app.py
.venv\Scripts\python.exe -m unittest discover -s tools -p "test_*.py"
.venv\Scripts\python.exe tools\build_windows.py --inno "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Le lecteur précompilé est dans `player/STFPLAY.PRG`, avec son source dans
`src/player.s`. Pour le reconstruire avec vasm :

```powershell
powershell -File tools\build.ps1 -Assembler "C:\outils\vasmm68k_mot.exe"
```

Le mode ligne de commande garde tous les réglages accessibles :

```powershell
.venv\Scripts\python.exe tools\encode.py clip.mp4 -o sorties --stf-fps 12.5 --dither ordered --quality perceptual --audio-codec optimal
```

Voir [la construction Windows](docs/BUILD-WINDOWS.md),
[le format STV](docs/FORMAT-STV.md) et [les validations](docs/VALIDATION.md).
Le modèle `packaging/github-actions-windows.yml` peut construire les distributions Windows une fois installé dans `.github/workflows/` par le propriétaire du dépôt ; les clips
personnels, chemins de développement et outils propriétaires sont exclus
de l'archive source préparée. Rien n'est publié automatiquement sur GitHub.

## Licence et crédits

GPL-2.0-or-later ; voir [LICENSE](LICENSE) et [THIRD_PARTY.md](THIRD_PARTY.md).
La table de niveaux YM mesurée par Paulo Simoes est distribuée avec Hatari.
Les médias de l'utilisateur ne sont pas placés sous cette licence.
Les logiciels LAV historiques et les ROM TOS ne sont pas redistribués.
