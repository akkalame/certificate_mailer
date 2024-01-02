from apps.authentication.models import Users
from apps.home.models import (
	Roles,
	UserRoles,
	createRecord, 
	deleteRecord, 
	EmailAccount, 
	EmailTemplate,
	EmailServer
	)
from apps import list2_dict, db
from sqlalchemy import column


def listUsers(filters={}):
	if filters:
		query = db.session.query(Users).filter_by(**filters).with_entities(Users.id, Users.username, Users.email).all()
	else:
		query = db.session.query(Users).with_entities(Users.id, Users.username, Users.email).all()
	return list2_dict(query, ["id","username", "email"])

def listRoles():
	query = db.session.query(Roles).with_entities(Roles.id, Roles.name, Roles.description).all()
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


