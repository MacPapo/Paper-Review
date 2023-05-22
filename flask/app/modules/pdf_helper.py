import os
from urllib.parse import unquote
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from app import db, firebase
from app.models import PDF
from .crypt import Crypt

import re


def upload_pdf(dir, pdfs):
    re_filename = lambda n: secure_filename(re.sub(r"[^\w\s.-]", "", n))
    correct_file_name = lambda n: os.path.join(
        dir,
        f"{Path(re_filename(n)).stem}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.pdf",
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


def get_all_pdfs(pdfs):
    links = []
    for pdf in pdfs:
        links.append(get_link(pdf.key, pdf.id))

    retrive_file_name = lambda n: os.path.basename(unquote(Path(n).stem))
    names = []
    for name in links:
        names.append(retrive_file_name(name))

    return create_dictionary(links, names)


def get_link(key, id):
    crypt = Crypt()
    return crypt.decrypt(key, id)


def create_dictionary(links, names):
    dictionary = {}
    for link, name in zip(links, names):
        dictionary[link] = name
    return dictionary


def download_pdf(name):
    return firebase.download(name)
