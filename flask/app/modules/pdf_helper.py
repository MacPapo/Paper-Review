import os
from urllib.parse import unquote
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from app import db
from app.models import PDF
from .crypt import Crypt
from extensions import firebase

<<<<<<< HEAD
def upload_pdf(pdfs):
    # Description of the lambda function:
    # 1. secure_filename(n) returns a string of the filename with all the special characters removed.
    #    For example, if n = "hello world.pdf", then secure_filename(n) = "hello world.pdf"
    #
    # 2. Path(secure_filename(n)).stem returns the filename without the extension.
    #    For example, if n = "hello world.pdf", then Path(secure_filename(n)).stem = "hello world"
    #
    # 3. datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") returns the current date and time in the format of "-YYYY-MM-DD-HH:MM:SS"
    #    For example, if the current date and time is 2020-07-01 12:00:00, then datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") = "-2020-07-01-12:00:00"
    #
    # 4. Putting it all together, if n = "hello world.pdf", then correct_file_name(n) = "uploads/hello world-2020-07-01-12:00:00.pdf"
    #    If n = "hello world!.pdf", then correct_file_name(n) = "uploads/hello world!-2020-07-01-12:00:00.pdf"
    #
    # 5. os.path.join("uploads", Path(secure_filename(n)).stem + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") + ".pdf") returns the filename with the path.
    #    For example, if n = "hello world.pdf", then os.path.join("uploads", Path(secure_filename(n)).stem + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S") + ".pdf") = "uploads/hello world-2020-07-01-12:00:00.pdf"
    correct_file_name = lambda n: os.path.join(
        "uploads",
        Path(secure_filename(n)).stem
        + datetime.now().strftime("-%Y-%m-%d-%H:%M:%S")
        + ".pdf",
=======
import re


def upload_pdf(dir, pdfs):
    re_filename = lambda n: secure_filename(re.sub(r"[^\w\s.-]", "", n))
    correct_file_name = lambda n: os.path.join(
        dir,
        f"{Path(re_filename(n)).stem}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf",
>>>>>>> f2c6ff9fe98284cdc62dc40c20ab547a71a495d5
    )

    files = [correct_file_name(f.filename) for f in pdfs]
    [f.save(filename) for f, filename in zip(pdfs, files)]

    crypt = Crypt()
    pdf_urls = [crypt.encrypt_url(firebase.upload(filename)) for filename in files]

    name_no_folder = lambda n: os.path.basename(n)
    out = [
        PDF(id=pdf_url[0], filename=name_no_folder(files[index]), key=pdf_url[1])
        for index, pdf_url in enumerate(pdf_urls)
    ]

    [os.remove(filename) for filename in files]

    db.session.add_all(out)
    db.session.commit()
    return out


def get_pdf(pdfs):
    crypt = Crypt()
    links = []
    for pdf in pdfs:
        links.append(crypt.decrypt(pdf.key, pdf.id))

    retrive_file_name = lambda n: os.path.basename(unquote(Path(n).stem))
    names = []
    for name in links:
        names.append(retrive_file_name(name))

    return create_dictionary(links, names)


def create_dictionary(links, names):
    dictionary = {}
    for link, name in zip(links, names):
        dictionary[link] = name
    return dictionary
