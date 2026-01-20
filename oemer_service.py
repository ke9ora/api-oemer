import subprocess
import os
from typing import Dict, Any

from config import TIMEOUT_OEMER

def verifier_oemer_installe() -> bool:
    """
    Vérifier si Oemer est OK

    Retour: True si OK, False sinon
    """
    try:
        # Essayer de lancer "oemer --help"
        resultat = subprocess.run(
            ['oemer', '--help'],     
            capture_output=True,     
            text=True,              
            timeout=10              
        )
        return resultat.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def analyser_image_partition(chemin_image: str, dossier_sortie: str, moteur: str = None) -> Dict[str, Any]:
    """
    Analyser une image de partition avec Oemer.

    Paramètres:
    - chemin_image: Où se trouve la photo
    - dossier_sortie: Où mettre les fichiers créés
    - moteur: 'tf' pour utiliser TensorFlow, 'onnx' ou None pour Onnxruntime par défaut

    Retour: Dictionnaire avec les fichiers créés
    """
    dossier_actuel = os.getcwd()

    try:
        os.chdir(dossier_sortie)

        # Construire la commande pour Oemer
        commande = ['oemer']

        if moteur == 'tf':
            commande.append('--use-tf')

        commande.append(chemin_image)

        # Lancer Oemer
        resultat = subprocess.run(
            commande,
            capture_output=True,  
            text=True,          
            timeout=TIMEOUT_OEMER  
        )

        if resultat.returncode != 0:
            raise Exception(f"Oemer a échoué: {resultat.stderr}")

        import glob
        fichiers_xml = glob.glob("*.musicxml")  
        fichiers_png = glob.glob("*.png")       

        return {
            "succes": True,
            "fichiers_musicxml": [os.path.basename(f) for f in fichiers_xml],
            "fichiers_images": [os.path.basename(f) for f in fichiers_png],
            "dossier_sortie": dossier_sortie,
        }

    except subprocess.TimeoutExpired:
        raise Exception("Timeout - Oemer a mis trop de temps à répondre.")
    except Exception as erreur:
        raise Exception(f"Erreur lors de l'analyse: {str(erreur)}")
    finally:
        os.chdir(dossier_actuel)

