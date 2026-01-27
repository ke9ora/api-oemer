from enum import Enum
from pydantic import BaseModel

class MoteurAnalyse(str, Enum):
    """
    Moteurs d'analyse disponibles

    - onnxruntime: Utilise ONNX Runtime (plus rapide)
    - homr: Utilise HOMR 
    """
    onnxruntime = "onnx"
    homr = "homr"

class RequeteAnalyse(BaseModel):
    backend: MoteurAnalyse = MoteurAnalyse.onnxruntime