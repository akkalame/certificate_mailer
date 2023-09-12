from types import SimpleNamespace
from reportbro import Report, ReportBroError

from controller.email_controller import send_gmail
from controller.oauth_login import Service
from utils import _, today, mkdir
import utils, json, glob, os, random, base64

from flask import url_for


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
			#if len(row) >= 12:
			#	if row[11] == "CE": continue

			obj = SimpleNamespace()
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
		r = []
		for d in data:
			if d.faltas >= faltaMax and faltaMax > 0:
				continue
			r.append(d)
		self.toCertificate = r

	def generate_cert(self, templatePath, pathToSave=None):
		with open(templatePath, 'r') as f:
			reportDefinition = json.loads(f.read())

		additionalFonts = get_additional_fonts()
		#data = [{"name":"Isabela oliveira", "email":"devakkalame@gmail.com"}, {"name":"Pedro Oliveira","email":""}]
		for d in self.toCertificate:
			reportData = vars(d)
			reportData["name"] = reportData["name"].lower().title()
			report = Report(report_definition=reportDefinition, data=reportData, 
				additional_fonts=additionalFonts)
			report_file = report.generate_pdf()

			namePdf = d.email if d.email != "" else generate_file_name(d.name)
			if not pathToSave:
				pathToSave = './pdf/'+today+'/'
				mkdir(pathToSave)
			filePath = pathToSave+namePdf+'.pdf'

			with open(filePath, 'wb') as f:
				f.write(report_file)

			if d.email != "":
				dCopy = d
				dCopy.file = filePath
				self.toSend.append(dCopy)

	def send_emails(self, subject, body):
		gmail = self.service.gmail()
		for d in self.toSend:
			send_gmail(gmail, '',d.email,subject,body,filePath=[d.file])
		
		return f"{len(self.toSend)} emails enviados"

def make_process(tokenName,spreadLink,cell1,cell2,faltaMax,subject,body, templatePath, sendEmail):
	main = Main()
	main.connect_to_google(tokenName)
	sheetId = utils.sheet_id_from_link(spreadLink)
	rangeName = f"{cell1.upper()}:{cell2.upper()}"
	rows = main.get_sheet_values(sheetId, rangeName)



	data = main.rows_to_obj(rows, int(cell1[1:]))
	main.availables_to_certificate(data, faltaMax)
	main.generate_cert(templatePath)
	if sendEmail:
		return main.send_emails(subject, body)

	return f"{len(main.toCertificate)} certificados generados"

def save_template(str64, nameFile=""):
	if nameFile == "":
		nameFile = generate_code(10)

	strRB = base64.b64decode(str64)
	with open("./cert_template/"+nameFile+".json", "w") as f:
		f.write(strRB.decode("utf-8"))

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
		r.append(dict(path=f, name=name))
	return r

def get_rb_templates():
	paths = glob.glob(f'./cert_template/*.json')
	r = []
	for f in paths:
		name = os.path.basename(f).split(".")[0]
		r.append(dict(path=f, name=name))
	return r

def load_rb_template(path):
	with open(path, "r") as f:
		d = f.read()
		#print(d)
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

if __name__ == "__main__":
	pass
	#main = Main()
	#main.connect_to_google()
	#sheetId = utils.sheet_id_from_link("https://docs.google.com/spreadsheets/d/1s7M9GnHU2nK5fNvGcWkS_G2Z_4imIXxhvrdnZdHtMrM/edit#gid=186001220")
	#rangeName = utils.format_sheet_range_name('A', 4, 'M', 5)
	#rows = main.get_sheet_values(sheetId, rangeName)
	#data = main.rows_to_obj(rows, 4)
	#main.availables_to_certificate(data, 1)
	#main.generate_cert()
	#main.send_emails()
	#get_additional_fonts()
	#print('\n',filteredData)


