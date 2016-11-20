from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField,\
    DateTimeField, IntegerField, DecimalField, BooleanField, RadioField,\
    SelectField, SelectMultipleField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, IPAddress,\
    Regexp, URL, AnyOf, NoneOf, Length
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    # id = StringField('ID', validators=[DataRequired()])
    # username = StringField("Username", validators=[DataRequired(), Length(1,64)])
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    sign_in = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-Za-z]\w*')])
    password = PasswordField('Password', validators=[DataRequired(),
            EqualTo('password2', 'Password has to match.')])
    password2 = PasswordField('Confirm', validators=[DataRequired()])
    register = SubmitField('Sign Up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username has already been used.")