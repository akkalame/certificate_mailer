from flask import session

from apps.certificate_mailer.googlecon import GoogleCon
from apps.certificate_mailer.utils import today, mkdir, sheet_id_from_link, generate_file_name, generate_code
from apps.certificate_mailer.email_controller import send_smtp, smtp_service
from apps import _dict
from apps.controllers import (
	listEmailTemplate, 
	listEmailAccount, 
	listEmailServer, 
	listGoogleTokens, 
	current_user_to_arg,
	updateGOAT,
	listSessionVariables,
	updateSessionVariable
)
import json, glob, os
from pathlib import Path
from weasyprint import HTML, CSS, Document
from weasyprint.text.fonts import FontConfiguration
from copy import deepcopy
from flask_login import (
	current_user
)
from apps import socket_io_events as ioe




basedir = os.path.abspath(os.path.dirname(__file__))

class Main():
	def __init__(self):
		self.googleCon = None
		self.toCertificate = []
		self.toSend = []

	def connect_to_google(self,tokenName):
		user = current_user_to_arg(current_user)
		if user:
			googleToken = listGoogleTokens({"user_id": user.id, "name": tokenName})
			googleTokenInfo = {}
			
			if googleToken:
				googleTokenInfo = googleToken[0]
			self.googleCon = GoogleCon()
			self.googleCon.load_creds(googleTokenInfo)

			# actualizo el token en la db
			if self.googleCon.gCreds:
				token = self.googleCon.gCreds.to_json()
				if isinstance(token, str):
					token = json.loads(token)
				token = _dict(token)
				if token.token != googleTokenInfo.token:
					user = current_user_to_arg(current_user)
					token.user_id = user.id
					token.name = tokenName
					updateGOAT(token)
			
			return self.googleCon.gCreds
		raise "User not connected"

	def get_sheet_values(self, sheetId, rangeName):
		sheet = self.googleCon.sheets().spreadsheets()
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
		ext = ".html"
		tp = os.path.join(basedir,"cert_template/"+templatePath)
		if Path(tp+ext).exists():
			tp = tp + ext
		else:
			return 

		pathToSave = validate_path_to_save(pathToSave)
		self.gen_by_html(tp, pathToSave)

	
	def gen_by_html(self, tp, pathToSave=None):
		with open(tp, "r", encoding="utf-8") as f:
			baseHtml = f.read()
		font_config = FontConfiguration()

		with open(os.path.join(basedir, "../static/assets/css/custom_fonts.css"), "r", encoding="utf-8") as f:
			css_content = f.read()
		with open(os.path.join(basedir, "../static/assets/css/edit-cert.css"), "r", encoding="utf-8") as f:
			css_content += f.read()
		
		css = CSS(string=str(css_content), font_config=font_config)
		
		ioe.progress(0, len(self.toCertificate), title="Generacíon de Certificados", 
				 description=f" 0/{len(self.toCertificate)}")
		for idx, d in enumerate(self.toCertificate):
			
			d.name = d.name.lower().title()
			tpl = deepcopy(baseHtml)
			tpl = tpl.replace("${name}", d.name)
			
			html = HTML(string=tpl)
			filename = get_name_pdf(d, pathToSave)
			filePath = pathToSave+filename
			try:
				html.write_pdf(f"{filePath}.pdf", stylesheets=[css], font_config=font_config)
				ioe.progress(idx+1, len(self.toCertificate), title="Generacíon de Certificados", 
				 description=f"{d.name}. {idx+1}/{len(self.toCertificate)}")
			except Exception as e:
				raise e

			if d.email != "":
				dCopy = d
				dCopy.file = f"{filePath}.pdf"
				self.toSend.append(dCopy)


	def set_just_send(self):
		pathToSave = validate_path_to_save(None)
		for idx, d in enumerate(self.toCertificate):
			if d.email != "":
				dCopy = d
				filename = d.email.replace(".", "_")
				dCopy.file = f"{pathToSave}/{filename}.pdf"
				self.toSend.append(dCopy)
	
	def send_emails(self, subject="", body="", emailAccount="", useEmailTp=False, emailTemplate=""):
		
		service = self.get_smtp_service(emailAccount)
		method = send_smtp
		if useEmailTp:
			subject, body = get_email_tp_data_pretty(emailTemplate)
			

		sents = 0
		emailsSent = []
		emailsUnsent = []
		for idx, d in enumerate(self.toSend):
			ioe.progress(idx+1, len(self.toSend), title="Envío de Certificados", 
				description=f"{d.name}. {idx+1}/{len(self.toSend)}")
			if Path(d.file).exists():
				try:
					sub = subject.replace("{{name}}", d.name)
					bod = body.replace("{{name}}", d.name)

					method(service, '',d.email,sub,bod,attachments=[d.file])
					sents += 1
					emailsSent.append(d.email)
				except Exception as e:
					emailsUnsent.append(_dict(email=d.email, name=d.name))

		ioe.msgprint(f"{sents} e-mails enviados")
		
		if emailsUnsent:
			msg = ""
			for e in emailsUnsent:
				msg += f"{e.name}, {e.email} \n"
			ioe.msgprint(msg)

	def get_smtp_service(self, emailAccount):
		query = listEmailAccount(filters={"email": emailAccount})
		if query:
			ea = query[0]
			query2 = listEmailServer(filters={"server": ea.server})
			if query2:
				server = query2[0]
				useremail = make_addr_email(ea.email, ea.name)
				service = smtp_service(useremail, ea.password, ea.server, server.port, server.use_tls)
				
				return service



def make_process(data):
	try:
		main = Main()
		creds = main.connect_to_google(data.credentialName)
		if creds:
			sheetId = sheet_id_from_link(data.spreadLink)
			rangeName = f"{data.cell1.upper()}:{data.cell2.upper()}"
			rows = main.get_sheet_values(sheetId, rangeName)

			rows = main.rows_to_obj(rows, int(data.cell1[1:]))
			main.availables_to_certificate(rows, data.faltaMax)
			if not int(data.justSend):
				main.generate_cert(data.templatePath)
			else:
				main.set_just_send()

			if int(data.sendEmail):
				main.send_emails(data.subject, data.body, data.emailAccount,
								int(data.useEmailTp),
								data.emailTemplate)

			#return f"{len(main.toCertificate)} certificados generados"
		else:
			#print("colocando variable de sesion")
			#user = current_user_to_arg(current_user)
			#updateSessionVariable(_dict({"user_id": user.id, "json":{"credential_name":data.credentialName}}))
			session['credential_filename'] = data.credentialName
	except Exception as e:
		raise e

def validate_path_to_save(pathToSave):
	if not pathToSave:
		pathToSave = os.path.join(basedir,'pdf/'+today()+'/')
		mkdir(pathToSave)
	return pathToSave


def get_name_pdf(d, pathToSave=None):
	filename = d.email.replace(".", "_") if d.email != "" else generate_file_name(d.name)
	if pathToSave:
		while Path(pathToSave+filename+".pdf").exists():
			nameData = d.email.replace(".", "_") if d.email else d.name
			filename = generate_file_name(nameData)

	return filename




def cleanOutputs(path, extension='docx'):
	files = glob.glob(f'{path}/*.{extension}')
	for file in files:
		try:
			os.remove(file)
		except Exception as e:
			pass

def get_email_tp_data_pretty(emailTemplate):
	try:
		tpData = get_email_template_data(emailTemplate)[0]
		subject = tpData.subject
		del tpData["subject"]
		with open(os.path.join(basedir,"email_template/email_tp.html"), "r", encoding="utf-8") as f:
			body = f.read().replace("\n", "")
			for key in tpData:
				body = body.replace("{{"+key+"}}", tpData[key] or "")
		return subject, body
	
	except Exception as e:
		raise e

def get_email_template_data(name):
	return listEmailTemplate(filters={"name": name})
	

def make_addr_email(email, name=""):
	if not name or name == "":
		name = email.split("@")[0]
	r = _dict()
	r[email] = f"{name}"# <{email}>"
	return r







