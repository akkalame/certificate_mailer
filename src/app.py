from flask import Flask, jsonify, render_template, request
from markupsafe import Markup

from kernel import _dict, get_config, _
from main import (
	make_process, 
	save_template, 
	get_cert_templates, 
	load_rb_template, 
	load_custom_fonts,
	get_tokens,
	get_mail_servers,
	get_email_accounts,
	update_settings,
	delete_settings,
	get_languages,
	get_rb_templates,
	get_email_templates,
	update_email_tp,
	get_email_template_data
	)
from utils import open_container_folder, get_port, open_browser



app = Flask(__name__)

app.jinja_env.globals.update(load_custom_fonts=load_custom_fonts)

#  main pages
@app.route('/')
def index():
	return render_template('index.html', credenciales=get_tokens(), 
		plantillas=get_cert_templates(),
		emailAccounts=get_email_accounts(),
		emailTemplates=get_email_templates()
		)


@app.route('/designer')
def designer():
	custom_font = load_custom_fonts()
	return render_template('reportbro_designer.html', plantillas=get_rb_templates(),
		custom_fonts_css=Markup(custom_font['css']), json_cf=custom_font['json'])

@app.route('/editor-email', methods=["GET", "POST", "DELETE"])
def editor_email():
	if request.method == 'GET':
		plantillas = get_email_templates()
		return render_template('email_tp_editor.html', plantillas=plantillas)
	else:
		data = _dict(request.form) 
		print(data)
		if request.method == 'POST':
			
			result = _dict(type="")
			if data.get("type"):
				result.type = "data"
				result.data = get_email_template_data(data.name)
			else:
				result.type = "msg"
				result.data = update_email_tp(data)

		return jsonify(result)
	

@app.route('/settings', methods=["GET", "POST", "DELETE"])
def settings():
	if request.method == 'GET':
		return render_template('settings.html', servers=get_mail_servers(),
			emailAccounts=get_email_accounts(), languages=get_languages())
	else:
		data = _dict(request.form) 
		if request.method == 'POST':
			result = update_settings(data)
		elif request.method == 'DELETE':
			result = delete_settings(data)

		return jsonify({"msg":result})
		

###



@app.route('/generate', methods=["POST"])
def generate():
	data = _dict(request.form)
	r = make_process(data)

	return jsonify({"response":r})



@app.route('/open_container_folder')
def openContainerFolder():
	open_container_folder()
	return "True"

@app.route('/save_rb_template', methods=["POST"])
def save_rb_template():
	print(request.form)
	save_template(request.form["reportDefinition"], request.form["nameFile"])
	return "guardado"

@app.route('/load_template', methods=["POST"])
def load_template():
	response = load_rb_template(request.form["path"])
	return jsonify(dict(response=response))

if __name__ == "__main__":
	debug = get_config().debug or False
	port = get_port()
	if not debug:
		open_browser(f"http://127.0.0.1:{port}")
	app.run(debug=debug, host="0.0.0.0", port=port)
