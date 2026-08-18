from prism import BackendId, Context

from globals.data_store import config, motor_de_interfaz

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
        except Exception:
            pass

    def list_voices(self):
        voices = []
        try:
            count = self.backend.voices_count
            for i in range(count):
                voices.append(self.backend.get_voice_name(i))
        except Exception:
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
        except Exception:
            pass

    def set_rate(self, value):
        try:
            # Mapear de -10 a 10 al rango 0.0-1.0 (donde 0 es 0.5 de Prism)
            self.backend.rate = (float(value) + 10.0) / 20.0
        except Exception:
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
        except Exception:
            pass


class ReaderHandler:
    def __init__(self, lector=None):
        sistema = motor_de_interfaz() if lector is None else lector
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
            print(
                f"Advertencia: No se pudo inicializar SAPI5 para anuncios del sistema ({e}). Intentando OneCore..."
            )
            try:
                self._leer = PrismBackendWrapper(BackendId.ONE_CORE)
            except Exception as ex:
                print(
                    f"Advertencia: No se pudo inicializar OneCore para anuncios del sistema ({ex}). Usando el mejor disponible..."
                )
                self._leer = PrismBackendWrapper(is_best=True)

    def set_tts(self, nuevo_tts):
        # Igual que en __init__: pasar por configurar_tts siempre, para que al
        # dejar piper o kokoro se cierre su servidor en vez de quedarse en
        # memoria con el modelo cargado (Kokoro son unos 350 MB).
        from TTS.lector import configurar_tts

        self._lector = configurar_tts(nuevo_tts)

    def set_sapi(self, sapi):
        config["sapi"] = sapi

    def _voz_del_chat(self):
        """La voz que dice el chat: la voz SAPI 5 secundaria con la casilla
        «Usar voz sapi» marcada, y el motor elegido cuando no lo está.
        """
        return self._leer if config["sapi"] else self._lector

    def leer_mensaje(self, mensaje):
        """El chat: los mensajes y los eventos del directo.

        Con la casilla marcada salen por la voz SAPI 5 secundaria y por ahí
        solamente, tenga el usuario el motor que tenga. Eso es justo lo que la
        casilla ofrece: una segunda voz que lee el chat mientras el lector de
        pantalla sigue libre para moverse por el programa.
        """
        self._voz_del_chat().speak(mensaje)

    def leer_aviso(self, mensaje):
        """Los avisos del programa: «Ingresando al chat», los errores de
        conexión, «Mensaje copiado», «Página borrada»…

        Salen por la misma voz que el chat, y nunca por el lector de pantalla.
        Lo decidió César: oír «Ingresando al chat» en la voz del motor le
        confirma al usuario que el motor que eligió en los Ajustes funciona; y
        una frase corta dicha por el lector de pantalla «se pasa súper rápido»,
        porque el siguiente evento de foco la corta y uno se la pierde.

        Tiene nombre propio aunque hoy comparta regla con leer_mensaje: son dos
        familias distintas, y así cada llamada dice a cuál pertenece.
        """
        self._voz_del_chat().speak(mensaje)

    def leer_interfaz(self, mensaje):
        """Moverse por el programa: las flechas en la lista de mensajes, Inicio
        y Fin, cambiar de pestaña.

        Va por el lector que lee el programa, que con la casilla marcada es el
        lector de pantalla. Es la voz que sigue el ritmo del teclado cuando uno
        recorre la lista deprisa, que es de lo que se trata.
        """
        self._lector.speak(mensaje)

    def leer_motor(self, mensaje):
        """Las pruebas del motor: las frases que solo significan algo dichas
        por el motor elegido, como «Hablaré a través de este dispositivo».

        Hoy hace lo mismo que leer_interfaz, porque las dos hablan con el
        lector que está cargado, pero no son lo mismo: con la casilla marcada
        no hay ningún motor cargado y estas frases mentirían en boca del lector
        de pantalla. Por eso quien llama mira antes motor_de_interfaz() y no
        llega hasta aquí en ese caso.
        """
        self._lector.speak(mensaje)

    def silence(self):
        # Silencia la voz principal y la voz SAPI secundaria.
        self._lector.silence()
        self._leer.silence()

    def close(self):
        if hasattr(self._lector, "close"):
            self._lector.close()
