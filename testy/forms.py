from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from testy.models import User

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class RegisterForm(FlaskForm):

    def ValidateUsername(self, usernameToCheck):
        user = User.query.filter_by(username=usernameToCheck.data).first()
        if user:
            raise ValidationError('Username already exists!')

    def ValidateEmailAddress(self, emailToCheck):
        emailAddress = User.query.filter_by(email=emailToCheck.data).first()
        if emailAddress:
            raise ValidationError('Email Address already exists!')

    username = StringField(label="User name", validators=[Length(min=2, max=30), DataRequired()])
    emailAddress = StringField(label=" Email address:", validators=[Email(),DataRequired()])
    password1 = PasswordField(label = "Password", validators=[Length(min=8),DataRequired()])
    password2 = PasswordField(label = "Confirm Password", validators=[EqualTo("password1"),DataRequired()])
    submit = SubmitField(label = "Create Account")