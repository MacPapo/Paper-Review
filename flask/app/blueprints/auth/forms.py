import phonenumbers
from codicefiscale import isvalid
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtform_address import CountrySelectField
from app.models import User
from datetime import date, datetime
from wtforms_components import DateRange
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateField,
    RadioField,
)


class LoginUserForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Username",
            "size": "32",
        },
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Password",
            "size": "32",
        },
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In", render_kw={"class": "btn btn-primary"})


class RegistrationResearcherForm(FlaskForm):
    today = date.today()
    max_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 18), "%d/%m/%Y"
    ).date()
    min_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 100),
        "%d/%m/%Y",
    ).date()

    uid = StringField(
        "User ID",
        validators=[DataRequired(), Length(min=16, max=16)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 16,
            "placeholder": "User ID",
        },
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=6, max=32)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 32,
            "placeholder": "Username",
        },
    )
    firstname = StringField(
        "First Name",
        validators=[DataRequired(), Length(min=1, max=32)],
        render_kw={
            "placeholder": "First Name",
            "class": "shadow-sm form-control",
            "size": 32,
        },
    )
    lastname = StringField(
        "Last Name",
        validators=[DataRequired(), Length(min=1, max=64)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 64,
            "placeholder": "Last Name",
        },
    )
    birthdate = DateField(
        "Birth Date",
        validators=[DataRequired(), DateRange(max=max_date, min=min_date)],
        render_kw={"class": "shadow-sm form-control"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Email",
            "size": 64,
        },
    )
    sex = RadioField(
        "Sex",
        choices=[("M", "M"), ("F", "F"), ("Other", "Other")],
        render_kw={
            "class": "form-check-input",
        },
        validators=[DataRequired()],
    )
    nationality = CountrySelectField(
        default="IT", render_kw={"class": "shadow-sm form-control"}
    )
    phone = StringField(
        "Phone",
        validators=[DataRequired()],
        render_kw={"class": "shadow-sm form-control"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Password",
            "size": 32,
        },
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={
            "placeholder": "Repeat Password",
            "size": 32,
            "class": "shadow-sm form-control",
        },
    )
    submit = SubmitField("Register", render_kw={"class": "btn btn-primary"})

    def validate_uid(self, uid):
        if not isvalid(uid.data):
            raise ValidationError("Please use a real UID.")

        user = User.query.filter_by(uid=uid.data).first()
        if user is not None:
            raise ValidationError("UID is already registered with a different account.")

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
            raise ValidationError("Invalid phone number")


class RegistrationReviewerForm(FlaskForm):
    today = date.today()
    max_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 18), "%d/%m/%Y"
    ).date()
    min_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 100),
        "%d/%m/%Y",
    ).date()

    uid = StringField(
        "User ID",
        validators=[DataRequired(), Length(min=16, max=16)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 16,
            "placeholder": "User ID",
        },
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=6, max=32)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 32,
            "placeholder": "Username",
        },
    )
    firstname = StringField(
        "First Name",
        validators=[DataRequired(), Length(min=1, max=32)],
        render_kw={
            "placeholder": "First Name",
            "class": "shadow-sm form-control",
            "size": 32,
        },
    )
    lastname = StringField(
        "Last Name",
        validators=[DataRequired(), Length(min=1, max=64)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 64,
            "placeholder": "Last Name",
        },
    )
    birthdate = DateField(
        "Birth Date",
        validators=[DataRequired(), DateRange(max=max_date, min=min_date)],
        render_kw={"class": "shadow-sm form-control"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Email",
            "size": 64,
        },
    )
    sex = RadioField(
        "Sex",
        choices=[("M", "M"), ("F", "F"), ("Other", "Other")],
        render_kw={
            "class": "form-check-input",
        },
        validators=[DataRequired()],
    )
    nationality = CountrySelectField(
        default="IT", render_kw={"class": "shadow-sm form-control"}
    )
    phone = StringField(
        "Phone",
        validators=[DataRequired()],
        render_kw={"class": "shadow-sm form-control"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "class": "shadow-sm form-control",
            "placeholder": "Password",
            "size": 32,
        },
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={
            "placeholder": "Repeat Password",
            "size": 32,
            "class": "shadow-sm form-control",
        },
    )

    pdf = FileField(
        "Upload PDF",
        validators=[FileRequired(), FileAllowed(["pdf"], "PDF only!")],
        render_kw={
            "placeholder": "Submit a PDF of your ID Card",
            "class": "shadow-sm form-control",
        },
    )

    submit = SubmitField("Register", render_kw={"class": "btn btn-primary"})

    def validate_uid(self, uid):
        if not isvalid(uid.data):
            raise ValidationError("Please use a real UID.")

        user = User.query.filter_by(uid=uid.data).first()
        if user is not None:
            raise ValidationError("UID is already registered with a different account.")

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
            raise ValidationError("Invalid phone number")

    def validate_pdf_files(self, pdf):
        for data in pdf.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")


class EditUserForm(FlaskForm):
    today = date.today()
    max_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 18), "%d/%m/%Y"
    ).date()
    min_date = datetime.strptime(
        str(today.day) + "/" + str(today.month) + "/" + str(today.year - 100),
        "%d/%m/%Y",
    ).date()

    first_name = StringField(
        "First Name",
        validators=[DataRequired(), Length(min=1, max=32)],
        render_kw={
            "placeholder": "First Name",
            "class": "shadow-sm form-control",
            "size": 32,
        },
    )
    last_name = StringField(
        "Last Name",
        validators=[DataRequired(), Length(min=1, max=64)],
        render_kw={
            "class": "shadow-sm form-control",
            "size": 64,
            "placeholder": "Last Name",
        },
    )
    birthdate = DateField(
        "Birth Date",
        validators=[DataRequired(), DateRange(max=max_date, min=min_date)],
        render_kw={"class": "shadow-sm form-control"},
    )
    sex = RadioField(
        "Sex",
        choices=[("M", "M"), ("F", "F"), ("Other", "Other")],
        validators=[DataRequired()],
    )
    nationality = CountrySelectField(
        default="IT", render_kw={"class": "shadow-sm form-control"}
    )
    submit = SubmitField("Confirm edit", render_kw={"class": "btn btn-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different user name.")
