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


@routeur.post(
    "/debug",
    summary="Debugger",
    description="""
Retourne directement un fichier MusicXML.

**Parametres d'entree:**
- file: Image de la partition (PNG, JPG, JPEG, TIFF, BMP)
- backend: Moteur d'analyse ('tf' ou 'onnx')

**Retour:** Fichier MusicXML telechargeable
""",
    response_description="Fichier MusicXML genere"
)
async def debug(
    file: UploadFile = File(..., description="Image de partition musicale"),
    backend: MoteurAnalyse = Form(MoteurAnalyse.onnxruntime, description="Moteur d'analyse")
):
    # On garde la même validation que ta route "normale"
    if not verifier_format_image(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilise PNG, JPG, JPEG, TIFF ou BMP"
        )

    dossier_temporaire = None

    try:
        _, dossier_temporaire = creer_dossier_temporaire()

        # On lit quand même le fichier comme avant (même format de requête),
        # mais on ne fait aucun traitement.
        contenu_image = await file.read()
        chemin_image = os.path.join(dossier_temporaire, f"input_{file.filename}")
        with open(chemin_image, "wb") as f:
            f.write(contenu_image)

        # Génération d'un MusicXML brut (minimal) — sans traitement
        nom_fichier_musicxml = "result.musicxml"
        chemin_fichier_musicxml = os.path.join(dossier_temporaire, nom_fichier_musicxml)

        musicxml_brut = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work>
    <work-title>Input_hp.jpeg</work-title>
  </work>
  <identification>
    <creator type="composer">Transcribed by Oemer</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
      <score-instrument id="P1-I1">
        <instrument-name>Piano</instrument-name>
        <instrument-sound>keyboard.piano</instrument-sound>
      </score-instrument>
      <midi-instrument id="P1-I1">
        <midi-channel>1</midi-channel>
        <midi-program>1</midi-program>
        <volume>80</volume>
        <pan>0</pan>
      </midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <sound tempo="90"/>
    <measure number="1">
      <attributes>
        <divisions>16</divisions>
        <key>
          <fifths>1</fifths>
        </key>
        <staves>2</staves>
        <clef number="1">
          <sign>G</sign>
          <line>2</line>
        </clef>
        <clef number="2">
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>B</step>
          <alter>0</alter>
          <octave>4</octave>
        </pitch>
        <duration>8</duration>
        <type>eighth</type>
        <stem>down</stem>
        <staff>1</staff>
        <voice>1</voice>
      </note>
      <backup>
        <duration>8</duration>
      </backup>
      <note>
        <rest measure="yes"/>
        <duration>8</duration>
        <staff>2</staff>
      </note>
    </measure>
    <measure number="2">
      <note>
        <pitch>
          <step>E</step>
          <alter>0</alter>
          <octave>5</octave>
        </pitch>
        <duration>12</duration>
        <type>eighth</type>
        <dot/>
        <stem>down</stem>
        <staff>1</staff>
        <voice>1</voice>
      </note>
      <backup>
        <duration>12</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <alter>0</alter>
          <octave>4</octave>
        </pitch>
        <duration>24</duration>
        <type>quarter</type>
        <dot/>
        <stem>up</stem>
        <staff>2</staff>
        <voice>1</voice>
      </note>
      <backup>
        <duration>12</duration>
      </backup>
      <note>
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>5</octave>
        </pitch>
        <duration>4</duration>
        <type>16th</type>
        <stem>down</stem>
        <staff>1</staff>
        <voice>1</voice>
      </note>
      <note>
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>8</duration>
        <type>eighth</type>
        <stem>down</stem>
        <staff>1</staff>
        <voice>1</voice>
      </note>
    </measure>
  </part>
</score-partwise>"""

        with open(chemin_fichier_musicxml, "w", encoding="utf-8") as f:
            f.write(musicxml_brut)

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
            detail=f"Erreur lors du debug: {str(erreur)}"
        )