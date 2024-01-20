from apps.authentication.models import Users, GoogleOAuthToken
from apps.home.models import (
	Roles,
	UserRoles,
	createRecord, 
	deleteRecord, 
	EmailAccount, 
	EmailTemplate,
	EmailServer,
	CustomFonts
	)
from apps import list2_dict, db, _dict
from sqlalchemy import column
from apps import socket_io_events as ioe
from apps.controllers.builds import build_custom_fonts

def listUsers(filters={}):
	if filters:
		query = db.session.query(Users).filter_by(**filters).with_entities(Users.id, Users.username, Users.email).all()
	else:
		query = db.session.query(Users).with_entities(Users.id, Users.username, Users.email).all()
	return list2_dict(query, ["id","username", "email"])

def listRoles(filters={}):
	query = db.session.query(Roles)
	if filters:
		query.filter_by(**filters)
	
	query = query.with_entities(Roles.id, Roles.name, Roles.description).all()
	return list2_dict(query, ["id","name", "description"])

def listUserRoles(user_id=None, role_id=None):
	
	if user_id:
		query = db.session.query(UserRoles).filter_by(user_id=int(user_id)).with_entities(UserRoles.id, UserRoles.user_id, UserRoles.role_id).all()
	elif role_id:
		query = db.session.query(UserRoles).filter_by(role_id=int(role_id)).with_entities(UserRoles.id, UserRoles.user_id, UserRoles.role_id).all()
	else:
		query = db.session.query(UserRoles).with_entities(UserRoles.id, UserRoles.user_id, UserRoles.role_id).all()
	
	return list2_dict(query, ["id","user_id", "role_id"])

def listEmailAccount(filters={}):
	if filters:
		query = db.session.query(EmailAccount).filter_by(**filters).with_entities(EmailAccount.email, EmailAccount.server, EmailAccount.password, EmailAccount.name).all()
	else:
		query = db.session.query(EmailAccount).with_entities(EmailAccount.email, EmailAccount.server, EmailAccount.password, EmailAccount.name).all()
	
	return list2_dict(query, ["email","server", "password", "name"])

def listEmailTemplate(filters={}):
	query = db.session.query(EmailTemplate)
	if filters:
		query.filter_by(**filters)

	query = query.with_entities(
		EmailTemplate.name, 
		EmailTemplate.subject,
		EmailTemplate.body,
		EmailTemplate.footer,
		EmailTemplate.logo,
		EmailTemplate.header,
		EmailTemplate.header_color
	)
	return list2_dict(query, ["name",
		"subject",
		"body",
		"footer",
		"logo",
		"header",
		"header_color"
	])

def listEmailServer(filters={}):
	query = db.session.query(EmailServer)
	if filters:
		query.filter_by(**filters)

	query = query.with_entities(
		EmailServer.server, 
		EmailServer.port,
		EmailServer.use_tls
	)
	return list2_dict(query, ["server",
		"port",
		"use_tls",
	])

def listCustomFonts(filters={}):
	query = db.session.query(CustomFonts)
	if filters:
		query.filter_by(**filters)

	query = query.with_entities(
		CustomFonts.name, 
		CustomFonts.url,
	)
	return list2_dict(query, ["name", "url"])

def listGoogleTokens(filters=_dict(), raw=False):
	qb = db.session.query(GoogleOAuthToken)
	if filters:
		qb.filter_by(**filters)
	
	query = qb.with_entities(
		GoogleOAuthToken.user_id, 
		GoogleOAuthToken.name, 
		GoogleOAuthToken.token,
		GoogleOAuthToken.refresh_token,
		GoogleOAuthToken.token_uri,
		GoogleOAuthToken.client_id,
		GoogleOAuthToken.client_secret,
		GoogleOAuthToken.scopes,
		GoogleOAuthToken.expiry
		).all()
	
	if raw:
		return query

	print("query", query)
	result = list2_dict(query, [
		"user_id", "name", "token",
		"refresh_token","token_uri","client_id",
		"client_secret","scopes","expiry",])
	for r in result:
		r.scopes = r.scopes.split(",")
	
	print("\nresult",result)
	if filters:
		return strictFilter(result, _dict(filters))

	return result


def asignRole(data_form):
	checked = int(data_form.checked)
	del data_form['checked']
	user_role = UserRoles(**data_form)
	if checked:
		createRecord(user_role)
	else:
		record = db.session.query(UserRoles).filter_by(**data_form).first()
		deleteRecord(record)

def getUserRolesName(current=None, user_id=None):
	roles_name = []
	if current:
		if hasattr(current, "username"):
			user = listUsers(filters={"username": current.username})
			user_id = user[0].id or None
	if user_id:
		user_roles = listUserRoles(user_id=user_id)
		user_roles_id = [ur.role_id for ur in user_roles]
		roles = listRoles()
		roles_name = [r.name for r in roles if r.id in user_roles_id]

	return roles_name

def current_user_to_arg(current):
	if hasattr(current, "username"):
		user = listUsers(filters={"username": current.username})[0]
		user.user_id = user.id
		return user
	
	return {}

def updateGOAT(data):
	data.scopes = ",".join(data.scopes)
	user_tokens = listGoogleTokens({"user_id": data.user_id, "client_id": data.client_id})
	# in case token link not exist with current user, check if link exist with another user
	if not user_tokens:
		if listGoogleTokens({"client_id": data.client_id}):
			return "La cuenta google que intenta vincular ya se encuentra en uso con otro usuario."

	if user_tokens:
		record = listGoogleTokens({"user_id": data.user_id, "client_id": data.client_id}, raw=True)[0]
		record.token = data.token
		record.token_uri = data.token_uri
		record.client_secret = data.client_secret
		record.scopes = data.scopes
		record.expiry = data.expiry
		if data.get("refresh_token"):
			record.refresh_token = data.refresh_token
		db.session.commit()
	else:
		obj = GoogleOAuthToken(**data)
		createRecord(obj)


def update_settings(data_form):
	type_request = data_form.type_request
	del data_form['type_request']

	if type_request == "add_custom_font":
		op = CustomFonts(**data_form)
		result = createRecord(op)
		if not result:
			ioe.show_alert("Registro Exitoso")
			build_custom_fonts(listCustomFonts())
	elif type_request == "del_custom_font":
		record = db.session.query(CustomFonts).filter_by(**data_form).first()
		deleteRecord(record)
		build_custom_fonts(listCustomFonts())

def update_user(data_form):
	type_request = data_form.type_request
	del data_form['type_request']

	if type_request == "delete_user":
		record = db.session.query(Users).filter_by(**data_form).first()
		deleteRecord(record)

def strictFilter(data: list, filters: _dict):
	r = []
	print("filters", filters)
	for d in data:
		valid = True
		for k, v in filters.items():
			print(k,":",v)
			print(d[k])
			if d[k] != v:
				valid = False
				break
		if valid:
			r.append(d)
	return r