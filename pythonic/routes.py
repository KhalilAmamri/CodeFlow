import secrets
from PIL import Image
import os
from flask_login import login_user, current_user, logout_user, login_required
from pythonic.models import User, Lesson, Course
from flask import render_template, url_for, flash, redirect, request, session
from pythonic.forms import NewCourseForm, NewLessonForm, RegistrationForm, LoginForm, UpdateProfileForm
from pythonic import app, db, bcrypt
from flask_modals import Modal, render_template_modal


lessons = [
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
    {
        "title": "Request Library Course",
        "course": "Python",
        "author": "Omar",
        "thumbnail": "thumbnail.jpg",
    },
]
courses = [
    {
        "name": "Python",
        "icon": "python.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Data Analysis",
        "icon": "analysis.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Machine Learning",
        "icon": "machine-learning.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Web Design",
        "icon": "web.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Blockchain",
        "icon": "blockchain.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
    {
        "name": "Tips & Tricks",
        "icon": "idea.png",
        "description": "Lorem ipsum dolor sit amet consectetur adipisicing elit. Neque quidem nihil dolor officiis at magni!",
    },
]

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/user_pics', picture_name)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_name
@app.route("/")
def home():
    return render_template("home.html", lessons=lessons, courses=courses)


@app.route("/about")
def about():
    return render_template("about.html", title="About Page")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()

        flash(
            f"Account created for {form.first_name.data} {form.last_name.data}!",
            "success",
        )
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash("Login successful!", "success")
                return redirect(next_page) if next_page else redirect(url_for("home"))
            else:
                flash("Login Unsuccessful. Please check email and password", "danger")
            
    return render_template("login.html", title="Login", form=form)
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard", active_tab='None')

@app.route("/dashboard/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = UpdateProfileForm()
    if profile_form.validate_on_submit():
        if profile_form.picture.data:
            picture_file = save_picture(profile_form.picture.data)
            current_user.image_file = picture_file
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash("Your profile has been updated", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        profile_form.bio.data = current_user.bio
    image_file = url_for("static", filename=f"user_pics/{current_user.image_file}")
    return render_template(
        "profile.html",
        title="Profile",
        profile_form=profile_form,
        image_file=image_file,
        active_tab="profile",
    )
@app.route("/dashboard/new_lesson", methods=["GET", "POST"])
@login_required
def new_lesson():
    new_lesson_form = NewLessonForm()
    if new_lesson_form.validate_on_submit():
        course = new_lesson_form.course.data
        lesson = Lesson(
            title=new_lesson_form.title.data,
            content=new_lesson_form.content.data, 
            slug=new_lesson_form.slug.data, 
            author=current_user, course_name=course
        )
        db.session.add(lesson)
        db.session.commit()
        
        flash("Your lesson has been created!", "success")
        return redirect(url_for("dashboard"))
    
    modals = Modal().load
    return render_template_modal(
        "new_lesson.html", title="New Lesson",
        new_lesson_form=new_lesson_form, 
        active_tab='new_lesson',
        modals=modals
    )

@app.route("/dashboard/new_course", methods=["GET", "POST"])
@login_required
def new_course():
    new_course_form = NewCourseForm()
    if new_course_form.validate_on_submit():
        icon_file = 'default_icon.png'  # Default icon
        if new_course_form.icon.data:
            icon_file = save_picture(new_course_form.icon.data)
        
        course = Course(
            title=new_course_form.title.data,
            description=new_course_form.description.data,
            icon=icon_file
        )
        db.session.add(course)
        db.session.commit()
        flash("Your course has been created!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("new_course.html", title="New Course", new_course_form=new_course_form, active_tab='new_course')