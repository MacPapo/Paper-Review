from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse  # this is used to parse the url
from app import db
from app.auth import bp
from app.models import User, Researcher, UserV
from app.auth.forms import LoginUserForm, RegistrationUserForm, EditUserForm
from sqlalchemy import text, Table


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginUserForm()
    if form.validate_on_submit():
        user = UserV()
        user_data = user.search_user(form.username.data)
        # Non esiste utentecon questo  username
        if user_data is None or not user.check_password(user_data, form.password.data):
            current_app.logger.info(
                "Invalid username or password for user %s", form.username.data
            )
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        # Controllo se è un ricercatore o reviewer

        if user_data.rsid is None:
            current_app.logger.info("User %s is not a researcher", form.username.data)
            return redirect(url_for("auth.login"))
        else:
            current_app.logger.info("User %s is a researcher", form.username.data)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("main.index")
                return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationUserForm()
    if form.validate_on_submit():
        user = User(
            uid=form.uid.data,
            username=form.username.data,
            first_name=form.firstname.data,
            last_name=form.lastname.data,
            birthdate=form.birthdate.data,
            email=form.email.data,
            sex=form.sex.data,
            nationality=form.nationality.data,
            phone=form.phone.data,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        db.session.add(Researcher(rsid=user.uid))
        db.session.commit()
        create_userv()
        refresh_userv()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("auth.login"))
    return render_template("register.html", title="Register", form=form)


@bp.route("/user/<username>")
@login_required
def profile(username):
    # TODO: add a check to see if the user is a researcher or a reviewer
    user = (
        User.query.join(Researcher, User.uid == Researcher.rsid)
        .filter(User.username == username)
        .first_or_404()
    )
    user_type = "Researcher"
    return render_template(
        "profile.html", title="profile", user=user, user_type=user_type
    )


@bp.route("/user/<username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    this_user = current_user.get_this_user()
    form = EditUserForm()
    if form.validate_on_submit():
        this_user.first_name = form.first_name.data
        this_user.last_name = form.last_name.data
        this_user.birthdate = form.birthdate.data
        this_user.sex = form.sex.data
        this_user.nationality = form.nationality.data
        this_user.updated_at = datetime.now()
        db.session.commit()
        flash("Your changes have been saved.")
        refresh_userv()
        return redirect(url_for("auth.profile", username=this_user.username))
    elif request.method == "GET":
        form.first_name.data = this_user.first_name
        form.last_name.data = this_user.last_name
        form.birthdate.data = this_user.birthdate
        form.sex.data = this_user.sex
        form.nationality.data = this_user.nationality
    return render_template("edit_profile.html", title="Edit Profile", form=form)


def create_userv():
    # param query to be more safe against sql injection
    view_name = "userv"
    table1 = Table("user", db.metadata, autoload_with=db.engine, schema="public")
    table2 = Table("researcher", db.metadata, autoload_with=db.engine, schema="public")
    query = """
    CREATE  MATERIALIZED VIEW IF NOT EXISTS {view} AS
    SELECT *
    FROM public.{t1} u left join public.{t2} r on u.uid = r.rsid
    """.format(
        view=view_name, t1=table1.name, t2=table2.name
    )

    db.session.execute(text(query))
    db.session.commit()


def refresh_userv():
    # param query to be more safe against sql injection
    view_table = Table("userv", db.metadata, autoload_with=db.engine, schema="public")
    query = """
    REFRESH MATERIALIZED VIEW {view}
    """.format(
        view=view_table.name
    )

    db.session.execute(text(query))
    db.session.commit()
