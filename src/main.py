from types import SimpleNamespace
from reportbro import Report, ReportBroError

from kernel import _dict, get_config, _
from controller.email_controller import send_gmail, send_smtp, smtp_service
from controller.oauth_login import Service

from model.DataBase import DataBase
from controller.database.DBTable import (
	TabMailServer, 
	TabEmailAccount, 
	TabLanguage,
	TabPreference
	)

from utils import today, mkdir
import utils, json, glob, os, random, base64

from flask import url_for
from urllib.parse import unquote

class Main():
	def __init__(self):
		self.service = None
		self.toCertificate = []
		self.toSend = []

	def connect_to_google(self,tokenName):
		
		self.service = Service()
		self.service.get_creds(tokenName)

	def get_sheet_values(self, sheetId, rangeName):
		sheet = self.service.sheets().spreadsheets()
		result = sheet.values().get(
			spreadsheetId=sheetId, range=rangeName).execute()
		return result.get('values', [])

	def rows_to_obj(self, rows,rowSpan=1):
		data = []
		for idx, row in enumerate(rows):
			obj = _dict()
			obj.email = row[0]
			obj.name = row[1]
			obj.faltas = 0
			obj.indexRow = idx+rowSpan
			try:
				obj.faltas = int(row[9])
			except: pass

			data.append(obj)
		return data

	def availables_to_certificate(self, data, faltaMax=0):
		if type(faltaMax) == str: faltaMax = int(faltaMax)
		r = []
		for d in data:
			if d.faltas >= faltaMax and faltaMax > 0:
				continue
			r.append(d)
		self.toCertificate = r

	def generate_cert(self, templatePath, pathToSave=None):
		with open("./cert_template/"+templatePath+".json", 'r', encoding="utf-8") as f:
			content = f.read()
			print(type(content))
			reportDefinition = json.loads(content)

		additionalFonts = get_additional_fonts()
		#data = [{"name":"Isabela oliveira", "email":"devakkalame@gmail.com"}, {"name":"Pedro Oliveira","email":""}]
		for d in self.toCertificate:
			d.name = d.name.lower().title()
			report = Report(report_definition=reportDefinition, data=d, 
				additional_fonts=additionalFonts)
			report_file = report.generate_pdf()

			namePdf = d.email.replace(".", "_") if d.email != "" else generate_file_name(d.name)
			if not pathToSave:
				pathToSave = './pdf/'+today()+'/'
				mkdir(pathToSave)
			filePath = pathToSave+namePdf+'.pdf'

			with open(filePath, 'wb') as f:
				f.write(report_file)

			if d.email != "":
				dCopy = d
				dCopy.file = filePath
				self.toSend.append(dCopy)

	def send_emails(self, subject, body, emailAccount="", sendViaGoogle=0):
		if sendViaGoogle:
			service = self.service.gmail()
			method = send_gmail
		else:
			service = self.get_smtp_service(emailAccount)
			method = send_smtp

		for d in self.toSend:
			method(service, '',d.email,subject,body,attachments=[d.file])

		
		return f"{len(self.toSend)} e-mails enviados"

	def get_smtp_service(self, emailAccount):
		db = DataBase(get_db_path())
		mailAccount = TabEmailAccount(db)
		
		query = mailAccount._Listar(filters={"email": emailAccount})
		if query:
			ea = query[0]
			mailServer = TabMailServer(db)
			query2 = mailServer._Listar(filters={"server": ea.server})
			if query2:
				server = query2[0]
				useremail = make_addr_email(ea.email, ea.name)
				service = smtp_service(useremail, ea.password, ea.server, server.port, server.use_tls)
				
				return service

def make_addr_email(email, name=""):
	if not name or name == "":
		name = email.split("@")[0]
	r = _dict()
	r[email] = f"{name}"# <{email}>"
	return r


def make_process(data):
	main = Main()
	main.connect_to_google(data.credentialName)
	sheetId = utils.sheet_id_from_link(data.spreadLink)
	rangeName = f"{data.cell1.upper()}:{data.cell2.upper()}"
	rows = main.get_sheet_values(sheetId, rangeName)

	rows = main.rows_to_obj(rows, int(data.cell1[1:]))
	main.availables_to_certificate(rows, data.faltaMax)
	main.generate_cert(data.templatePath)

	if int(data.sendEmail):
		return main.send_emails(data.subject, data.body, data.emailAccount, int(data.sendViaGoogle))

	return f"{len(main.toCertificate)} certificados generados"

def save_template(str64, nameFile=""):
	#nameFile = nameFile.replace("./cert_template/", "")
	if nameFile == "":
		nameFile = generate_code(10)


	strRB = base64.b64decode(str64).decode("utf-8")
	decode_str = unquote(strRB)
	with open("./cert_template/"+nameFile+".json", "w", encoding="utf-8") as f:
		f.write(decode_str)

def generate_file_name(txt=""):
	txt = txt.lower().replace(" ", "_")
	return txt+"_"+generate_code(6)

def generate_code(length):
	digitos = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
	code = ""
	for i in range(length):
		idx = random.randint(0,len(digitos))
		code += digitos[idx:idx+1]
	return code


def get_additional_fonts(path=['./static/fonts/', './static/fonts/custom_fonts/']):
	fonts = []
	for p in path:
		fontsPath = glob.glob(p+'*.*')
		for f in fontsPath:
			name = os.path.basename(f).split(".")[0]
			fonts.append(dict(value=name, filename=f))

	return fonts

def get_tokens():
	paths = glob.glob(f'./tokens/*.json')
	r = []
	for f in paths:
		name = os.path.basename(f).split(".")[0]
		r.append(_dict(name=name))
	return r

def get_rb_templates():
	paths = glob.glob(f'./cert_template/*.json')
	r = []
	for f in paths:
		basename = os.path.basename(f)
		name = basename.split(".")[0]
		r.append(_dict(name=name))
	return r

def load_rb_template(filename):
	with open("./cert_template/"+filename+".json", "r", encoding="utf-8") as f:
		d = f.read()
		print(d)
		return json.loads(d)

def load_custom_fonts():
	fonts = get_additional_fonts(['./static/fonts/custom_fonts/'])
	contentFile = '<style type="text/css">'

	jsonContent = []
	for font in fonts:
		fontName = font['value'].replace('_',' ').replace('-',' ').lower().capitalize()
		fontUrl = url_for('static', filename= 'fonts/custom_fonts/{0}'.format(os.path.basename(font['filename'])))
		contentFile += """\n@font-face {{
			font-family: "{0}";
			src: url("{1}");
		}}""".format(font['value'], fontUrl)

		jsonContent.append({'name': fontName, 'value':font['value']})
	contentFile += '</style>'

	#with open('./templates/custom_fonts.html', 'w') as f:
	#	f.write(contentFile)
	return {'css':contentFile, 'json': json.dumps(jsonContent)}

def get_mail_servers():
	db = DataBase(get_db_path())
	mailServer = TabMailServer(db)
	
	query = mailServer._Listar(db)
	result = []
	for q in query:
		result.append(
			{
				"data": f"{q.server}:{q.port}:{q.use_tls}",
				"server_name": q.server
			}
		)
	return result

def get_email_accounts():
	db = DataBase(get_db_path())
	mailAccount = TabEmailAccount(db)
	
	query = mailAccount._Listar(db)
	result = []
	for q in query:
		raw_account = q.email.split("@")[0]
		result.append(
			{
				"data": f"{raw_account}:{q.server}:{q.password}:{q.name or ''}",
				"email": q.email
			}
		)
	return result


def get_db_path():
	config = get_config()
	dbPath = f"db/{config.db_name}"
	return dbPath


def update_settings(data):
	type_con = data.type
	del data.type

	db = DataBase(get_db_path())
	response = ""
	if type_con == "EmailServer":
		mailServer = TabMailServer(db)
		server = {"server": data.server}
		existe = mailServer._Exists(db, server)
		if existe:
			response = mailServer._Actualizar(db, data, server)
		else:
			response = mailServer._Crear(db, data)

	elif type_con == "EmailAccount":
		emailAccount = TabEmailAccount(db)
		filters = {"email": data.email}
		existe = emailAccount._Exists(db, filters)
		if existe:
			response = emailAccount._Actualizar(db, data, filters)
		else:
			response = emailAccount._Crear(db, data)

	return response

def delete_settings(data):
	type_con = data.type
	del data.type

	db = DataBase(get_db_path())
	response = ""
	if type_con == "EmailServer":
		mailServer = TabMailServer(db)
		existe = mailServer._Exists(db, data)
		if existe:
			response = mailServer._Eliminar(db, data)

	elif type_con == "EmailAccount":
		emailAccount = TabEmailAccount(db)
		existe = emailAccount._Exists(db, data)
		if existe:
			response = emailAccount._Eliminar(db, data)

	return response


def get_languages():
	db = DataBase(get_db_path())
	language = TabLanguage(db)
	langs = language._Listar()
	current = get_preference().lang
	return _dict(langs=langs, current=current)

def get_preference():
	db = DataBase(get_db_path())
	preference = TabPreference(db)
	preferencias = preference._Listar()

	r = _dict()
	for pr in preferencias:
		r[pr.key] = pr.value
	return r

if __name__ == "__main__":
	pass


