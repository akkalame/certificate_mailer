from model.translator import translate
from datetime import datetime
import os, platform
from pathlib import Path

def _(text):
	lang = 'es_VE'
	return translate(text, lang)

def get_config():
	pass

def sheet_id_from_link(link):
	return link.replace("https://docs.google.com/spreadsheets/d/", "").split("/")[0]

def format_sheet_range_name(c1, f1, c2, nRows):
	f2 = nRows + f1 -1
	return f"{c1}{f1}:{c2}{f2}".upper()


def today():
	fecha_actual = datetime.now()
	return fecha_actual.strftime("%d-%m-%Y")

def mkdir(path):
	carpeta = Path(path)
	if not carpeta.exists():
		carpeta.mkdir(parents=True)
		return True

def open_container_folder(path=None):
	if not path: path = './pdf/'+today()+'/'
	carpeta = Path(path)
	command = get_explorer_command(check_os())

	if carpeta.exists():
		os.system(f'{command} "{path}"')
	else:
		os.system(f'{command} "./pdf"')

def check_os():
	sistema = platform.system()
	if sistema == "Windows":
		return "Windows"
	elif sistema == "Linux":
		return "Linux"
	else:
		return "Sistema operativo no compatible"

def get_explorer_command(system):
	if system == "Windows":
		return "explorer"
	elif system == "Linux":
		return "xdg-open"