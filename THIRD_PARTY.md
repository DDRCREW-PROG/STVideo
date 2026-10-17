# Composants tiers

ST Vidéo est un projet de David Ascenso. Le code du lecteur 68000 et l'encodeur
sont fournis sous GPL-2.0-or-later ; voir `LICENSE`. Cette licence ne change
pas les droits sur les vidéos utilisées ou produites par l'utilisateur.

| Composant | Usage | Licence / source |
| --- | --- | --- |
| Table YM de Paulo Simoes, copyright 2012 | Niveaux mesurés des 4096 combinaisons YM | Distribuée avec [Hatari](https://github.com/hatari/hatari), GPL-2.0-or-later ; en-tête conservé dans `data/ym2149_fixed_vol.h` |
| Python | Runtime de la version Windows | PSF ; https://www.python.org/psf/license/ |
| Tcl/Tk | Interface graphique | Licences Tcl/Tk ; https://www.tcl.tk/software/tcltk/license.html |
| NumPy | Traitement numérique | BSD-3-Clause ; https://numpy.org/ |
| Pillow | Images | HPND et notices associées ; https://python-pillow.org/ |
| imageio-ffmpeg | Exécutable FFmpeg et accès Python | BSD-2-Clause pour le paquet ; https://github.com/imageio/imageio-ffmpeg |
| FFmpeg | Décodage, filtrage, rééchantillonnage | Conditions propres au binaire embarqué et à ses bibliothèques ; https://ffmpeg.org/legal.html |
| yt-dlp | URL vidéo | Unlicense pour le code principal, notices de ses dépendances ; https://github.com/yt-dlp/yt-dlp |
| PyInstaller | Construction de l'exécutable | GPL avec exception de distribution des applications ; https://pyinstaller.org/ |
| Inno Setup | Construction de l'installateur | Licence Inno Setup ; https://jrsoftware.org/ |

Les notices présentes dans les paquets Python sont copiées dans les
ressources de l'application pendant la construction. Le manifeste de build
indique les versions et la configuration du FFmpeg embarqué. Les binaires
FFmpeg tiers doivent être redistribués avec leurs notices et les informations
d'accès aux sources correspondantes ; voir `docs/BUILD-WINDOWS.md`.

vasm sert uniquement à recompiler le lecteur. Il n'est pas embarqué dans
l'application ni dans les sources préparées pour GitHub. Son utilisation
reste soumise à sa propre licence : http://sun.hasenbraten.de/vasm/.

LAVP2, LAVMOD, STEAV, Hatari, les ROM TOS et les clips de test de David Ascenso
ne sont pas inclus dans les distributions de ST Vidéo. L'export STEAV2
est une fonction d'interopérabilité ; aucun code de ces lecteurs n'est
nécessaire au fonctionnement de STFPLAY.
