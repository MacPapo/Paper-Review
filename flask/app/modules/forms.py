import phonenumbers
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtform_address import CountrySelectField
from app.models import User
from datetime import date,timedelta,datetime
from wtforms_components import DateRange
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


    today = date.today()
    min_date = datetime.strptime(str(today.day) + '/'+ str(today.month) + '/'+ str(today.year - 18),'%d/%m/%Y').date()
    uid = StringField("Username", validators=[DataRequired(), Length(min=16, max=16)])
    username = StringField("User Name", validators=[DataRequired(), Length(min=6, max=32)])
    firstname = StringField("First Name", validators=[DataRequired(), Length(min=1, max=32)],render_kw={"placeholder": "First Name","class":"shadow-sm form-control"})
    lastname = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=32)])
    birthdate = DateField("Birth Date", validators=[DataRequired(),DateRange(max=min_date)],render_kw={"format": "%d/%m/%Y","class":"shadow-sm form-control"}})
    email = StringField("Email", validators=[DataRequired(), Email()])
    sex = RadioField("Sex",choices=[('M','M'),('F','F'),('Other','Other')],validators=[DataRequired()])
    nationality = CountrySelectField(default='IT')
    phone = StringField("Phone", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_uid(self, uid):
        user = User.query.filter_by(uid=uid.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different user name.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')



class UploadForm(FlaskForm):
    pdfs = MultipleFileField("PDF Files")
    submit = SubmitField("Submit")

    def validate_pdf_files(form, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")
