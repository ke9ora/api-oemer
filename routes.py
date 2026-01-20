from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

from file_utils import creer_dossier_temporaire, verifier_format_image
from oemer_service import analyser_image_partition
from models import MoteurAnalyse
from config import VERSION

routeur = APIRouter()

@routeur.get(
    "/health",
    summary="Verifier l'etat de l'API",
    description="Verifie que l'API et ses services fonctionnent correctement"
)
def verifier_sante():
    return {
        "status": "OK",
        "oemer_ok": True
    }

@routeur.post(
    "/recognize",
    summary="Analyser une partition musicale",
    description="""
Analyse une image de partition musicale et retourne un fichier MusicXML.

**Parametres d'entree:**
- file: Image de la partition (PNG, JPG, JPEG, TIFF, BMP)
- backend: Moteur d'analyse ('tf' ou 'onnx')

**Retour:** Fichier MusicXML telechargeable

**Temps de traitement:** Peut mettre du temps à répondre 
""",
    response_description="Fichier MusicXML genere"
)
async def reconnaitre_partition(
    file: UploadFile = File(..., description="Image de partition musicale"),
    backend: MoteurAnalyse = Form(MoteurAnalyse.onnxruntime, description="Moteur d'analyse")
):
    if not verifier_format_image(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilise PNG, JPG, JPEG, TIFF ou BMP"
        )

    dossier_temporaire = None

    try:
        _, dossier_temporaire = creer_dossier_temporaire()

        contenu_image = await file.read()  
        chemin_image = os.path.join(dossier_temporaire, f"input_{file.filename}")

        with open(chemin_image, 'wb') as f:
            f.write(contenu_image) 

        resultat = analyser_image_partition(
            chemin_image,
            dossier_temporaire,
            moteur=backend.value
        )

        if not resultat["fichiers_musicxml"]:
            raise HTTPException(
                status_code=500,
                detail="Erreur Serveur: Aucun fichier MusicXML généré"
            )

        nom_fichier_musicxml = resultat["fichiers_musicxml"][0]
        chemin_fichier_musicxml = os.path.join(dossier_temporaire, nom_fichier_musicxml)

        return FileResponse(
            path=chemin_fichier_musicxml,     
            filename=nom_fichier_musicxml,    
            media_type="application/xml",     
        )

    except Exception as erreur:
        if dossier_temporaire and os.path.exists(dossier_temporaire):
            shutil.rmtree(dossier_temporaire)

        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse: {str(erreur)}"
        )