from app import db
from faker import Faker
from werkzeug.security import generate_password_hash
from app.models import User , PDF , Reviewer , ReportDraft , Researcher , Project ,  Draft ,Version , Report , Comment , ReportComment
from app.modules.crypt import Crypt
from datetime import datetime, timedelta



def random_user(fake):
    max_date = datetime.now() - timedelta(days=365 * 18)
    file_path = "app/fake_user_info.txt"
    #generate 10 rows for tablee users
    try:
        user_num = User.query.count()
        if user_num < 9:
            pdfs = PDF.query.limit(9).all()
            with open(file_path, "w") as file:
                    file.truncate(0)
            for _ in range(9):
                name = fake.name()
                words = name.split()
                first_name = ' '.join(words[:-1])
                last_name = words[-1]
                type = fake.random_element(elements=("researcher", "reviewer"))
                paword = fake.password()
                if(type=="researcher"):
                    user = Researcher(
                        uid = fake.bothify(text='???????????????'),
                        username=name,
                        first_name=first_name,
                        last_name=last_name,
                        birthdate=fake.date_between(end_date=max_date),
                        email=fake.email(),
                        password_hash=generate_password_hash(paword),
                        sex=fake.random_element(elements=("M", "F", "Other")),
                        nationality=fake.country(),
                        phone=fake.bothify(text='+#########'),
                        department=fake.random_element(elements=("Economia", "Informatica e Statistica", "Umanistico","Asia e Africa Mediterranea")),
                        type=type,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                else:
                    pdf = pdfs.pop()
                    user = Reviewer(
                        uid = fake.bothify(text='????????????????'),
                        username=name,
                        first_name=first_name,
                        last_name=last_name,
                        birthdate=fake.date_between(end_date=max_date),
                        email=fake.email(),
                        password_hash=generate_password_hash(paword),
                        sex=fake.random_element(elements=("M", "F", "Other")),
                        nationality=fake.country(),
                        phone=fake.bothify(text='+#########'),
                        department=fake.random_element(elements=("Economia", "Informatica e Statistica", "Umanistico","Asia e Africa Mediterranea")),
                        type=type,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        pdf_id=pdf.id,
                    )
                db.session.add(user)
                with open(file_path, "a") as file:
                    file.write(f"uid:  {user.uid}\nusername:  {user.username}\npassw:  {paword}\nrole:  {user.type}\nphone:  {user.phone}\nemail:  {user.email}\n\n\n\n")
            db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_pdf():
    file_path = "app/links.txt"
    try:
        pdf_num = PDF.query.count()
        if pdf_num < 9:
            crypt = Crypt()
            with open(file_path, "r") as file:
                for line in file:
                    stripped_line = line.strip()
                    parts = stripped_line.split("/")
                    word = parts[-1]
                    key = crypt.generate_key()
                    encrypted = crypt.encrypt(key, stripped_line)
                    pdf = PDF(
                        id = encrypted,
                        filename = word,
                        key = key,
                    )
                    db.session.add(pdf)
            db.session.commit()

    except FileNotFoundError:
            print(f"File '{file_path}' not found.")
    except Exception as e:
            print(f"Error: {e}")


def random_project():
    try:
        res_num = Researcher.query.count()
        researchers = Researcher.query.limit(res_num).all()
        project_num = Project.query.count()
        if res_num != 0 and project_num < res_num:
            for _ in range(res_num):
                researcher = researchers.pop()
                project = Project(
                    rsid = researcher.rsid,
                )
                db.session.add(project)
            db.session.commit()
    except Exception as e:
        print(f"Error: {e}")


def random_draft(faker):
    try:
        draft_num= Draft.query.count()
        proj_num = Project.query.count()
        if draft_num < proj_num:
            for _ in range(proj_num):
                draft = Draft(
                    title = faker.text(max_nb_chars=20,ext_word_list=None),
                    description = faker.text(max_nb_chars=200, ext_word_list=None),
                )
                db.session.add(draft)
            db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_report_draft(faker):
    try:
        #check if there are enough reviewerss to make a draft
        rev_num = Reviewer.query.count()
        proj_num = Project.query.count()
        if rev_num != 0 and proj_num != 0:
            reviewers = Reviewer.query.limit(rev_num).all()
            draft_num= ReportDraft.query.count()
            proj_num = Project.query.count()
            if draft_num < proj_num:
                for _ in range(proj_num):
                    reviewer = reviewers.pop()
                    draft = ReportDraft(
                        title = faker.text(max_nb_chars=20,ext_word_list=None),
                        body = faker.text(max_nb_chars=200, ext_word_list=None),
                        rvid = reviewer.rvid,
                        pid = Project.query.first().pid,
                        status = "Submitted",
                        created_at=datetime.now(),
                    )
                    db.session.add(draft)
                    db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_version():
    try:
        draft_num= Draft.query.count()
        proj_num = Project.query.count()
        if draft_num != 0 and proj_num != 0:
            version_num= Version.query.count()
            if version_num < draft_num:
                projects = Project.query.limit(proj_num).all()
                drafts = Draft.query.limit(draft_num).all()
                for _ in range(draft_num):
                    project = projects.pop()
                    draft = drafts.pop()
                    version = Version(
                        version_number = 1,
                        project_title = draft.title,
                        project_description = draft.description,
                        project_status = "Submitted",
                        pid = project.pid,
                        draft_id = draft.did,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    db.session.add(version)
                db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_report():
    try:
        report_num= Report.query.count()
        version_num = Version.query.count()
        report_draft_num = ReportDraft.query.count()
        if report_draft_num != 0 and version_num != 0:
            if report_num < report_draft_num:
                versions = Version.query.limit(version_num).all()
                report_drafts = ReportDraft.query.limit(report_draft_num).all()
                for _ in range(report_draft_num):
                    report_draft = report_drafts.pop()
                    version = versions.pop()
                    report = Report(
                        title = report_draft.title,
                        body = report_draft.body,
                        pid = report_draft.pid,
                        rvid = report_draft.rvid,
                        vid = version.vid,
                        rdraft_id = report_draft.rdid,
                        created_at=datetime.now(),
                    )
                    db.session.add(report)
                db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_comment(faker):
    try:
        comment_num= Comment.query.count()
        user_num = User.query.count()
        project_num = Project.query.count()
        version_num = Version.query.count()
        if user_num != 0 and project_num != 0 and version_num != 0:
            if comment_num < project_num:
                users = User.query.limit(user_num).all()
                projects = Project.query.limit(project_num).all()
                for _ in range(project_num):
                    user = users.pop()
                    project = projects.pop()
                    comment = Comment(
                        body = faker.text(max_nb_chars=200, ext_word_list=None),
                        uid = user.uid,
                        pid = project.pid,
                        version_ref = 1,
                        created_at=datetime.now(),
                    )
                    db.session.add(comment)
                db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def random_report_comment(faker):
    try:
        report_comment_num= ReportComment.query.count()
        report_num = Report.query.count()
        user_num = User.query.count()
        version_num = Version.query.count()
        if report_num != 0 and user_num != 0 and version_num != 0:
            if report_comment_num < report_num:
                users = User.query.limit(user_num).all()
                reports = Report.query.limit(report_num).all()
                for _ in range(report_num):
                    user = users.pop()
                    report = reports.pop()
                    report_comment = ReportComment(
                        body = faker.text(max_nb_chars=200, ext_word_list=None),
                        uid = user.uid,
                        rid = report.rid,
                        version_ref = 1,
                        created_at=datetime.now(),
                    )
                    db.session.add(report_comment)
                db.session.commit()
    except Exception as e:
        print(f"Error: {e}")

def fake_data():
    faker = Faker()
    faker.locale = 'it_IT'
    Faker.seed(0)

    random_pdf()
    random_user(faker)
    random_project()
    random_draft(faker)
    random_report_draft(faker)
    random_version()
    random_report()
    random_comment(faker)
    random_report_comment(faker)
