# Validation et limites

## Matériel réel

Retour de David Ascenso : STF avec stockage ACSI sur carte SD. À 25 images/s,
la lecture ralentit ; à 12,5 images/s, elle fonctionne bien, avec une fluidité
jugée satisfaisante. Le débit annoncé du stockage est de 800 à 900 ko/s.
La RAM exacte, le modèle d'interface et le pilote n'ont pas été consignés.
Ce n'est donc pas une certification de toutes les configurations STF.

## Émulation

Hatari, 68000 à 8 MHz, 512 Ko, PAL :

- 200 images à 25 images/s retrouvées à l'identique dans la capture STV3.
- 98 304 commandes audio restituées sans abandon sur l'extrait de 8 secondes.
- 20 images à 12,5 images/s et 13 107 commandes audio restituées.
- Sortie DMA STE conservée pour STV1 : 200 images retrouvées.
- Accès au sélecteur avec Shift droit et retour au système vérifiés lors
  du développement du lecteur.

Sur deux tonalités de 440 Hz d'amplitudes 16 et 100 en PCM 8 bits,
le rapport d'énergie hors fondamentale entre 50 et 5 500 Hz s'améliore
d'environ 3,5 et 5,7 dB par rapport au mode YM classique, à PCM identique.
Ces mesures concernent l'émulateur, deux signaux et une fenêtre d'analyse.
Elles ne prédisent ni le souffle analogique du STF ni tous les extraits musicaux.

Les captures vidéo et l'émulation peuvent surcharger le PC et produire
un ralentissement à l'écoute. Un lanceur sans capture est préférable pour
une comparaison auditive. Le dossier Windows de Hatari n'a pas la même
latence ni le même débit qu'un disque ACSI physique.

## Vérifications reproductibles du dépôt

`python -m unittest discover -s tools -p "test_*.py"` vérifie notamment :
palettes d'images uniformes, noms de sortie sans écrasement, légalité et
optimalité de petites séquences YM, continuité des états, profils de l'interface.
Les résultats de construction et versions des dépendances sont dans le
manifeste fourni avec la distribution Windows.

Le support des URL varie selon les sites et les versions de yt-dlp. Les essais
de référence utilisent des fichiers locaux ; aucune promesse de compatibilité
universelle avec une plateforme en ligne n'est faite.
