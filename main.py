from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import NOM_APPLICATION, DESCRIPTION, VERSION, ADRESSE_SERVEUR, PORT_SERVEUR
from routes import routeur
from file_utils import demarrer_nettoyage_automatique

app = FastAPI(
    title=NOM_APPLICATION,
    description="""
API de reconnaissance musicale utilisant l'IA pour convertir des images de partitions en fichiers MusicXML.

## Utilisation

Envoyez une image de partition musicale via l'endpoint `/recognize` pour obtenir un fichier MusicXML.

## Formats supportes

- Images : PNG, JPG, JPEG, TIFF, BMP
- Sortie : MusicXML

## Exemple d'utilisation (Attention, je sais pas si le code marche directement comme ça, il faut surement changer l'url et l'adapter):

### Flutter/Dart
```dart
import 'package:http/http.dart' as http;
import 'dart:io';

Future<void> analyzePartition(File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://localhost:8000/recognize'),
  );

  // Ajouter le fichier image
  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path),
  );

  // Ajouter le parametre backend
  request.fields['backend'] = 'onnx'; // ou 'homr' pour utiliser HOMR qui est plus rapide

  // Envoyer la requete
  var response = await request.send();

  if (response.statusCode == 200) {
    // Sauvegarder le fichier MusicXML
    var bytes = await response.stream.toBytes();
    File resultFile = File('resultat.musicxml');
    await resultFile.writeAsBytes(bytes);
    print('Fichier MusicXML sauvegarde');
  } else {
    print('Erreur: ${response.statusCode}');
  }
}
```
    """,
    version=VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(routeur)
demarrer_nettoyage_automatique()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=ADRESSE_SERVEUR, port=PORT_SERVEUR)