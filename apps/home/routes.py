# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps import _dict
from apps.home import blueprint
from apps.certificate_mailer import (
	get_tokens, 
	get_cert_templates,
	get_email_accounts,
	update_cert_template
)
from apps.certificate_mailer.certificate import make_process
from apps.controllers import (
	listUsers, 
	listRoles, 
	listUserRoles, 
	asignRole, 
	getUserRolesName, 
	current_user_to_arg,
	listEmailTemplate,
	update_settings,
	listCustomFonts,
	update_user
)
from flask import render_template, request
from flask_login import (
	current_user,
	login_required
)
#from run import socketio

from jinja2 import TemplateNotFound


@blueprint.route('/index')
@login_required
def index():
	user_roles_name = getUserRolesName(current=current_user)
	data = get_data_from_segment("gencert")
	return render_template('home/gencert.html', segment='gencert', data=data, user_roles=user_roles_name)


@blueprint.route('/<template>', methods=['GET', 'POST'])
@login_required
def route_template(template):
	args = _dict(request.args) or current_user_to_arg(current_user)
	try:
		user_roles_name = getUserRolesName(current=current_user)

		if not template.endswith('.html'):
			template += '.html'

		# Detect the current page
		segment = get_segment(request)

		data = get_data_from_segment(segment, args)

		# Serve the file (if exists) from app/templates/home/FILE.html
		if request.method == 'POST':
			data_form = _dict(request.form)
			r = set_data_for_segment(segment, data_form)

		if request.method == "GET":
			r = render_template("home/" + template, segment=segment, data=data, user_roles=user_roles_name)
		
		return r
	except TemplateNotFound:
		return render_template('home/page-404.html'), 404

	except Exception as e:
		raise e
		#return render_template('home/page-500.html'), 500





# Helper - Extract current page name from request
def get_segment(request):
	try:
		segment = request.path.split('/')[-1]
		if segment == '':
			segment = 'index'
		return segment
	except:
		return None


def get_data_from_segment(segment, args=_dict()):
	if segment == "users":
		return {"users_list": listUsers()}
	elif segment == "roles":
		return {"roles": listRoles()}
	elif segment == "edit-role":
		user = listUsers({"id":int(args.user_id)})[0] or {}
		roles = listRoles()
		user_roles = listUserRoles(user_id=args.user_id)
		user_roles_id = [ur.role_id for ur in user_roles]
		for r in roles:
			r.active = False
			if r.id in user_roles_id:
				r.active = True
		return {"user": user, "user_roles": roles}
	elif segment == "gencert":
		
		data = _dict(
			credenciales=get_tokens(), 
			plantillas=get_cert_templates(),
			emailAccounts=get_email_accounts(),
			emailTemplates=listEmailTemplate(),
			
		)
		return data 
	elif segment == "settings":
		cf_list = [cf.name for cf in listCustomFonts()] or []
		return _dict(custom_fonts=cf_list)
	elif segment == "edit-cert":
		cf_list = [cf.name for cf in listCustomFonts()] or []
		return _dict(
			custom_fonts=cf_list,
			plantillas=get_cert_templates())
	
	return _dict()

def set_data_for_segment(segment, data_form):
	if segment == "edit-role":
		asignRole(data_form)
	elif segment == "gencert":
		r = make_process(data_form)
	elif segment == "edit-cert":
		return update_cert_template(data_form) or _dict()
	elif segment == "settings":
		update_settings(data_form)
	elif segment == "users":
		update_user(data_form)

	return _dict()




