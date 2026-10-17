# Format STV, version 1.0

Tous les entiers sont big-endian. Un fichier comporte un en-tête de
32 768 octets, puis un bloc de 32 768 octets par image. Le format ne
compresse pas les images. Le lecteur doit vérifier le format avant lecture.

## En-tête

| Position | Taille | Contenu |
| --- | --- | --- |
| 0 | 8 | `STFVID1\0`, `STFVID2\0` ou `STFVID3\0` |
| 8 | 4 | Nombre d'images STV |
| 12 | 4 | Fréquence audio préparée : 12 288 ou 8 192 Hz |
| 16 | 4 | Cadence : 25, ou 1250 pour 12,5 images/s |
| 256 | 3072 | Table de 256 entrées × 3 commandes PSG de 32 bits |

Une commande PSG contient le numéro de registre dans l'octet de poids fort
et le volume dans les bits 8 à 15. L'assemblage exploite l'accès 68000 au
sélecteur/données du YM2149. Voir le source du lecteur pour les écritures.

## Bloc image

| Position relative | Taille | Contenu |
| --- | --- | --- |
| 0 | 32 000 | 320 × 200, quatre bitplanes entrelacés au format ST |
| 32 000 | 32 | 16 mots de palette ST, composantes 3 bits |
| 32 032 | variable | PCM ou commandes YM compactes |
| 32 744 | 12 | État initial YM des trois voies pour STV2/STV3 |
| 32 760 | 2 | Nombre d'échantillons/commandes dans ce bloc |

À 25 images/s, le nombre alterne entre 491 et 492 ; à 12,5 images/s,
entre 655 et 656. Les zones non utilisées sont réservées. Une image à
12,5 images/s correspond à un prélèvement sur deux des images source à 25 Hz.

STV1 stocke du PCM 8 bits non signé, utilisé avec une table de trois volumes
YM par échantillon. Sur STE détecté via le cookie machine, le PCM est converti
en signé et rééchantillonné à 12 517 Hz pour le DAC DMA.

STV2/STV3 stockent un octet de commande : `registre = 8 + code // 16`,
`volume = code & 15`, pour `0 <= code < 48`. Une seule voie est modifiée
à chaque échantillon. STV2 recale la lecture à chaque image. STV3 conserve
l'état final entre les blocs et les enchaîne dans l'interruption audio.
Une boucle de correction ajuste doucement la cadence via les rechargements
fractionnaires du timer MFP, sans abandon systématique des queues de blocs.
Sur STE, ces deux formats continuent à utiliser le YM.

Le lecteur restaure l'affichage, les interruptions et le son à sa sortie.
Le fichier de diagnostic PLAYSTAT.BIN contient six entiers 32 bits : images,
VBL, échantillons comptabilisés, échantillons abandonnés, mode DMA, réservé.
En DMA, le compteur audio représente les échantillons programmés, pas une
mesure exacte de la sortie matérielle.
