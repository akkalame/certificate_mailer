from flask_login import UserMixin

from apps import db


class Roles(db.Model):

	__tablename__ = 'Roles'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	description = db.Column(db.String(300), unique=False)

	def __init__(self, **kwargs):
		for property, value in kwargs.items():
			# depending on whether value is an iterable or not, we must
			# unpack it's value (when **kwargs is request.form, some values
			# will be a 1-element list)
			if hasattr(value, '__iter__') and not isinstance(value, str):
				# the ,= unpack of a singleton fails PEP8 (travis flake8 test)
				value = value[0]

			setattr(self, property, value)

	def __repr__(self):
		return str(self.role)

class UserRoles(db.Model):

	__tablename__ = 'User Roles'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	role_id = db.Column(db.Integer)

	def __init__(self, **kwargs):
		for property, value in kwargs.items():
			# depending on whether value is an iterable or not, we must
			# unpack it's value (when **kwargs is request.form, some values
			# will be a 1-element list)
			if hasattr(value, '__iter__') and not isinstance(value, str):
				# the ,= unpack of a singleton fails PEP8 (travis flake8 test)
				value = value[0]

			setattr(self, property, value)

	def __repr__(self):
		return str([self.user_id, self.role_id])
	
class EmailAccount(db.Model):

	__tablename__ = 'Email Account'

	email = db.Column(db.String(255), primary_key=True)
	server = db.Column(db.String(255))
	password = db.Column(db.String(80))
	name = db.Column(db.String(64))

	def __init__(self, **kwargs):
		for property, value in kwargs.items():
			# depending on whether value is an iterable or not, we must
			# unpack it's value (when **kwargs is request.form, some values
			# will be a 1-element list)
			if hasattr(value, '__iter__') and not isinstance(value, str):
				# the ,= unpack of a singleton fails PEP8 (travis flake8 test)
				value = value[0]

			setattr(self, property, value)

	def __repr__(self):
		return str(self.email)

class EmailTemplate(db.Model):

	__tablename__ = 'Email Template'

	name = db.Column(db.String(80), primary_key=True)
	subject = db.Column(db.String(255))
	body = db.Column(db.String(2000))
	footer = db.Column(db.String(500))
	logo = db.Column(db.String(255))
	header = db.Column(db.String(300))
	header_color = db.Column(db.String(7))

	def __init__(self, **kwargs):
		for property, value in kwargs.items():
			# depending on whether value is an iterable or not, we must
			# unpack it's value (when **kwargs is request.form, some values
			# will be a 1-element list)
			if hasattr(value, '__iter__') and not isinstance(value, str):
				# the ,= unpack of a singleton fails PEP8 (travis flake8 test)
				value = value[0]

			setattr(self, property, value)

	def __repr__(self):
		return str(self.name)

class EmailServer(db.Model):

	__tablename__ = 'Email Server'

	server = db.Column(db.String(80), primary_key=True)
	port = db.Column(db.Integer)
	use_tls = db.Column(db.Integer)

	def __init__(self, **kwargs):
		for property, value in kwargs.items():
			# depending on whether value is an iterable or not, we must
			# unpack it's value (when **kwargs is request.form, some values
			# will be a 1-element list)
			if hasattr(value, '__iter__') and not isinstance(value, str):
				# the ,= unpack of a singleton fails PEP8 (travis flake8 test)
				value = value[0]

			setattr(self, property, value)

	def __repr__(self):
		return str(self.server)


def createRecord(arg):
	db.session.add(arg)
	db.session.commit()

def deleteRecord(arg):
	db.session.delete(arg)
	db.session.commit()