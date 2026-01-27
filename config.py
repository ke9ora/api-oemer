NOM_APPLICATION = "API Oemer"
DESCRIPTION = "Transformer photos de partitions en fichiers MusicXML"
VERSION = "1.0.0"

ADRESSE_SERVEUR = "0.0.0.0"
PORT_SERVEUR = 8000

FORMATS_ACCEPTES = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')

TIMEOUT_OEMER = 600      # 10 minutes max pour analyser une image
TIMEOUT_SESSION = 3600   # Garder les fichiers temporaires 1 heure
NETTOYAGE_AUTO = 300     # Vérifier toutes les 5 minutes si faut nettoyer