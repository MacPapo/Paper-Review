from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtform_address import CountrySelectField
from werkzeug.utils import secure_filename
from app.models import User
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateField,
    RadioField,
    TelField,
    MultipleFileField,
)

class LoginForm(FlaskForm):
    rsid = StringField("RSID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    uid = StringField("Username", validators=[DataRequired()])
    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name", validators=[DataRequired()])
    birthdate = DateField("Birth Date", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    sex = RadioField("Sex",choices=[('M','M'),('F','F'),('Other','Other')],validators=[DataRequired()])
    nationality = CountrySelectField(default='IT')
    phone = TelField("Phone", validators=[DataRequired()]  )
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")


class UploadForm(FlaskForm):
    pdfs = MultipleFileField("PDF Files")
    submit = SubmitField("Submit")

    def validate_pdf_files(form, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")
