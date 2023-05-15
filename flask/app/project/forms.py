from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired
from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField


class UploadForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    pdfs = MultipleFileField("PDF Files")
    submit = SubmitField("Submit")

    def validate_pdf_files(self, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")

class AddNoteForm(FlaskForm):
    newpdfs = MultipleFileField("PDF Files",validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_pdf_files(self, field):
        for data in field.data:
            if not data.filename.endswith(".pdf"):
                raise ValidationError("Only PDFs are allowed.")
