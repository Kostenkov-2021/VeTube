import os
import tarfile
from pathlib import Path
from .lector import detect_onnx_models
from . import sherpa_handler as speaker
import wx
from globals.paths import VOICES_DIR

# Ficheros de las antiguas voces RT: no son modelos completos y el motor
# sherpa no puede usarlos (la variante RT se retiró del catálogo).
_ONNX_RT = ("encoder.onnx", "decoder.onnx")
def extract_tar(file, destination):
	if not os.path.exists(destination):
		os.makedirs(destination)
	try:
		with tarfile.open(file, 'r:gz') as tar:
			tar.extractall(destination)
	except tarfile.ReadError:
		with tarfile.open(file, 'r:') as tar:
			tar.extractall(destination)

def install_piper_voice(config, reader):
	abrir_tar = wx.FileDialog(None, _("Selecciona un paquete de voz"), wildcard=_("Archivos tar.gz (*.tar.gz)|*.tar.gz"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
	if abrir_tar.ShowModal() == wx.ID_CANCEL:
		wx.MessageBox(_('Para usar piper como sistema TTS, necesitas tener al menos una voz. Si quieres hacerlo de forma manual, extrae el paquete de voz en la carpeta "voices/voice-nombre_de_paquete" en VeTube.'), _("No se instaló ninguna voz"), wx.ICON_ERROR)
		return False
	paquete = abrir_tar.GetPath()
	nombre_paquete = os.path.splitext(os.path.basename(paquete))[0]
	destino = str(VOICES_DIR / nombre_paquete[:-3])
	extract_tar(paquete, destino)
	wx.MessageBox(_("¡Voz instalada satosfactoriamente! esta será establecida en VeTube ahora. Para cambiar de modelo de voz, puedes hacerlo a través de las configuraciones."), _("Listo"), wx.ICON_INFORMATION)
	reader=speaker.sherpaSpeak(f"{destino}/{nombre_paquete}.onnx")
	config['voz'] = 0
	abrir_tar.Destroy()
	return config, reader

def _onnx_completos(folder_path):
	"""Modelos .onnx utilizables de una carpeta de voz (excluye los ficheros
	partidos de las antiguas voces RT)."""
	import glob
	folder_str = str(folder_path)
	return [m for m in glob.glob(os.path.join(folder_str, "*.onnx"))
		if os.path.basename(m).lower() not in _ONNX_RT]

def piper_list_voices():
	if not VOICES_DIR.exists():
		return []
	folders = [f.name for f in VOICES_DIR.iterdir() if f.is_dir() and f.name.startswith("voice-")]
	valid_folders = []
	for folder in folders:
		folder_path = VOICES_DIR / folder
		if _onnx_completos(folder_path):
			valid_folders.append(folder)
	return valid_folders

def obtener_ruta_voz(nombre_carpeta):
	if not nombre_carpeta:
		return None
	# Si ya es una ruta completa/relativa a un archivo, la devolvemos directamente
	if nombre_carpeta.endswith(".onnx") or nombre_carpeta.endswith(".json"):
		return nombre_carpeta
		
	folder_path = VOICES_DIR / nombre_carpeta
	onnx_files = _onnx_completos(folder_path)
	if onnx_files:
		return str(onnx_files[0])
	return None
