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
	TabPreference,
	TabMailTemplate
	)

from utils import today, mkdir
import utils, json, glob, os, random, base64
from pathlib import Path
from flask import url_for
from urllib.parse import unquote
from docxtpl import DocxTemplate
from docx2pdf import convert
import pythoncom


class Main():
	def __init__(self):
		pythoncom.CoInitialize()
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
			obj.email = row[0].strip()
			obj.name = row[1].strip()
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
		tp = "./cert_template/"+templatePath
		if Path(tp+".docx").exists():
			tp = tp + ".docx"
		else:
			return 

		pathToSave = validate_path_to_save(pathToSave)

		self.gen_by_docx(tp, pathToSave)

	def gen_by_docx(self, tp, pathToSave=None):
		
		for idx, d in enumerate(self.toCertificate):
			print("Geração de certificado ",idx,"/",len(self.toCertificate))
			doc = DocxTemplate(tp)
			d.name = d.name.lower().title()
			doc.render(d)
			filename = get_name_pdf(d, pathToSave)
			filePath = pathToSave+filename
			doc.save(f"{filePath}.docx")
			try:
				convert(f"{filePath}.docx", f"{filePath}.pdf")
			except Exception as e:
				pass

			if d.email != "":
				dCopy = d
				dCopy.file = f"{filePath}.pdf"
				self.toSend.append(dCopy)

			#if os.path.exists(filePath+".pdf"):
			#	os.remove(filePath+".docx")
		cleanOutputs(pathToSave)

	def set_just_send(self):
		pathToSave = validate_path_to_save(None)
		for idx, d in enumerate(self.toCertificate):
			if d.email != "":
				dCopy = d
				filename = d.email.replace(".", "_")
				dCopy.file = f"{pathToSave}/{filename}.pdf"
				self.toSend.append(dCopy)

	def gen_by_rb(self, tp, pathToSave=None):
		with open(tp, 'r', encoding="utf-8") as f:
			content = f.read()
			reportDefinition = json.loads(content)
			
		additionalFonts = get_additional_fonts()
		#data = [{"name":"Isabela oliveira", "email":"devakkalame@gmail.com"}, {"name":"Pedro Oliveira","email":""}]
		for d in self.toCertificate:
			d.name = d.name.lower().title()
			report = Report(report_definition=reportDefinition, data=d, 
				additional_fonts=additionalFonts)
			report_file = report.generate_pdf()

			namePdf = get_name_pdf(d)
			
			filePath = pathToSave+namePdf+'.pdf'

			with open(filePath, 'wb') as f:
				f.write(report_file)

			if d.email != "":
				dCopy = d
				dCopy.file = filePath
				self.toSend.append(dCopy)

	def send_emails(self, subject="", body="", emailAccount="", sendViaGoogle=False, useEmailTp=False, emailTemplate=""):
		print("Envío de correos electrónicos")
		if sendViaGoogle:
			service = self.service.gmail()
			method = send_gmail
		else:
			service = self.get_smtp_service(emailAccount)
			method = send_smtp
		if useEmailTp:
			subject, body = get_email_tp_data_pretty(emailTemplate)
			

		sents = 0
		emailsSent = []
		emailsUnsent = []
		for d in self.toSend:
			if Path(d.file).exists():
				try:
					sub = subject.replace("{{name}}", d.name)
					bod = body.replace("{{name}}", d.name)

					method(service, '',d.email,sub,bod,attachments=[d.file])
					sents += 1
					print("Enviado para",d.email)
					emailsSent.append(d.email)
				except Exception as e:
					print("Erro ao enviar e-mail para ",d.email)
					log(str(e))
					emailsUnsent.append(d.email)

		return f"{sents} e-mails enviados"

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

def get_name_pdf(d, pathToSave=None):
	filename = d.email.replace(".", "_") if d.email != "" else generate_file_name(d.name)
	if pathToSave:
		while Path(pathToSave+filename+".pdf").exists():
			nameData = d.email.replace(".", "_") if d.email else d.name
			filename = generate_file_name(nameData)

	return filename

def validate_path_to_save(pathToSave):
	if not pathToSave:
		pathToSave = './pdf/'+today()+'/'
		mkdir(pathToSave)
	return pathToSave

def make_process(data):
	main = Main()
	main.connect_to_google(data.credentialName)
	sheetId = utils.sheet_id_from_link(data.spreadLink)
	rangeName = f"{data.cell1.upper()}:{data.cell2.upper()}"
	rows = main.get_sheet_values(sheetId, rangeName)

	rows = main.rows_to_obj(rows, int(data.cell1[1:]))
	main.availables_to_certificate(rows, data.faltaMax)
	if not int(data.justSend):
		main.generate_cert(data.templatePath)
	else:
		main.set_just_send()

	if int(data.sendEmail):
		return main.send_emails(data.subject, data.body, data.emailAccount, int(data.sendViaGoogle),
						  data.useEmailTp,
						  data.emailTemplate)

	return f"{len(main.toCertificate)} certificados generados"

def save_template(str64, nameFile=""):
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

def get_cert_templates():
	return get_docx_templates()

def get_docx_templates():
	r = []
	for ext in (".docx", ".doc"):
		paths = glob.glob(f'./cert_template/*{ext}')
		for f in paths:
			basename = os.path.basename(f)
			name = basename.split(".")[0]
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

def get_email_templates():
	db = DataBase(get_db_path())
	mailTemplate = TabMailTemplate(db)
	query = mailTemplate._Listar(db, columns=["name"])
	return query

def get_blank_email_template():
	paths = glob.glob(f'./static/email_template/email_tp.html')

	for f in paths:
		basename = os.path.basename(f)
		name = basename.split(".")[0]
		if name == "email_tp": continue
		path = url_for('static', filename='email_template/'+basename)
		return _dict(name=name, path=path)
	
def get_email_tp_data_pretty(emailTemplate):
	try:
		tpData = get_email_template_data(emailTemplate)[0]
		subject = tpData.subject
		del tpData["subject"]
		with open("./static/email_template/email_tp.html", "r", encoding="utf-8") as f:
			body = f.read().replace("\n", "")
			for key in tpData:
				body = body.replace("{{"+key+"}}", tpData[key] or "")
		return subject, body
	
	except Exception as e:
		log(str(e))
		raise e
def load_rb_template(filename):
	with open("./cert_template/"+filename+".json", "r", encoding="utf-8") as f:
		d = f.read()
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

def update_email_tp(data):
	db = DataBase(get_db_path())
	
	mailTemplate = TabMailTemplate(db)
	cond = {"name": data.name}
	existe = mailTemplate._Exists(db, cond)

	if existe:
		response = mailTemplate._Actualizar(db, data, cond)
	else:
		response = mailTemplate._Crear(db, data)
	return response

def get_email_template_data(name):
	db = DataBase(get_db_path())
	mailTemplate = TabMailTemplate(db)
	
	query = mailTemplate._Listar(db, filters={"name": name})
	
	return query

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


def cleanOutputs(path, extension='docx'):
        files = glob.glob(f'{path}/*.{extension}')
        for file in files:
            try:
                nameFile = file.split('.'+extension)[0]
                os.remove(file)

            except Exception as e:
                pass


def log(data):
	with open("log.txt", "a", encoding="utf-8") as f:
		f.write(data+"\n")

if __name__ == "__main__":
	pass


