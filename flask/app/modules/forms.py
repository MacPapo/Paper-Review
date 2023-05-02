import phonenumbers
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtform_address import CountrySelectField
from app.models import User
from datetime import date,datetime
from wtforms_components import DateRange
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateField,
    RadioField,
    MultipleFileField,
)

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()],
                           render_kw={"class":"shadow-sm form-control","placeholder":"Username","size":"32"})
    password = PasswordField("Password", validators=[DataRequired()],
                           render_kw={"class":"shadow-sm form-control","placeholder":"Password","size":"32"})
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In",render_kw={"class":"btn btn-primary"})


class RegistrationForm(FlaskForm):
    today = date.today()
    max_date = datetime.strptime(str(today.day) + '/'+ str(today.month) + '/'+ str(today.year - 18),'%d/%m/%Y').date()
    min_date = datetime.strptime(str(today.day) + '/'+ str(today.month) + '/'+ str(today.year - 100),'%d/%m/%Y').date()
    uid = StringField("Username", validators=[DataRequired(), Length(min=16, max=16)],
                      render_kw={"class":"shadow-sm form-control","size":16,"placeholder":"User ID"})
    username = StringField("User Name", validators=[DataRequired(), Length(min=6, max=32)],
                      render_kw={"class":"shadow-sm form-control","size":32,"placeholder":"Username"})
    firstname = StringField("First Name", validators=[DataRequired(), Length(min=1, max=32)],
                      render_kw={"placeholder": "First Name","class":"shadow-sm form-control","size":32})
    lastname = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=64)],
                      render_kw={"class":"shadow-sm form-control","size":64,"placeholder":"Last Name"})
    birthdate = DateField("Birth Date",validators=[DataRequired(),DateRange(max=max_date,min=min_date)],
                      render_kw={"class":"shadow-sm form-control"})
    email = StringField("Email", validators=[DataRequired(), Email()],
                      render_kw={"class":"shadow-sm form-control","placeholder":"Email","size":64})
    sex = RadioField("Sex",choices=[('M','M'),('F','F'),('Other','Other')],validators=[DataRequired()]
                      )
    nationality = CountrySelectField(default='IT',
                      render_kw={"class":"shadow-sm form-control"})
    phone = StringField("Phone", validators=[DataRequired()],
                      render_kw={"class":"shadow-sm form-control"})
    password = PasswordField("Password", validators=[DataRequired()],
                      render_kw={"class":"shadow-sm form-control","placeholder":"Password","size":32})
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")],
                      render_kw={"placeholder":"Repeat Password","size":32,"class":"shadow-sm form-control"})
    submit = SubmitField("Register",render_kw={"class":"btn btn-primary"})

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
