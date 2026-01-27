import subprocess
import os
from typing import Dict, Any

from config import TIMEOUT_OEMER

# On vérifie si homr (CLI de homr) est disponible
def verifier_homr_installe() -> bool:
    """
    Vérifier si Homr est OK

    Retour: True si OK, False sinon
    """
    try:
        resultat = subprocess.run(
            ['homr', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return resultat.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

HOMR_AVAILABLE = verifier_homr_installe()


def analyser_image_partition(chemin_image: str, dossier_sortie: str, moteur: str = None) -> Dict[str, Any]:
    """
    Analyser une image de partition avec Homr.

    Paramètres:
    - chemin_image: Où se trouve la photo
    - dossier_sortie: Où mettre les fichiers créés
    - moteur: Ignoré pour homr

    Retour: Dictionnaire avec les fichiers créés
    """
    if not HOMR_AVAILABLE:
        raise Exception("HOMR n'est pas disponible. Installez-le avec: pip install homr")

    dossier_actuel = os.getcwd()

    try:
        os.chdir(dossier_sortie)

        # Construire la commande pour Homer
        commande = ['homr', chemin_image]

        # Lancer Homer
        resultat = subprocess.run(
            commande,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_OEMER
        )

        if resultat.returncode != 0:
            raise Exception(f"Homr a échoué: {resultat.stderr}")

        import glob
        fichiers_xml = glob.glob("*.musicxml")

        return {
            "succes": True,
            "fichiers_musicxml": [os.path.basename(f) for f in fichiers_xml],
            "fichiers_images": [],
            "dossier_sortie": dossier_sortie,
        }

    except subprocess.TimeoutExpired:
        raise Exception("Timeout - Homr a mis trop de temps à répondre.")
    except Exception as erreur:
        raise Exception(f"Erreur lors de l'analyse: {str(erreur)}")
    finally:
        os.chdir(dossier_actuel)
