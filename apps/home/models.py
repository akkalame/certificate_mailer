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

class CustomFonts(db.Model):

	__tablename__ = 'Custom Fonts'

	name = db.Column(db.String(80), primary_key=True)
	url = db.Column(db.String(255))

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

class Student(db.Model):

	__tablename__ = 'Student'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=False)
	dni = db.Column(db.String(50))
	email = db.Column(db.String(255), unique=True)
	code = db.Column(db.String(10), unique=True)

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
		return str(f"{self.role}, {self.dni}")

class Matter(db.Model):

	__tablename__ = 'Matter'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=True)

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

class MatterModule(db.Model):

	__tablename__ = 'Matter Module'

	id = db.Column(db.Integer, primary_key=True)
	matter_id = db.Column(db.Integer)
	name = db.Column(db.String(30))

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

class Teacher(db.Model):

	__tablename__ = 'Teacher'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(150), unique=False)
	email = db.Column(db.String(255), unique=True)

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
		return str(f"{self.name}, {self.email}")

class Course(db.Model):

	__tablename__ = 'Course'

	id = db.Column(db.Integer, primary_key=True)
	matter_id = db.Column(db.Integer, primary_key=False)
	module_id = db.Column(db.Integer, primary_key=False)
	teacher_id = db.Column(db.Integer, primary_key=False)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)

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
		return str(f"{self.role}, {self.dni}")

class AttendanceList(db.Model):

	__tablename__ = 'Attendance List'

	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer)
	student_id = db.Column(db.Integer)
	status = db.Column(db.String(30))

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
		return str(self.id)

class SessionVariable(db.Model):

	__tablename__ = 'Session Variable'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	json = db.Column(db.String(1000))

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
		return str(self.variables)

def createRecord(arg):
	try:
		db.session.add(arg)
		db.session.commit()
	except Exception as e:
		return e

def deleteRecord(arg):
	db.session.delete(arg)
	db.session.commit()

def updateRecord(arg):
	pass