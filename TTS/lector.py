# lector:
from . import sonata_handler
from . import sherpa_handler
import glob
import os
from helpers.reader_handler import PrismBackendWrapper
from prism import BackendId

"""
Esto es un gestionador de TTS. Permite manejar el uso de diferentes motores de texto a voz como:
1. Prism Accessibility Library
2. Sonata (motor Piper gRPC): las voces Piper, incluidas las variantes RT.
3. Puente sherpa-onnx (habla el mismo protocolo sonata_grpc): el modelo Kokoro.

Cada motor tiene su propio servidor y solo uno vive a la vez: al elegir un
lector se cierran los puentes de todos los demás. Eso incluye elegir un lector
que no usa ninguno (auto, sapi5, onecore): si no, el servidor del motor
anterior se quedaba en memoria con su modelo cargado hasta cerrar VeTube.
"""
# Motores con servidor propio: nombre en config['sistemaTTS'] -> módulo puente.
# Basta añadir una línea aquí para un motor nuevo; la regla «solo uno vivo»
# se cumple sola en vez de tener que acordarse de cerrar los otros uno por uno.
PUENTES = {
	"piper": sonata_handler,
	"kokoro": sherpa_handler,
}

def configurar_tts(lector):
	for nombre, puente in PUENTES.items():
		if nombre != lector:
			puente.detener_puente()
	if lector == "auto":
		return PrismBackendWrapper(is_best=True)
	elif lector == "sapi5":
		return PrismBackendWrapper(BackendId.SAPI)
	elif lector == "onecore":
		return PrismBackendWrapper(BackendId.ONE_CORE)
	elif lector == "piper":
		return sonata_handler.piperSpeak()
	elif lector == "kokoro":
		return sherpa_handler.sherpaSpeak()
	else:
		raise Exception("Lector no soportado.")

def detect_onnx_models(path):
    # Solo las carpetas «voice-*», que son las de Piper: en voices/ vive también
    # el paquete de Kokoro (voices/kokoro-multi-lang-v1_0/model.onnx), y contarlo
    # como voz de Piper dejaba mudo a quien tuviera Kokoro y ninguna voz de
    # Piper — el arranque creía que ya había una y no ofrecía descargarla.
    # Mismo criterio que piper_list_voices().
    onnx_models = glob.glob(path + '/voice-*/*.onnx')
    if onnx_models:
        # Filtrar encoder.onnx para no duplicar las voces RT: sus dos ficheros
        # viven en la misma carpeta y el que carga sonata es decoder.onnx.
        onnx_models = [m for m in onnx_models if os.path.basename(m).lower() != "encoder.onnx"]
        if len(onnx_models) > 1:
            return onnx_models
        elif len(onnx_models) == 1:
            return onnx_models[0]
    return None
