from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

class CreateRoleForm(FlaskForm):
    role = StringField('Role',
                         id='role_create',
                         validators=[DataRequired()])
    description = StringField('Description',
                      id='description_role_create',
                      validators=[])