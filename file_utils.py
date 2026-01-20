import tempfile
import shutil
import os
import time
import threading
import uuid
from typing import Tuple

from config import TIMEOUT_SESSION, NETTOYAGE_AUTO, FORMATS_ACCEPTES

sessions_actives = {}

def creer_dossier_temporaire() -> Tuple[str, str]:
    """
    Créé un dossier temporaire unique pour une nouvelle session.
    Retour: (id_session, chemin_dossier_temporaire)
    """
    id_session = str(uuid.uuid4())  
    dossier_temp = tempfile.mkdtemp(prefix=f"musique_{id_session}_")
    sessions_actives[id_session] = dossier_temp
    return id_session, dossier_temp

def verifier_format_image(nom_fichier: str) -> bool:
    """
    Vérifier si le fichier uploadé est dans un format d'image accepté.
    On accepte seulement les photos de partitions:
    PNG, JPG, JPEG, TIFF, BMP
    Retour: True si accepté, False sinon
    """
    nom_minuscule = nom_fichier.lower()
    return nom_minuscule.endswith(FORMATS_ACCEPTES)

def sauvegarder_fichier_upload(file_upload, dossier_temp: str, nom_fichier: str) -> str:
    """
    Sauvegarder le fichier uploadé dans un dossier temporaire.

    Paramètres:
    - file_upload: L'objet fichier reçu
    - dossier_temp: Où le sauvegarder
    - nom_fichier: Comment l'appeler

    Retour: Le chemin complet du fichier sauvegardé
    """
    chemin_fichier = os.path.join(dossier_temp, f"input_{nom_fichier}")

    with open(chemin_fichier, 'wb') as fichier:
        contenu = file_upload.read()
        fichier.write(contenu)

    return chemin_fichier

def nettoyer_sessions_expirees():
    while True:  
        heure_actuelle = time.time()
        sessions_a_supprimer = []

        # Chercher les sessions expirées
        for id_session, dossier_temp in sessions_actives.items():
            if os.path.exists(dossier_temp):
                heure_modification = os.path.getmtime(dossier_temp)

                if heure_actuelle - heure_modification > TIMEOUT_SESSION:
                    sessions_a_supprimer.append(id_session)
            else:
                # Le dossier n'existe plus
                sessions_a_supprimer.append(id_session)

        # Supprimer les sessions expirées
        for id_session in sessions_a_supprimer:
            dossier_temp = sessions_actives[id_session]
            try:
                if os.path.exists(dossier_temp):
                    shutil.rmtree(dossier_temp)  # Supprimer tout le dossier
                del sessions_actives[id_session]  # Retirer de la liste
            except Exception:
                pass

        time.sleep(NETTOYAGE_AUTO)

def demarrer_nettoyage_automatique():
    thread_nettoyage = threading.Thread(
        target=nettoyer_sessions_expirees,
        daemon=True,  # S'arrête quand le programme principal s'arrête
        name="NettoyeurFichiers"
    )
    thread_nettoyage.start()
