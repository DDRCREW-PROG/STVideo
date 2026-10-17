# ST VidÃ©o

Encodeur Windows et lecteur Atari ST / STF / STE : **320 Ã— 200, 16 couleurs
parmi les 512 du ST, son mono et lecture PAL Ã  12,5 ou 25 images/s**.

Projet de **David Ascenso**, dÃ©veloppÃ© Ã  partir de son encodeur, de son lecteur
et de ses premiers essais de vidÃ©o sur Atari. Cette version ajoute une
interface, des palettes optimisÃ©es, le traitement audio et la restitution
YM anticipÃ©e sur STF. Le lecteur fourni, `STFPLAY.PRG`, est Ã©crit en
assembleur 68000 ; l'encodeur est Ã©crit en Python et utilise FFmpeg.

## RÃ©sultat sur un vrai STF

David Ascenso a testÃ© la lecture sur **STF avec disque ACSI sur carte SD** :

| RÃ©glage STV | DÃ©bit du fichier | RÃ©sultat rapportÃ© |
| --- | --- | --- |
| 12,5 images/s | 409 600 octets/s, environ 410 ko/s | Lecture fonctionnelle, rÃ©sultat jugÃ© fluide |
| 25 images/s | 819 200 octets/s, environ 819 ko/s | Ralentissements sur ce stockage |

Ce constat concerne cette machine et ce stockage. Un dÃ©bit annoncÃ© Ã 
800â€“900 ko/s laisse peu de marge Ã  25 images/s : les pauses de lecture,
le pilote et le systÃ¨me de fichiers comptent aussi. **Commencez Ã  12,5
images/s sur STF.** La quantitÃ© de RAM de l'essai physique n'a pas Ã©tÃ©
consignÃ©e ; les essais d'Ã©mulation ont notamment utilisÃ© 512 Ko et 8 MHz.
Hatari avec un dossier Windows ne mesure pas les performances ACSI rÃ©elles.

Télécharger la version Windows : [installateur et version portable](https://github.com/DDRCREW-PROG/STVideo/releases/latest).

[English documentation](README.en.md)

## Installer sous Windows

Les distributions Ã  construire avec ce dÃ©pÃ´t sont :

- **STVideo-1.0.1-Setup.exe** : installateur Windows 10/11 x64, pour
  l'utilisateur courant, avec raccourci dans le menu DÃ©marrer et dÃ©sinstallation.
- **STVideo-1.0.1-Windows-portable.zip** : extraire tout le dossier puis
  lancer **STVideo.exe**. Pas besoin d'installer Python ni FFmpeg.
- **STVideo-1.0.1-sources.zip** : sources de l'application et du lecteur,
  dÃ©pendances et instructions de reconstruction.

L'application est en franÃ§ais. Les clips personnels, Ã©mulateurs et ROM TOS
ne sont pas fournis. Les fichiers de sortie sont crÃ©Ã©s dans le dossier choisi
dans l'interface ; par dÃ©faut, `VidÃ©os/STVideo` dans le profil Windows.

## Tutoriel STF : rÃ©glages conseillÃ©s

1. Choisir la vidÃ©o locale ou une URL prise en charge par yt-dlp.
2. Cliquer sur **RÃ©glages STF / ACSI conseillÃ©s**. Ce profil sÃ©lectionne
   **12,5 images/s**, **Trame fixe (stable)**, **Palette ST optimisÃ©e** et
   **RÃ©glage audio optimisÃ© pour STF (plus lent)**.
3. Choisir le dossier de sortie et un nom Atari de 1 Ã  8 caractÃ¨res.
   Indiquer Ã©ventuellement un dÃ©but et une durÃ©e en secondes.
4. Cliquer sur **Essayer sur 5 secondes**. L'essai est placÃ© dans `APERCU`.
   Examiner l'aperÃ§u puis tester ce STV sur la machine rÃ©elle.
5. Encoder le clip complet, puis copier **<NOM>.STV** et **STFPLAY.PRG**
   sur le stockage Atari. Lancer le lecteur en basse rÃ©solution couleur PAL.

Le guide complet est accessible dans l'onglet **Guide STF** de l'application
et dans [docs/GUIDE-STF.txt](docs/GUIDE-STF.txt).

Ã€ 12,5 images/s, le film conserve sa durÃ©e : l'Ã©cran est renouvelÃ© toutes
les quatre VBL PAL au lieu de deux. La fluiditÃ© dÃ©pend du mouvement du clip.
L'audio STV est prÃ©parÃ© Ã  **8 192 Hz** Ã  12,5 images/s, et **12 288 Hz** Ã 
25 images/s. Le rÃ©glage Â« plus lent Â» de l'audio STF dÃ©signe le **temps
d'encodage sur PC**, pas une lecture ralentie sur Atari.

## Lecture sur Atari

`STFPLAY.PRG` ouvre `VIDEO.STV` s'il existe ; sinon, il affiche un sÃ©lecteur.
**Shift droit** pendant la lecture arrÃªte le clip et ouvre le sÃ©lecteur pour
un autre STV. **Ã‰chap** quitte ; annuler le sÃ©lecteur quitte Ã©galement.
Le son est inclus dans le STV : les WAV et le LAV ne sont pas nÃ©cessaires.
Toujours conserver le lecteur rÃ©cent avec les clips, surtout au format STV3.

## Couleurs et tramage

**Palette ST optimisÃ©e** cherche 16 couleurs distinctes dans la grille
matÃ©rielle de 512 couleurs, avec un critÃ¨re CIELAB pondÃ©rÃ©. Le choix n'est
pas une garantie d'optimum global. Les coupures de plan peuvent rÃ©initialiser
la palette. La mÃ©thode **Palette classique rapide** reste disponible.

- **Trame fixe (stable)** : motif ordonnÃ© fixe ; rÃ©glage conseillÃ© pour
  commencer en vidÃ©o sur STF. Le motif est fixe, pas nÃ©cessairement la palette.
- **Trame adaptative** : mÃ©langes de couleurs selon l'image, motif fixe
  et intensitÃ© rÃ©glable ; Ã  comparer sur les dÃ©gradÃ©s.
- **Sans dithering** : utile pour dessins animÃ©s, textes et aplats.
- **Diffusion Floyd** : autre rendu possible, qui peut scintiller en vidÃ©o.

La nettetÃ© agit avant la rÃ©duction des couleurs. **Plus nette** peut aider,
**TrÃ¨s nette** peut ajouter des halos. Le nettoyage vidÃ©o attÃ©nue le grain
mais peut effacer des dÃ©tails. Ces traitements se font sur le PC : ils ne
modifient pas le dÃ©bit du fichier ni le nombre de couleurs du ST.

## Quel rÃ©glage audio choisir ?

| Mode | Fichier | Sur STF | Sur STE |
| --- | --- | --- | --- |
| RÃ©glage audio optimisÃ© pour STF (plus lent) | STV3 | YM anticipÃ©, lecture continue | MÃªme sortie YM ; pas de DMA |
| Audio optimisÃ© pour STE | STV1 | Restitution YM classique | DÃ©tection du STE et sortie DMA |
| YM lÃ©ger (expÃ©rimental) | STV2 | Une Ã©criture YM par Ã©chantillon, recalage par image | MÃªme sortie YM |

Le STF n'a pas le DAC audio DMA du STE. Le mode STF prÃ©calcule sur le PC une
suite de changements des volumes du YM2149, puis les enchaÃ®ne sans abandonner
systÃ©matiquement la fin de chaque trame audio. Certains parasites diminuent,
mais le rÃ©sultat reste moins propre que le DMA du STE. **Un STV3 lu sur STE
ne retrouve pas le son DMA : il faut rÃ©encoder en mode STE pour cela.**

Le nettoyage audio LÃ©ger, RenforcÃ© ou Voix filtre la source. RenforcÃ© peut
retirer des aigus : commencer par LÃ©ger. Le renforcement des sources faibles
limite le gain Ã  environ +12 dB. Ces options ne suppriment pas tous les bruits
du circuit analogique ou les retards d'interruptions.

Le profil STE propose 25 images/s et l'audio DMA. Le stockage doit toujours
suivre : le STE ne rÃ©sout pas un dÃ©bit disque insuffisant. On peut aussi
choisir 12,5 images/s avec l'audio STE.

## Fichiers produits et tailles

Un nom dÃ©jÃ  prÃ©sent reÃ§oit un numÃ©ro automatiquement : `VIDEO.STV`,
`VIDEO001.STV`, etc. Les sorties existantes ne sont pas Ã©crasÃ©es.
Le journal affiche le nom retenu. Les fichiers associÃ©s portent ce prÃ©fixe :

- `<NOM>.STV` : fichier Ã  jouer avec STFPLAY, son inclus.
- `<NOM>.LAV` : export STEAV2 historique ; il reste Ã  **25 images/s**, mÃªme
  si le STV est en 12,5 images/s. Il vise les lecteurs LAV compatibles.
- `<NOM>-AUDIO<frÃ©quence>.WAV` : audio PCM mono sÃ©parÃ© pour comparaison.
- `<NOM>-PREVIEW.png`, `-PREVIEW.gif`, `-COMPARAISON.png` : aperÃ§us.
- `<NOM>-REPORT.json` : paramÃ¨tres, cadence et dÃ©bit du STV.
- `STFPLAY.PRG` : lecteur commun, copiÃ© dans le dossier de sortie.

Le STV occupe environ **24,6 Mo/minute** Ã  12,5 images/s, **49,2 Mo/minute**
Ã  25 images/s, plus un en-tÃªte de 32 Kio. Le dossier complet est plus gros,
car le LAV et les aperÃ§us sont aussi produits. La limite de fichier TOS de
2 Gio impose de dÃ©couper les longs contenus avec DÃ©but/DurÃ©e ; l'enchaÃ®nement
automatique de plusieurs parties n'est pas implÃ©mentÃ©.

Une URL nÃ©cessite Internet et dÃ©pend des sites, de leurs accÃ¨s et du support
de yt-dlp. Le fonctionnement des fichiers locaux ne dÃ©pend pas d'Internet.
Si une URL Ã©choue, utiliser un fichier local. L'application ne contourne pas
les restrictions d'accÃ¨s Ã  un contenu.

## DÃ©velopper et reconstruire

Avec Python 3.12 x64 sous Windows :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe tools\app.py
.venv\Scripts\python.exe -m unittest discover -s tools -p "test_*.py"
.venv\Scripts\python.exe tools\build_windows.py --inno "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Le lecteur prÃ©compilÃ© est dans `player/STFPLAY.PRG`, avec son source dans
`src/player.s`. Pour le reconstruire avec vasm :

```powershell
powershell -File tools\build.ps1 -Assembler "C:\outils\vasmm68k_mot.exe"
```

Le mode ligne de commande garde tous les rÃ©glages accessibles :

```powershell
.venv\Scripts\python.exe tools\encode.py clip.mp4 -o sorties --stf-fps 12.5 --dither ordered --quality perceptual --audio-codec optimal
```

Voir [la construction Windows](docs/BUILD-WINDOWS.md),
[le format STV](docs/FORMAT-STV.md) et [les validations](docs/VALIDATION.md).
Le modèle `packaging/github-actions-windows.yml` peut construire les distributions Windows une fois installé dans `.github/workflows/` par le propriétaire du dépôt ; les clips
personnels, chemins de dÃ©veloppement et outils propriÃ©taires sont exclus
de l'archive source prÃ©parÃ©e. Rien n'est publiÃ© automatiquement sur GitHub.

## Licence et crÃ©dits

GPL-2.0-or-later ; voir [LICENSE](LICENSE) et [THIRD_PARTY.md](THIRD_PARTY.md).
La table de niveaux YM mesurÃ©e par Paulo Simoes est distribuÃ©e avec Hatari.
Les mÃ©dias de l'utilisateur ne sont pas placÃ©s sous cette licence.
Les logiciels LAV historiques et les ROM TOS ne sont pas redistribuÃ©s.
