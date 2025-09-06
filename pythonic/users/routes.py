from flask import Blueprint

# Standard library imports for security, image processing, and file operations
# Flask-Login imports for user authentication and session management
from flask_login import login_user, current_user, logout_user, login_required

# Local model imports for database entities
from pythonic.models import User, Lesson

# Flask core imports for web framework functionality
from flask import render_template, url_for, flash, redirect, request, abort

# Local form imports for user input validation and processing
from pythonic.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm

# Local application imports for database, encryption, and app instance
from pythonic import db, bcrypt

# Local helper imports for image processing
from pythonic.helpers import save_picture
from pythonic.lessons.helpers import delete_picture
# Local helper imports for email functionality
from pythonic.users.helpers import send_reset_email


users = Blueprint('users', __name__)

@users.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))
    
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
        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))
    
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


@users.route("/logout")
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

@users.route("/dashboard", methods=["GET"])
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

@users.route("/dashboard/profile", methods=["GET", "POST"])
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
        return redirect(url_for("users.profile"))
    
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

@users.route("/author/<string:username>", methods=["GET"])
def author(username):
    """
    Author display route - shows lessons created by a specific author.
    Args:
        username (str): Username of the author
    Returns:
        str: Rendered author.html template with author's lessons data.
    
    This route displays all lessons created by a specific author, ordered by publication date.
    """
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    lessons = Lesson.query.filter_by(author=user).order_by(Lesson.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template("author.html", title=user.username, user=user, lessons=lessons, page=page)

@users.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)

@users.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)