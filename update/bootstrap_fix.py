import sys
import shutil
import os
import subprocess
import time
import ctypes
import traceback
import logging

logger = logging.getLogger(__name__)

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CANCELLED = 2

LOG_FILE = os.path.join(os.environ.get('TEMP', os.path.expanduser('~')), 'vetube_bootstrap_debug.txt')
ROLLBACK_SIGNAL = '_rollback_needed'


def log(msg: str) -> None:
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def kill_process(pid: int) -> None:
    log(f"Intentando matar proceso PID: {pid}")
    try:
        PROCESS_TERMINATE = 1
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        if handle:
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
            log("Proceso terminado exitosamente.")
        else:
            log("No se pudo obtener handle del proceso (¿ya estaba cerrado?).")
    except Exception as e:
        log(f"Error matando proceso: {e}")


def _write_rollback_signal(dest: str) -> None:
    signal_path = os.path.join(dest, ROLLBACK_SIGNAL)
    try:
        with open(signal_path, 'w') as f:
            f.write(str(int(time.time())))
        log(f"Rollback signal written: {signal_path}")
    except Exception as e:
        log(f"Failed to write rollback signal: {e}")


def main() -> None:
    log("=== INICIO BOOTSTRAP ===")
    log(f"Argumentos recibidos: {sys.argv}")

    if len(sys.argv) < 5:
        log("ERROR: No hay suficientes argumentos.")
        sys.exit(EXIT_FAILURE)

    exit_code = EXIT_FAILURE

    try:
        pid = int(sys.argv[1])
        source = sys.argv[2]
        dest = sys.argv[3]
        exe_path = sys.argv[4]

        log(f"Config inicial -> Source: {source} | Dest: {dest} | Exe: {exe_path}")

        if os.path.basename(os.path.normpath(dest)) == "_internal":
            log("Detectado destino '_internal'. Corrigiendo a directorio padre.")
            dest = os.path.dirname(os.path.normpath(dest))
            log(f"Nuevo Destino: {dest}")

        time.sleep(1)
        kill_process(pid)
        time.sleep(2)

        if os.path.exists(source) and os.path.exists(dest):
            log("Iniciando copia de archivos...")
            try:
                shutil.copytree(source, dest, dirs_exist_ok=True)
                log("Copia finalizada correctamente.")
            except PermissionError as e:
                log(f"ERROR copiando archivos (permiso deniado): {e}")
                log(traceback.format_exc())
                _write_rollback_signal(dest)
                sys.exit(EXIT_CANCELLED)
            except Exception as e:
                log(f"ERROR copiando archivos: {e}")
                log(traceback.format_exc())
                _write_rollback_signal(dest)
                sys.exit(EXIT_FAILURE)
        else:
            log("ERROR: La carpeta source o dest no existen.")
            sys.exit(EXIT_FAILURE)

        log("Intentando relanzar aplicación...")

        exe_path = os.path.normpath(exe_path)
        log(f"Ruta exe original: {exe_path}")

        final_exe_path = exe_path
        if not os.path.exists(final_exe_path):
            log("El exe no existe en la ruta original. Buscando alternativas...")
            candidate = os.path.join(dest, os.path.basename(exe_path))
            if os.path.exists(candidate):
                final_exe_path = candidate
                log(f"Encontrado en raíz destino: {final_exe_path}")
            else:
                clean_path = exe_path.replace("_internal\\", "").replace("_internal/", "")
                if os.path.exists(clean_path):
                    final_exe_path = clean_path
                    log(f"Encontrado limpiando ruta: {final_exe_path}")

        if os.path.exists(final_exe_path):
            working_dir = os.path.dirname(os.path.abspath(final_exe_path))
            log(f"Lanzando: {final_exe_path}")
            log(f"Directorio de trabajo (CWD): {working_dir}")

            os.chdir(working_dir)

            try:
                subprocess.Popen([final_exe_path],
                                 creationflags=subprocess.DETACHED_PROCESS,
                                 cwd=working_dir,
                                 close_fds=False,
                                 shell=False)
                log("subprocess.Popen llamado con éxito (DETACHED).")
                exit_code = EXIT_SUCCESS
            except Exception as e:
                log(f"Fallo intento 1: {e}")
                log("Intentando fallback con shell=True...")
                try:
                    subprocess.Popen(f'"{final_exe_path}"', shell=True, cwd=working_dir)
                    log("Fallback lanzado con éxito.")
                    exit_code = EXIT_SUCCESS
                except Exception as e2:
                    log(f"Fallo intento 2: {e2}")
                    exit_code = EXIT_FAILURE
        else:
            log(f"ERROR CRÍTICO: No se encontró el ejecutable en ninguna ruta probada. Última intentada: {final_exe_path}")
            exit_code = EXIT_FAILURE

    except Exception as e:
        log(f"ERROR GLOBAL NO CONTROLADO: {e}")
        log(traceback.format_exc())
        exit_code = EXIT_FAILURE

    log(f"=== FIN BOOTSTRAP (exit={exit_code}) ===")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
