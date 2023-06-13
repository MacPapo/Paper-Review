from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField, SelectField, RadioField


class UploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    pdfs = MultipleFileField("PDF Files")
    submit = SubmitField("Submit")

    def validate_pdf_files(self, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")


class ReportForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=256)])
    body = TextAreaField("Body", validators=[DataRequired(), Length(min=1, max=4096)])
    report = SelectField("Report",validators=[DataRequired()])
    status = RadioField("Status", choices=[("Requires changes","Requires changes"),("Approved", "Approved"), ("Not Approved", "Not Approved")], default="Need Changes",validators=[DataRequired()])
    pdf = MultipleFileField("PDF Files")
    submit = SubmitField("Confirm", render_kw={"class": "btn btn-primary"})

    def validate_pdf_files(self, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are  allowed.")
            

class AddCommentForm(FlaskForm):
    body = StringField("Title", validators=[DataRequired(), Length(min=1, max=256)])
    submit = SubmitField("Confirm", render_kw={"class": "btn btn-primary"})
