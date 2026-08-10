from utils import fajustes, funciones
from globals.paths import DATA_FILE, FAVORITOS_FILE, MENSAJES_DESTACADOS_FILE

# Inicialización global de configuración
if DATA_FILE.exists():
    config = fajustes.leerConfiguracion()
else:
    fajustes.escribirConfiguracion()
    config = fajustes.leerConfiguracion()

# Inicialización global de favoritos y mensajes destacados
favorite = funciones.leerJsonLista(FAVORITOS_FILE)
mensajes_destacados = funciones.leerJsonLista(MENSAJES_DESTACADOS_FILE)
favs = funciones.convertirLista(favorite, 'titulo', 'url')
msjs = funciones.convertirLista(mensajes_destacados, 'mensaje', 'titulo')
divisa="Por defecto"
# La traducción de mensajes no es persistente: arranca desactivada en cada sesión (se ajusta desde el diálogo)
dst = ""
