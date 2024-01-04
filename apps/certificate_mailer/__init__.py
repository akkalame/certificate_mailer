import json, glob, os, random, base64
from apps import _dict
from apps.controllers import listEmailAccount

basedir = os.path.abspath(os.path.dirname(__file__))

def get_tokens():
	paths = glob.glob(os.path.join(basedir, 'tokens/*.json'))
	r = []
	for f in paths:
		name = os.path.basename(f).split(".")[0]
		r.append(_dict(name=name))
	return r

def get_cert_templates():
	return get_html_templates()

def get_docx_templates():
	r = []
	for ext in (".docx", ".doc"):
		paths = glob.glob(os.path.join(basedir,f'cert_template/*{ext}'))
		for f in paths:
			basename = os.path.basename(f)
			name = basename.split(".")[0]
			r.append(_dict(name=name))
	return r

def get_html_templates():
	r = []
	for ext in (".html"):
		paths = glob.glob(os.path.join(basedir,f'cert_template/*{ext}'))
		for f in paths:
			basename = os.path.basename(f)
			name = basename.split(".")[0]
			r.append(_dict(name=name))
	return r

def get_email_accounts():
	query = listEmailAccount()
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

def build_cert_template(data):
	with open(os.path.join(basedir, f"cert_template/{data.name}.html"), "w", encoding="utf-8") as f:
		f.write(data.content)

def get_content_html_template(data):
	with open(os.path.join(basedir, f"cert_template/{data.name}.html"), "r", encoding="utf-8") as f:
		return f.read()

def update_cert_template(data_form):
	type_request = data_form.type_request
	del data_form['type_request']
	if type_request == "save_template":
		build_cert_template(data_form)
	elif type_request == "get_template":
		return _dict(tpl_content=get_content_html_template(data_form))
	elif type_request == "delete_template":
		path = os.path.join(basedir, f"cert_template/{data_form.name}.html")
		os.remove(path)


