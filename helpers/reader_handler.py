import os
from globals.data_store import config
from prism import Context, BackendId

# Instancia única del contexto de Prism para compartir recursos
_prism_context = None

def get_prism_context():
    global _prism_context
    if _prism_context is None:
        _prism_context = Context()
    return _prism_context


class PrismBackendWrapper:
    def __init__(self, backend_id=None, is_best=False):
        context = get_prism_context()
        self.backend_id = backend_id
        if is_best:
            self.backend = context.create_best()
        else:
            self.backend = context.create(backend_id)

    def speak(self, text, interrupt=False):
        if not text:
            return
        try:
            self.backend.speak(text, bool(interrupt))
        except Exception as e:
            print(f"Error en speak de Prism: {e}")

    def silence(self):
        try:
            self.backend.stop()
        except Exception as e:
            pass

    def list_voices(self):
        voices = []
        try:
            count = self.backend.voices_count
            for i in range(count):
                voices.append(self.backend.get_voice_name(i))
        except Exception as e:
            pass
        return voices

    def set_voice(self, voice_name):
        try:
            count = self.backend.voices_count
            for i in range(count):
                if self.backend.get_voice_name(i) == voice_name:
                    self.backend.voice = i
                    break
        except Exception as e:
            print(f"Error al establecer voz en Prism: {e}")

    def set_volume(self, value):
        try:
            # Mapear de 0-100 a 0.0-1.0
            self.backend.volume = float(value) / 100.0
        except Exception as e:
            pass

    def set_rate(self, value):
        try:
            # Mapear de -10 a 10 al rango 0.0-1.0 (donde 0 es 0.5 de Prism)
            self.backend.rate = (float(value) + 10.0) / 20.0
        except Exception as e:
            pass

    def set_pitch(self, value):
        try:
            if self.backend_id == BackendId.ONE_CORE:
                # OneCore: recibe posición 0-4 del slider especial
                # Mapeo directo: 0=0.6, 1=0.7, 2=0.8, 3=0.9, 4=1.0
                pitch_values = [0.6, 0.7, 0.8, 0.9, 1.0]
                idx = max(0, min(4, int(value)))
                self.backend.pitch = pitch_values[idx]
            else:
                # SAPI: mapeamos [-10, 10] a [0.0, 1.0] (0.5 = neutro)
                self.backend.pitch = (float(value) + 10.0) / 20.0
        except Exception as e:
            pass


class ReaderHandler:
    def __init__(self, lector=None):
        sistema = config['sistemaTTS'] if lector is None else lector
        # TODOS los lectores pasan por configurar_tts, también los que no usan
        # ningún puente: es ahí donde se cierran los puentes de los demás. Si
        # sapi5/onecore/auto se construyeran aquí, el servidor del motor
        # anterior seguiría vivo con su modelo cargado hasta cerrar VeTube.
        # De paso, un motor nuevo (como edge) ya no hay que apuntarlo también
        # en esta lista: basta con añadirlo en configurar_tts.
        from TTS.lector import configurar_tts
        self._lector = configurar_tts(sistema)

        # Intentar inicializar SAPI5 para alertas y anuncios secundarios del sistema.
        # Si falla (por ejemplo, en sistemas sin SAPI o que no son Windows), se usa OneCore de respaldo.
        # Si OneCore también falla, se recurre al mejor backend disponible en el sistema.
        try:
            self._leer = PrismBackendWrapper(BackendId.SAPI)
        except Exception as e:
            print(f"Advertencia: No se pudo inicializar SAPI5 para anuncios del sistema ({e}). Intentando OneCore...")
            try:
                self._leer = PrismBackendWrapper(BackendId.ONE_CORE)
            except Exception as ex:
                print(f"Advertencia: No se pudo inicializar OneCore para anuncios del sistema ({ex}). Usando el mejor disponible...")
                self._leer = PrismBackendWrapper(is_best=True)


    def set_tts(self, nuevo_tts):
        # Igual que en __init__: pasar por configurar_tts siempre, para que al
        # dejar piper o kokoro se cierre su servidor en vez de quedarse en
        # memoria con el modelo cargado (Kokoro son unos 350 MB).
        from TTS.lector import configurar_tts
        self._lector = configurar_tts(nuevo_tts)

    def set_sapi(self, sapi):
        config['sapi'] = sapi

    def leer_mensaje(self, mensaje):
        """El chat: los mensajes y los eventos del directo.

        Con la casilla «Usar voz sapi» marcada salen por la voz SAPI 5
        secundaria y por ahí solamente, tenga el usuario el motor que tenga.
        Eso es justo lo que la casilla ofrece: una segunda voz que lee el chat
        mientras el lector de pantalla sigue libre para moverse por el
        programa. Habla con _leer directamente y no llamando a leer_sapi()
        porque ese otro camino lleva los avisos del programa, donde la
        excepción de piper/kokoro/edge sí tiene sentido (ver leer_sapi).
        """
        if config['sapi']:
            self._leer.speak(mensaje)
        else:
            self.leer_auto(mensaje)

    def leer_sapi(self, mensaje):
        """Avisos del programa: «Ingresando al chat», errores de conexión…

        Salen por el motor activo cuando ese motor tiene voz propia, y caen en
        la voz SAPI secundaria con auto, sapi5 y onecore. No mira la casilla:
        estos avisos no son chat.
        """
        if config['sistemaTTS'] in ("piper", "kokoro", "edge"):
            self.leer_auto(mensaje)
        else:
            self._leer.speak(mensaje)

    def leer_auto(self, mensaje):
        self._lector.speak(mensaje)

    def silence(self):
        # Silencia la voz principal y la voz SAPI secundaria.
        self._lector.silence()
        self._leer.silence()

    def close(self):
        if hasattr(self._lector, 'close'):
            self._lector.close()
