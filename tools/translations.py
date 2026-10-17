"""French source strings and English UI translations; codec IDs stay unchanged."""
EN = {
    'Vos vidéos sur Atari • 320 × 200 • 16 couleurs parmi 512 • PAL': 'Your videos on Atari • 320 × 200 • 16 colours from 512 • PAL',
    '  Encodage  ': '  Encoding  ', '  Guide STF  ': '  STF guide  ', '  À propos  ': '  About  ',
    'Démarrage rapide': 'Quick start',
    'Réglages STF / ACSI conseillés': 'Recommended STF / ACSI settings',
    'Réglages STE / débit rapide': 'STE / fast storage settings',
    'Source et destination': 'Source and destination',
    'Fichier vidéo ou URL': 'Video file or URL', 'Dossier de sortie': 'Output folder',
    'Nom du clip': 'Clip name', 'Début (secondes)': 'Start (seconds)', 'Durée (secondes)': 'Duration (seconds)',
    '8 caractères maximum ; numérotation automatique': 'Up to 8 characters; automatic numbering',
    '0 = début du fichier': '0 = beginning of the file', 'Laisser vide pour tout encoder': 'Leave blank to encode the entire file',
    'Image': 'Picture', 'Palette': 'Palette', 'Tramage (dithering)': 'Dithering',
    'Détecter les changements de plan': 'Detect scene changes', 'Nettoyer le bruit vidéo': 'Reduce video noise',
    'Netteté': 'Sharpness', 'Intensité de la trame adaptative': 'Adaptive dithering strength',
    'Son et cadence': 'Audio and frame rate', 'Restitution audio': 'Audio playback', 'Nettoyage du son': 'Audio cleanup',
    'Renforcer les sources faibles (maximum +12 dB)': 'Boost quiet sources (up to +12 dB)',
    'Images par seconde du fichier STV': 'STV frame rate (frames per second)',
    'Trame fixe (stable)': 'Fixed pattern (stable)', 'Trame adaptative': 'Adaptive pattern',
    'Sans dithering': 'No dithering', 'Diffusion Floyd': 'Floyd error diffusion',
    'Palette ST optimisée': 'Optimised ST palette', 'Palette classique rapide': 'Fast classic palette',
    'Réglage audio optimisé pour STF (plus lent)': 'Optimised STF audio (slower encoding)',
    'Audio optimisé pour STE': 'Optimised STE audio', 'YM léger (expérimental)': 'Lightweight YM (experimental)',
    'Léger': 'Light', 'Désactivé': 'Off', 'Renforcé': 'Strong', 'Voix': 'Speech',
    'Naturelle': 'Natural', 'Légère': 'Mild', 'Plus nette': 'Sharper', 'Très nette': 'Very sharp',
    'Essayer sur 5 secondes': 'Try a 5-second preview', 'Encoder la vidéo': 'Encode video',
    'Ouvrir le dossier': 'Open output folder', 'Parcourir…': 'Browse…',
    'Prêt. Commencez par un essai de 5 secondes.': 'Ready. Start with a 5-second preview.',
    'Encodage en cours… Le précalcul audio STF peut prendre du temps.': 'Encoding… STF audio optimisation may take some time.',
    'Terminé : ': 'Finished: ', 'L’encodage a échoué. Consultez le détail ci-dessous.': 'Encoding failed. See the details below.',
    'Réglages': 'Settings', 'Encodage en cours': 'Encoding in progress',
    'Attendez la fin de l’encodage avant de fermer la fenêtre.': 'Please wait for encoding to finish before closing the window.',
    'Choisissez une vidéo ou saisissez une URL.': 'Choose a video or enter a URL.',
    'Le début et la durée doivent être des nombres en secondes (exemple : 12.5).': 'Start and duration must be numbers in seconds (for example, 12.5).',
    'Le début doit être positif ou nul et la durée strictement positive.': 'Start must be zero or positive, and duration must be greater than zero.',
    'Consultez le README fourni avec l’application.': 'Please refer to the README supplied with the application.',
    'STF / ACSI : 12,5 images/s, trame fixe, palette optimisée et audio STF. Ce réglage a fonctionné sur le STF du créateur ; le débit dépend de votre stockage.': 'STF / ACSI: 12.5 fps, fixed dithering, optimised palette and STF audio. Tested successfully on the creator’s STF; performance depends on your storage.',
    'STE : audio DMA et 25 images/s. Le DMA améliore le son, mais ne rend pas le disque plus rapide : choisir 12,5 images/s si nécessaire.': 'STE: DMA audio and 25 fps. DMA improves audio, but does not make storage faster: select 12.5 fps if needed.',
    'STV : environ 410 ko/s, audio préparé à 8 192 Hz. Conseillé pour commencer sur STF avec stockage ACSI.': 'STV: about 410 kB/s, audio prepared at 8,192 Hz. Recommended starting point for an STF with ACSI storage.',
    'STV : environ 819 ko/s, audio préparé à 12 288 Hz. Un débit soutenu avec de la marge est nécessaire ; 25 images/s n’est pas garanti.': 'STV: about 819 kB/s, audio prepared at 12,288 Hz. Requires sustained throughput with headroom; 25 fps is not guaranteed.',
    'Nom du clip : 1 à 8 lettres/chiffres ou _, pour la compatibilité Atari.': 'Clip name: use 1 to 8 letters, digits or underscores for Atari compatibility.',
    'Ce nom est réservé par Windows. Choisissez un autre nom de clip.': 'This name is reserved by Windows. Choose another clip name.',
    'Trop de fichiers avec ce nom : choisissez un autre nom de clip.': 'Too many files share this name: choose another clip name.',
}

ABOUT_EN = '''ST Vidéo {version}

Windows encoder and 68000 player for Atari ST / STF / STE.

A project by David Ascenso, developed from his Atari video experiments.

The PC prepares the pictures and audio; the ST reads native data without modern video decompression.
The supplied player is STFPLAY.PRG. Right Shift opens the file selector; Escape exits.

STV1, STV2 and STV3 files are supported. To use the STE’s DMA audio, select Optimised STE audio before encoding.

Third-party components and their licences are documented in THIRD_PARTY.md, supplied with the source and application.
No personal video clips or TOS ROMs are included.'''

def translate(text,language):
    return EN.get(text,text) if language=='en' else text

def option_code(options,label):
    for french,code in options.items():
        if label in (french,translate(french,'en')):return code
    raise ValueError('Unknown option: '+label)
