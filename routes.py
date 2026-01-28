from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os
import shutil

from file_utils import creer_dossier_temporaire, verifier_format_image
from oemer_service import analyser_image_partition as analyser_oemer
from homr_service import analyser_image_partition as analyser_homr, HOMR_AVAILABLE
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
        "oemer_ok": True,
        "homr_ok": HOMR_AVAILABLE
    }

@routeur.post(
    "/recognize",
    summary="Analyser une partition musicale",
    description="""
Analyse une image de partition musicale et retourne un fichier MusicXML.

**Parametres d'entree:**
- file: Image de la partition (PNG, JPG, JPEG, TIFF, BMP)
- backend: Moteur d'analyse ('onnx' ou 'homr')

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

        if backend.value == "homr":
            if not HOMR_AVAILABLE:
                raise HTTPException(
                    status_code=503,
                    detail="HOMR n'est pas disponible"
                )
            resultat = analyser_homr(chemin_image, dossier_temporaire)
        else:
            resultat = analyser_oemer(
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

    except HTTPException:
        raise
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
- backend: Moteur d'analyse ('onnx' ou 'homr')

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

        musicxml_brut = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<score-partwise>
  <work>
    <work-title />
  </work>
  <defaults />
  <part-list>
    <score-part id="P1">
      <part-name />
      <score-instrument id="P1-I1">
        <instrument-name>Piano</instrument-name>
        <instrument-sound>keyboard.piano</instrument-sound>
      </score-instrument>
      <midi-instrument id="P1-I1">
        <midi-channel>1</midi-channel>
        <midi-program>1</midi-program>
        <volume>100</volume>
        <pan>0</pan>
      </midi-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>2</divisions>
      </attributes>
      <attributes>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>6</beats>
          <beat-type>8</beat-type>
        </time>
        <clef number="1">
          <sign>G</sign>
          <line>2</line>
        </clef>
        <clef number="2">
          <sign>F</sign>
          <line>4</line>
        </clef>
      </attributes>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
    </measure>
    <measure number="2">
      <barline location="right">
        <repeat direction="forward" />
      </barline>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
    </measure>
    <measure number="3">
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <ornaments>
            <trill-mark />
          </ornaments>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="4">
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <articulations>
            <accent />
          </articulations>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="5">
      <print new-system="yes" />
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <ornaments>
            <trill-mark />
          </ornaments>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="6">
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations>
          <articulations>
            <staccato />
          </articulations>
        </notations>
      </note>
    </measure>
    <measure number="7">
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <ornaments>
            <trill-mark />
          </ornaments>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="8">
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <articulations>
            <accent />
          </articulations>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="9">
      <print new-system="yes" />
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="10">
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>C</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>G</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>G</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>F</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="11">
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>G</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="12">
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <ornaments>
            <inverted-turn />
          </ornaments>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="13">
      <print new-system="yes" />
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations>
          <ornaments>
            <trill-mark />
          </ornaments>
        </notations>
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations>
          <articulations>
            <staccatissimo />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations>
          <articulations>
            <staccatissimo />
          </articulations>
        </notations>
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations>
          <articulations>
            <staccatissimo />
          </articulations>
        </notations>
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>E</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <barline location="right">
        <repeat direction="backward" />
      </barline>
    </measure>
    <measure number="14">
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <rest />
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <chord />
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations>
          <ornaments>
            <trill-mark />
          </ornaments>
        </notations>
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
    </measure>
    <measure number="15">
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>6</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <chord />
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <chord />
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
    </measure>
    <measure number="16">
      <note>
        <pitch>
          <step>A</step>
          <octave>5</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>1</staff>
        <notations />
      </note>
      <backup>
        <duration>1</duration>
      </backup>
      <note>
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <chord />
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <chord />
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <staff>2</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>2</duration>
      </backup>
      <note>
        <rest />
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <staff>1</staff>
        <notations />
      </note>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>2</staff>
        <notations />
      </note>
      <backup>
        <duration>3</duration>
      </backup>
      <note>
        <rest />
        <duration>3</duration>
        <voice>1</voice>
        <type>quarter</type>
        <dot />
        <staff>1</staff>
        <notations />
      </note>
      <barline location="right">
        <bar-style>heavy-heavy</bar-style>
      </barline>
    </measure>
  </part>
</score-partwise>
"""

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