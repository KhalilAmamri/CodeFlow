# Standard library imports for security, image processing, and file operations
import secrets
from PIL import Image
import os

# Flask-Login imports for user authentication and session management
from flask_login import login_user, current_user, logout_user, login_required

# Local model imports for database entities
from pythonic.models import User, Lesson, Course

# Flask core imports for web framework functionality
from flask import render_template, url_for, flash, redirect, request, session, abort, jsonify

# Local form imports for user input validation and processing
from pythonic.forms import NewCourseForm, NewLessonForm, RegistrationForm, LoginForm, UpdateProfileForm, LessonUpdateForm

# Local application imports for database, encryption, and app instance
from pythonic import app, db, bcrypt

# Flask-Modals imports for dynamic modal functionality
from flask_modals import Modal, render_template_modal


def save_picture(form_picture, path, output_size=None):
    """
    Save uploaded image file with optional resizing.
    
    Args:
        form_picture: FileStorage object from form
        path (str): Directory path to save the image
        output_size (tuple, optional): Target dimensions (width, height) for resizing
    
    Returns:
        str: Generated filename of the saved image
    
    This function generates a unique filename using cryptographic randomness,
    processes the image with PIL if resizing is requested, and saves it
    to the specified directory path.
    """
    # Generate cryptographically secure random hex for unique filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    
    # Construct full file path within application directory
    picture_path = os.path.join(app.root_path, path, picture_name)
    
    # Open and process image with PIL
    i = Image.open(form_picture)
    if output_size:   
        i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_name


# TinyMCE image upload endpoint
ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    image = request.files.get('file')  # TinyMCE sends field name 'file'
    if not image or not image.filename:
        return jsonify({'error': 'No file'}), 400

    # Validate extension
    _, ext = os.path.splitext(image.filename)
    ext = ext.lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        return jsonify({'error': 'Invalid type'}), 400

    # Ensure upload directory exists
    upload_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate safe unique name and save
    random_hex = secrets.token_hex(16)
    filename = f"{random_hex}{ext}"
    save_path = os.path.join(upload_dir, filename)
    image.save(save_path)

    file_url = url_for('static', filename=f'uploads/{filename}')
    # TinyMCE expects { location: 'url' }
    return jsonify({'location': file_url})


def delete_picture(picture_name, path):
    """
    Delete an image file from the specified directory.
    
    Args:
        picture_name (str): Name of the file to delete
        path (str): Directory path where the file is located
    
    This function safely removes old image files when they are replaced,
    helping to manage storage space and prevent file accumulation.
    """
    if picture_name and picture_name not in ['default_thumbnail.jpg', 'default_icon.png']:
        try:
            picture_path = os.path.join(app.root_path, path, picture_name)
            if os.path.exists(picture_path):
                os.remove(picture_path)
        except Exception as e:
            # Log error but don't crash the application
            print(f"Error deleting picture {picture_name}: {e}")


def fet_previous_next_lesson(lesson_slug, course_slug):
    """
    Retrieve previous and next lessons within a course for navigation.
    
    Args:
        lesson_slug (str): Current lesson's slug identifier
        course_slug (str): Course slug for context
    
    Returns:
        tuple: (previous_lesson, next_lesson) - Lesson objects or None
    
    This function enables lesson-to-lesson navigation within a course,
    providing previous/next buttons for improved user experience.
    """
    # Get the course first
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    
    # Get all lessons in the course ordered by date
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.date_posted.asc()).all()
    
    # Find the current lesson index
    current_index = None
    for i, lesson in enumerate(lessons):
        if lesson.slug == lesson_slug:
            current_index = i
            break
    
    # Get previous and next lessons
    previous_lesson = lessons[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index is not None and current_index < len(lessons) - 1 else None
    
    return previous_lesson, next_lesson


# ============================================================================
# MAIN APPLICATION ROUTES
# ============================================================================

@app.route("/")
def index():
    """
    Root route handler - redirects to home page.
    
    Returns:
        Response: Redirect to home page for better URL structure.
    """
    return redirect(url_for("home"))


@app.route("/home")
def home():
    """
    Home page route - displays latest lessons and courses.
    
    Returns:
        str: Rendered home.html template with lessons and courses data.
    
    This route fetches the most recent lessons and courses from the database,
    ordered by publication date, and displays them on the main landing page.
    """
    lessons = Lesson.query.order_by(Lesson.date_posted.desc()).all()
    courses = Course.query.order_by(Course.date_posted.desc()).all()
    return render_template("home.html", lessons=lessons, courses=courses)


@app.route("/about")
def about():
    """
    About page route - displays application information.
    
    Returns:
        str: Rendered about.html template with page title.
    """
    return render_template("about.html", title="About Page")


# ============================================================================
# USER AUTHENTICATION ROUTES
# ============================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration route - handles new account creation.
    
    Methods:
        GET: Display registration form
        POST: Process form submission and create user account
    
    Returns:
        str: Rendered template or redirect response.
    
    This route validates user input, hashes passwords securely using bcrypt,
    creates new user records, and provides appropriate feedback messages.
    """
    # Redirect authenticated users to home page
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Hash password using bcrypt for secure storage
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        
        # Create new user instance with form data
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
        )
        
        # Persist user to database
        db.session.add(user)
        db.session.commit()

        # Provide success feedback and redirect to login
        flash(f"Account created for {form.first_name.data} {form.last_name.data}!", "success")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User login route - handles user authentication.
    
    Methods:
        GET: Display login form
        POST: Validate credentials and establish user session
    
    Returns:
        str: Rendered template or redirect response.
    
    This route verifies user credentials against the database, creates
    authenticated sessions, and handles 'next' parameter for post-login redirects.
    """
    # Redirect authenticated users to home page
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Query user by email address
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verify password using bcrypt hash comparison
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Establish user session with optional remember-me functionality
            login_user(user, remember=form.remember.data)
            
            # Handle post-login redirect to originally requested page
            next_page = request.args.get('next')
            flash("Login successful!", "success")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
            
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    """
    User logout route - terminates user session.
    
    Returns:
        Response: Redirect to home page after logout.
    
    This route safely terminates the current user's authenticated session
    and provides feedback about the logout action.
    """
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ============================================================================
# DASHBOARD AND USER MANAGEMENT ROUTES
# ============================================================================

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    User dashboard route - main user control panel.
    
    Returns:
        str: Rendered dashboard.html template.
    
    This route requires user authentication and provides access to
    user-specific functionality like creating content and managing profile.
    """
    return render_template("dashboard.html", title="Dashboard", active_tab='None')

@app.route("/dashboard/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    User profile management route - handles profile updates and display.
    
    Methods:
        GET: Display current profile information in editable form
        POST: Process profile updates including image uploads
    
    Returns:
        str: Rendered profile.html template with form and user data.
    
    This route allows authenticated users to update their profile information,
    including username, email, bio, and profile picture with automatic resizing.
    """
    profile_form = UpdateProfileForm()
    
    if profile_form.validate_on_submit():
        # Handle profile picture upload with resizing to 125x125 pixels
        if profile_form.picture.data:
            # Delete old profile picture if it exists and is not default
            if current_user.image_file and current_user.image_file != 'default.jpg':
                delete_picture(current_user.image_file, 'static/user_pics')
            
            # Save new profile picture
            picture_file = save_picture(profile_form.picture.data, 'static/user_pics', (125, 125))
            current_user.image_file = picture_file
        
        # Update user profile information from form data
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.bio = profile_form.bio.data
        
        # Persist changes to database
        db.session.commit()
        flash("Your profile has been updated", "success")
        return redirect(url_for("profile"))
    
    elif request.method == "GET":
        # Pre-populate form with current user data
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        profile_form.bio.data = current_user.bio
    
    # Generate URL for current profile picture
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
    """
    New lesson creation route - handles lesson creation and management.
    
    Methods:
        GET: Display lesson creation form with course selection
        POST: Process lesson submission and create new lesson
    
    Returns:
        str: Rendered new_lesson.html template or redirect response.
    
    This route enables authenticated users to create new lessons within existing courses,
    with automatic slug generation and thumbnail handling.
    """
    new_lesson_form = NewLessonForm()
    
    # Populate course dropdown with all available courses
    courses = Course.query.all()
    new_lesson_form.course.choices = [(course.id, course.title) for course in courses]
    
    if new_lesson_form.validate_on_submit():
        # Handle slug generation: use provided slug or generate from title
        if new_lesson_form.slug.data:
            lesson_slug = new_lesson_form.slug.data
        else:
            lesson_slug = str(new_lesson_form.title.data).lower().replace(" ", "-")
        
        # Set default thumbnail if none provided
        picture_file = 'default_thumbnail.jpg'
        
        # Process uploaded thumbnail if provided
        if new_lesson_form.thumbnail.data:
            picture_file = save_picture(new_lesson_form.thumbnail.data, 'static/lesson_thumbnails')
        
        # Retrieve course object for lesson creation
        course = Course.query.get(new_lesson_form.course.data)
        
        # Create new lesson instance
        lesson = Lesson(
            title=new_lesson_form.title.data,
            content=new_lesson_form.content.data, 
            slug=lesson_slug,
            author=current_user, 
            course_name=course,
            thumbnail=picture_file
        )
        
        # Persist lesson to database
        db.session.add(lesson)
        db.session.commit()
        
        flash("Your lesson has been created!", "success")
        return redirect(url_for("dashboard"))
    
    # Prepare modal functionality for form display
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
    """
    New course creation route - handles course creation and management.
    
    Methods:
        GET: Display course creation form
        POST: Process course submission and create new course
    
    Returns:
        str: Rendered new_course.html template or redirect response.
    
    This route enables authenticated users to create new courses with automatic
    slug generation and icon handling with resizing to 150x150 pixels.
    """
    new_course_form = NewCourseForm()
    
    if new_course_form.validate_on_submit():
        # Handle slug generation: use provided slug or generate from title
        if new_course_form.slug.data:
            course_slug = new_course_form.slug.data
        else:
            course_slug = str(new_course_form.title.data).lower().replace(" ", "-")
        
        # Set default icon if none provided
        picture_file = 'default_icon.png'
        
        # Process uploaded icon if provided with resizing
        if new_course_form.icon.data:
            picture_file = save_picture(new_course_form.icon.data, 'static/course_icons', (150, 150))

        # Create new course instance
        course = Course(
            title=new_course_form.title.data,
            description=new_course_form.description.data,
            icon=picture_file,
            slug=course_slug
        )
        
        # Persist course to database
        db.session.add(course)
        db.session.commit()
        flash("Your course has been created!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("new_course.html", title="New Course", new_course_form=new_course_form, active_tab='new_course')


# ============================================================================
# CONTENT DISPLAY ROUTES
# ============================================================================

@app.route("/<string:course_slug>/<string:lesson_slug>")
def lesson(course_slug, lesson_slug):
    """
    Individual lesson display route - shows lesson content with navigation.
    
    Args:
        course_slug (str): URL identifier for the course
        lesson_slug (str): URL identifier for the lesson
    
    Returns:
        str: Rendered lesson.html template with lesson data and navigation.
    
    This route displays individual lesson content within its course context,
    providing previous/next lesson navigation for improved user experience.
    """
    # Retrieve course and lesson with 404 handling for invalid slugs
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    lesson = Lesson.query.filter_by(slug=lesson_slug, course_id=course.id).first_or_404()
    
    # Get all lessons in course for navigation calculation
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.date_posted.asc()).all()
    
    # Calculate current lesson position for navigation
    current_index = None
    for i, lsn in enumerate(lessons):
        if lsn.slug == lesson_slug:
            current_index = i
            break
    
    # Determine previous and next lessons for navigation
    previous_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None
    
    return render_template("lesson_view.html", 
                         title=lesson.title, 
                         lesson=lesson, 
                         course=course,
                         previous_lesson=previous_lesson,
                         next_lesson=next_lesson)


@app.route("/<string:course_slug>")
def course(course_slug):
    """
    Course display route - shows course details and lessons.
    Args:
        course_slug (str): URL identifier for the course
    Returns:
        str: Rendered course.html template with course and lessons data.
    
    This route displays course information and lists all associated lessons,
    ordered by publication date for logical learning progression.
    """
    # Retrieve course with 404 handling for invalid slug
    course = Course.query.filter_by(slug=course_slug).first_or_404()
    # Get all lessons in course ordered by publication date
    page = request.args.get('page', 1, type=int)
    lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.date_posted.desc()).paginate(page=page, per_page=6)
    
    return render_template("course.html", 
        title=course.title, 
        course=course, 
        lessons=lessons, 
        page=page
    )


@app.route("/courses")
def courses():
    """
    Courses listing route - displays all available courses.
    Args:
        page (int): Page number for pagination
    Returns:
        str: Rendered courses.html template with all courses data.
    
    This route provides a comprehensive view of all courses in the system,
    ordered by publication date to show newest content first.
    """
    page = request.args.get('page', 1, type=int)
    courses = Course.query.order_by(Course.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template("courses.html", title="Courses", courses=courses)

@app.route("/dashboard/user_lessons", methods=["GET", "POST"])
@login_required
def user_lessons():

    return render_template("user_lessons.html", title="Your Lessons", active_tab="user_lessons")

@app.route("/<string:course_slug>/<string:lesson_slug>/update", methods=["GET", "POST"])
@login_required
def update_lesson(course_slug, lesson_slug):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    
    # Check if user is authorized to edit this lesson
    if lesson.author != current_user:
        abort(403)
    
    # Get previous and next lessons for navigation
    previous_lesson, next_lesson = fet_previous_next_lesson(lesson_slug, course_slug)
    
    form = LessonUpdateForm()
    
    # Populate course dropdown with all available courses
    courses = Course.query.all()
    form.course.choices = [(course.id, course.title) for course in courses]
    
    # Pre-populate form with current lesson data
    if request.method == "GET":
        form.title.data = lesson.title
        form.content.data = lesson.content
        form.slug.data = lesson.slug
        form.course.data = lesson.course_id
    
    if form.validate_on_submit():
        try:
            # Update lesson data
            lesson.title = form.title.data
            lesson.content = form.content.data
            lesson.slug = form.slug.data if form.slug.data else str(form.title.data).lower().replace(" ", "-")
            
            # Update course if changed
            if form.course.data != lesson.course_id:
                new_course = Course.query.get(form.course.data)
                if new_course:
                    lesson.course_name = new_course
            
            # Handle thumbnail update
            if form.thumbnail.data:
                # Delete old thumbnail if it exists and is not default
                if lesson.thumbnail and lesson.thumbnail != 'default_thumbnail.jpg':
                    delete_picture(lesson.thumbnail, 'static/lesson_thumbnails')
                
                # Save new thumbnail
                picture_file = save_picture(form.thumbnail.data, 'static/lesson_thumbnails')
                lesson.thumbnail = picture_file
            
            db.session.commit()
            flash("Your lesson has been updated successfully!", "success")
            
            # Redirect to user_lessons page after successful update
            return redirect(url_for("user_lessons"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the lesson: {str(e)}", "danger")
            return redirect(url_for("update_lesson", course_slug=course_slug, lesson_slug=lesson_slug))
    
    return render_template("update_lesson.html", 
        title="Update | "+lesson.title,
        form=form, 
        lesson=lesson, 
        previous_lesson=previous_lesson,
        next_lesson=next_lesson
    )


@app.route("/<string:course_slug>/<string:lesson_slug>/delete", methods=["POST"])
@login_required
def delete_lesson(course_slug, lesson_slug):
    lesson = Lesson.query.filter_by(slug=lesson_slug).first_or_404()
    
    # Check if user is authorized to delete this lesson
    if lesson.author != current_user:
        abort(403)
    
    # Delete the lesson thumbnail if it exists and is not default
    if lesson.thumbnail and lesson.thumbnail != 'default_thumbnail.jpg':
        delete_picture(lesson.thumbnail, 'static/lesson_thumbnails')
    
    # Delete the lesson
    db.session.delete(lesson)
    db.session.commit()
    
    flash("Your lesson has been deleted!", "success")
    
    # Redirect back to user_lessons page instead of course page
    return redirect(url_for("user_lessons"))


def delete_course_picture(course):
    """
    Helper function to delete course icon when course is deleted or icon is updated.
    
    Args:
        course: Course object containing icon information
    """
    if course.icon and course.icon != 'default_icon.png':
        delete_picture(course.icon, 'static/course_icons')