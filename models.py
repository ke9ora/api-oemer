from enum import Enum
from pydantic import BaseModel

class MoteurAnalyse(str, Enum):
    """
    Moteurs d'analyse disponibles

    - tensorflow: Utilise TensorFlow (plus precis)
    - onnxruntime: Utilise ONNX Runtime (plus rapide)
    """
    tensorflow = "tf"
    onnxruntime = "onnx"

class RequeteAnalyse(BaseModel):
    backend: MoteurAnalyse = MoteurAnalyse.onnxruntime