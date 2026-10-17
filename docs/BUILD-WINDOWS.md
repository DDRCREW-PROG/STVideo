# Construire et distribuer ST Vidéo

Environnement de référence : Windows x64, Python 3.12 x64 avec Tkinter,
PyInstaller 6.22.3. Python, NumPy, Pillow, FFmpeg et yt-dlp sont embarqués
dans l'exécutable ; les destinataires n'ont pas besoin de les installer.

1. Extraire les sources et créer un environnement avec `python -m venv .venv`.
2. Installer `requirements-build.txt` avec le pip de cet environnement.
3. Lancer `python -m unittest discover -s tools -p "test_*.py"`.
4. Vérifier que `player/STFPLAY.PRG` est présent ; son source est `src/player.s`.
5. Lancer `python tools/build_windows.py` pour l'exécutable et les ZIP.
6. Pour l'installateur, ajouter `--inno "chemin/vers/ISCC.exe"`.

Exécuter ces commandes avec le Python de `.venv`. La première construction
demande Internet pour les dépendances ; l'encodage d'une vidéo locale par
l'application construite fonctionne hors ligne.

## Artefacts

`dist/frozen/STVideo.exe` est autonome. `dist/portable-<version>` contient l'exécutable,
le guide, les notices et une archive du source de cette version. Le ZIP
portable et le Setup sont produits dans `dist`, avec `SHA256SUMS.txt`.

L'installateur place les fichiers dans le dossier de programmes de
l'utilisateur courant, sans demande d'élévation, et crée un raccourci dans
le menu Démarrer. Le raccourci Bureau est facultatif. Les clips sont écrits
dans le dossier de sortie choisi et ne sont pas supprimés par la désinstallation.
Les exécutables ne sont pas signés avec un certificat d'éditeur.

Le packager n'inclut que des fichiers explicitement sélectionnés. Les dossiers
`build`, `vendor`, les disassemblages de programmes historiques, les clips
personnels, les ROM et les émulateurs sont exclus de l'archive source.
Les dépendances binaires redistribuées par le portable restent dans l'exécutable.

## Ressources et processus d'encodage

En source, les ressources sont lues dans le projet ; dans l'EXE, elles sont
intégrées à l'archive PyInstaller. `app_runtime.py` centralise ces chemins.
Le GUI lance le même exécutable avec `--encode --log-file <journal>` pour
traiter la vidéo en arrière-plan. Un journal UTF-8 explicite permet de
suivre la progression même sans console Windows.

## Dépendances et provenance

`build/notices/BUILD-MANIFEST.json` enregistre Python, les versions des paquets
et les SHA-256 de FFmpeg et du lecteur. Les licences présentes dans les
paquets sont copiées dans les notices, ainsi que `FFmpeg-version.txt`.
Le binaire FFmpeg fourni par imageio-ffmpeg peut être sous GPLv3 selon sa
configuration ; le manifeste et sa provenance doivent accompagner chaque
release. Les sources correspondantes et celles des bibliothèques embarquées
sont à rendre disponibles selon leurs licences. Les liens du fournisseur
sont dans `FFmpeg-sources.txt` ; vérifier leur correspondance avec la version
effectivement redistribuée avant une publication publique.

Les dépendances peuvent évoluer : relancer les tests et examiner le manifeste
après une mise à jour. Les tests locaux ne prouvent pas le débit ACSI réel.

## Construire le lecteur

Télécharger vasm séparément selon sa licence, puis :

```powershell
powershell -File tools/build.ps1 -Assembler "C:\outils\vasmm68k_mot.exe"
```

Le script met à jour `player/STFPLAY.PRG` et sa copie de développement dans
`build/hdd`. Le binaire Atari ne demande pas de compilateur sur le PC du
destinataire. Le guide d'utilisation ne nécessite pas Hatari ; pour les
essais d'émulation, fournir son propre émulateur et sa ROM autorisée.
