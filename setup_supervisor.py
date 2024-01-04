import os

def generar_archivo_conf():
    """Genera un archivo .conf para Supervisor con la configuración especificada."""

    directorio_base = os.getcwd()
    nombre_directorio_base = os.getcwd().split("/")[-1]

    ruta_archivo_conf = os.path.join(directorio_base, "config/supervisor.conf")

    with open(ruta_archivo_conf, "w") as archivo:
        archivo.write(f"""
[program:{nombre_directorio_base}]
directory={directorio_base}
command={os.path.join(directorio_base, "env", "bin", "gunicorn")} -b 0.0.0.0:5000 -w 3 run:app
user={get_usuario_actual()}
autostart=true
autorestart=true
killasgroup=true
stderr_logfile={os.path.join(directorio_base, "log", f"{nombre_directorio_base}.err.log")}
stdout_logfile={os.path.join(directorio_base, "log", f"{nombre_directorio_base}.out.log")}
""")

def get_usuario_actual():
    return os.path.expanduser('~').split("/")[-1]

if __name__ == "__main__":
    generar_archivo_conf()
