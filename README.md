# ST Vidéo — Encodeur vidéo PC vers Atari ST

L'idée est simple : prendre une vidéo sur le PC, la convertir, puis la regarder
sur un Atari ST avec le son. C'est ce que permet ST Vidéo.

Je suis **David Ascenso**. J'avais déjà réalisé mon encodeur et mon lecteur
vidéo pour Atari. J'ai voulu rendre l'ensemble plus simple à utiliser et
améliorer l'image et le son, tout en restant sur un ST à **8 MHz**.

L'encodeur fonctionne sous **Windows 10 et 11, en français et en anglais**.
Il prépare la vidéo en **320 × 200 et 16 couleurs**, puis crée un fichier
à copier sur l'Atari. Le lecteur **STFPLAY.PRG** est fourni avec le programme.
Le tout fonctionne sur **ST, STF et STE, à partir de 512 Ko de RAM**, en PAL.

**[Télécharger l'installateur ou la version portable](https://github.com/DDRCREW-PROG/STVideo/releases/latest)** · [Read in English](README.en.md)

## Ce que ça donne sur mon STF

J'ai testé le lecteur sur mon **Atari STF avec 1 Mo de RAM**, équipé d'un
**disque ACSI sur carte SD**. Le programme fonctionne aussi avec **512 Ko**.

À **12,5 images par seconde**, ça tourne bien et le résultat est étonnamment
fluide. À **25 images par seconde**, la lecture ralentit sur mon installation :
le stockage n'arrive pas à suivre. C'est donc le mode 12,5 images/s que je
conseille pour commencer sur STF.

Le film garde sa vitesse normale : il dure aussi longtemps que l'original.
On affiche simplement moins d'images par seconde.

Pour donner un ordre d'idée, le fichier demande environ **410 ko/s à
12,5 images/s**, contre **819 ko/s à 25 images/s**. Même avec un stockage
annoncé à 800–900 ko/s, les temps d'accès et le pilote peuvent faire la différence.
Les essais sous Hatari ont aussi été réalisés à 8 MHz avec 512 Ko, mais un
émulateur ne permet pas de juger le débit d'un vrai disque ACSI.

## Installer et essayer

Sur la [page des téléchargements](https://github.com/DDRCREW-PROG/STVideo/releases/latest), vous avez le choix :

- **Setup.exe** : l'installateur Windows, avec un raccourci et une désinstallation classique.
- **Windows-portable.zip** : décompressez le dossier, puis lancez **STVideo.exe**.
- **sources.zip** : les sources pour ceux qui veulent regarder comment ça marche ou les modifier.

Vous n'avez pas besoin d'installer Python ou FFmpeg : ils sont inclus.
Le choix **Langue / Language** en haut de la fenêtre permet de passer du
français à l'anglais. Le programme mémorise votre choix.

1. Choisissez une vidéo sur votre PC. Vous pouvez aussi essayer une URL vidéo ; sa prise en charge dépend du site.
2. Cliquez sur **Réglages STF / ACSI conseillés** si vous utilisez un STF.
3. Choisissez le dossier de sortie et donnez un nom court au clip : **1 à 8 caractères** pour l'Atari.
4. Cliquez sur **Essayer sur 5 secondes** pour vérifier le rendu avant de lancer toute la vidéo.
5. Encodez, puis copiez **<NOM>.STV** et **STFPLAY.PRG** sur le disque de l'Atari.
6. Lancez **STFPLAY.PRG**, en basse résolution couleur sur un Atari PAL.

Les essais de cinq secondes sont rangés dans le sous-dossier **APERCU**.
Si le nom choisi existe déjà, l'encodeur ajoute un numéro : vos anciens
fichiers sont conservés.

## Les réglages que je conseille

Pour un STF, commencez avec **12,5 images/s**, **Trame fixe (stable)**,
**Palette ST optimisée** et **Réglage audio optimisé pour STF (plus lent)**.
Le bouton des réglages conseillés fait cela pour vous.

Le mot « plus lent » concerne le temps de préparation sur le PC.
La vidéo ne sera pas lue au ralenti sur l'Atari.

La palette optimisée choisit les 16 couleurs les mieux adaptées à l'image
parmi les **512 couleurs du ST**. Le tramage ajoute de petits motifs pour
rendre les dégradés plus agréables. La **trame fixe** est un bon point de
départ ; pour les dessins animés, les textes et les aplats, essayez aussi
**Sans dithering**. Comparez les réglages sur un petit extrait : selon la
vidéo, le résultat peut être assez différent.

**Plus nette** peut aider à retrouver du détail. **Très nette** accentue
davantage l'image, mais peut créer des contours trop marqués. Le nettoyage
vidéo atténue le grain ; s'il efface des détails, réduisez-le ou désactivez-le.

## Pour le son : STF ou STE ?

Sur **STF**, choisissez l'**audio optimisé pour STF**. Le PC prépare le son
pour le circuit YM2149 de l'Atari. Cela réduit une partie du grésillement,
mais le son reste moins propre que sur un STE.

Sur **STE**, choisissez l'**audio optimisé pour STE** pour profiter de sa
sortie audio DMA, de meilleure qualité. Un fichier préparé en mode STF
reste en mode YM même sur un STE : pour profiter du son DMA, réencodez-le
avec le réglage STE.

Commencez avec le nettoyage audio **Léger**. Le mode **Renforcé** peut aider
sur une source bruyante, mais aussi enlever des aigus. L'option de renforcement
des sources faibles remonte le volume, avec un gain limité à environ +12 dB.
Le mode **YM léger** est expérimental ; je conseille le mode STF optimisé
pour une utilisation normale.

Le STE a toujours besoin d'un disque assez rapide. Vous pouvez donc choisir
12,5 images/s avec l'audio STE si votre stockage peine à suivre à 25 images/s.

## Pendant la lecture sur Atari

- **Shift droit** : arrêter la vidéo et ouvrir le sélecteur pour en choisir une autre.
- **Échap** : quitter le lecteur. Annuler le sélecteur quitte aussi.

Le lecteur ouvre **VIDEO.STV** s'il le trouve ; sinon, il vous propose de
choisir un fichier. Le son est déjà inclus dans le **STV** : pour lire sur
l'Atari, seuls ce fichier et **STFPLAY.PRG** sont nécessaires.

## Où sont les fichiers, et quelle place prennent-ils ?

Tout est enregistré dans le dossier choisi dans l'encodeur. Par défaut,
il s'agit de **Vidéos/STVideo** dans votre profil Windows.

Le fichier **<NOM>.STV** est celui à lire avec STFPLAY. L'encodeur produit
aussi un export **LAV**, un fichier audio **WAV**, des aperçus et un rapport
**JSON** avec les réglages utilisés. L'export LAV reste à **25 images/s**,
même si vous avez choisi 12,5 images/s pour le STV.

Comptez environ **24,6 Mo par minute à 12,5 images/s** et **49,2 Mo par minute
à 25 images/s** pour le STV. Avec les autres fichiers, le dossier complet
prend davantage de place. Pour un long film, utilisez **Début** et **Durée**
pour faire plusieurs parties avant d'atteindre la limite de fichier de 2 Gio.
Le lecteur n'enchaîne pas encore les parties automatiquement.

Si une URL ne fonctionne pas, essayez une vidéo déjà présente sur votre PC.
La conversion d'un fichier local fonctionne sans connexion Internet.

## Pour ceux qui veulent aller plus loin

Le lecteur est écrit en **assembleur 68000** et l'encodeur en **Python**, avec
FFmpeg pour préparer la vidéo et le son. Le PC fait les gros calculs :
l'Atari lit des images et un son déjà préparés pour lui.

- [Guide STF](docs/GUIDE-STF.txt), également disponible dans l'application.
- [Comment construire la version Windows](docs/BUILD-WINDOWS.md).
- [Description du format STV](docs/FORMAT-STV.md).
- [Détails des essais et des mesures](docs/VALIDATION.md).

Avec Python 3.12 x64 sous Windows :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe tools\app.py
.venv\Scripts\python.exe -m unittest discover -s tools -p "test_*.py"
.venv\Scripts\python.exe tools\build_windows.py --inno "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
```

Le lecteur compilé se trouve dans `player/STFPLAY.PRG` et son source dans
`src/player.s`. Pour le reconstruire avec vasm :

```powershell
powershell -File tools\build.ps1 -Assembler "C:\outils\vasmm68k_mot.exe"
```

Le modèle `packaging/github-actions-windows.yml` est fourni pour ceux qui
souhaitent configurer une construction Windows dans GitHub Actions.
Il faut l'installer dans `.github/workflows/` pour l'activer.

## Crédits

**David Ascenso — ST Vidéo.** Sources sous GPL-2.0-or-later : voir
[LICENSE](LICENSE) et [les composants tiers](THIRD_PARTY.md).
Merci à Paulo Simoes pour la table de niveaux YM distribuée avec Hatari.
Les vidéos personnelles, émulateurs, ROM TOS et anciens lecteurs LAV ne sont
pas fournis. La licence du programme ne change pas les droits sur vos vidéos.
