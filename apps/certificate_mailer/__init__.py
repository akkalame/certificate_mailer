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
	return get_docx_templates()

def get_docx_templates():
	r = []
	for ext in (".docx", ".doc"):
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