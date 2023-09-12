from flask import Flask, jsonify, render_template, request, Markup
from main import get_tokens
from main import make_process, save_template, get_rb_templates, load_rb_template, load_custom_fonts
from utils import open_container_folder

app = Flask(__name__)

app.jinja_env.globals.update(load_custom_fonts=load_custom_fonts)

@app.route('/')
def index():
	return render_template('index.html', credenciales=get_tokens(), plantillas=get_rb_templates())

@app.route('/generate', methods=["POST"])
def generate():
	data = request.form

	r = make_process(tokenName=data["credentialName"],
		spreadLink=data["spreadLink"],
		cell1=data["cell1"],
		cell2=data["cell2"],
		faltaMax=int(data["faltaMax"]),
		subject=data["subject"],
		body=data["body"],
		templatePath=data["templatePath"],
		sendEmail=data["sendEmail"])

	return jsonify({"response":r})
	#return render_template('index.html', credenciales=get_tokens())


@app.route('/designer')
def designer():
	custom_font = load_custom_fonts()
	return render_template('reportbro_designer.html', plantillas=get_rb_templates(),
    	custom_fonts_css=Markup(custom_font['css']), json_cf=custom_font['json'])

@app.route('/open_container_folder')
def openContainerFolder():
	open_container_folder()
	return "True"

@app.route('/save_rb_template', methods=["POST"])
def save_rb_template():
    save_template(request.form["reportDefinition"], request.form["nameFile"])
    return "guardado"

@app.route('/load_template', methods=["POST"])
def load_template():
	response = load_rb_template(request.form["path"])
	return jsonify(dict(response=response))

if __name__ == "__main__":
	#load_custom_fonts()
	app.run(debug=True, host="0.0.0.0")