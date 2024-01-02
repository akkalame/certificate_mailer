from apps.certificate_mailer import utils
from apps.certificate_mailer.googlecon import Service
from apps.certificate_mailer.utils import today, mkdir
from apps.certificate_mailer.email_controller import send_smtp, smtp_service
from apps import _dict
from apps.controllers import listEmailTemplate, listEmailAccount, listEmailServer
import json, glob, os, random, base64
from pathlib import Path
from urllib.parse import unquote
from docxtpl import DocxTemplate
from docx2pdf import convert
import pythoncom


basedir = os.path.abspath(os.path.dirname(__file__))

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
		tp = os.path.join(basedir,"cert_template/"+templatePath)
		if Path(tp+".docx").exists():
			tp = tp + ".docx"
		else:
			return 

		pathToSave = validate_path_to_save(pathToSave)

		self.gen_by_docx(tp, pathToSave)

	def gen_by_docx(self, tp, pathToSave=None):
		
		for idx, d in enumerate(self.toCertificate):
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
	"""
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
	"""
	def send_emails(self, subject="", body="", emailAccount="", sendViaGoogle=False, useEmailTp=False, emailTemplate=""):
		
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
					emailsSent.append(d.email)
				except Exception as e:
					emailsUnsent.append(d.email)

		return f"{sents} e-mails enviados"

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