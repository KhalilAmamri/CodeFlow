# Standard library imports for string tokenization
from tokenize import String

# Flask-Login import for current user access
from flask_login import current_user

# Flask-WTF imports for form handling and CSRF protection
from flask_wtf import FlaskForm

# WTForms-SQLAlchemy for database-driven form fields
from wtforms_sqlalchemy.fields import QuerySelectField

# Flask-WTF file handling for file uploads
from flask_wtf.file import FileField, FileAllowed

# WTForms core components for form field types
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField

# WTForms validators for input validation and constraints
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError, Optional

# Local model imports for custom validation logic
from pythonic.models import Course, User


class RegistrationForm(FlaskForm):
    """
    User registration form for new account creation.
    
    This form handles user registration with comprehensive validation including
    username/email uniqueness checks, password strength requirements, and
    proper field constraints for data integrity.
    
    Fields:
        first_name: User's first name with length validation
        last_name: User's last name with length validation
        email: Email address with format and uniqueness validation
        password: Password with strength and complexity requirements
        confirm_password: Password confirmation with equality validation
        username: Unique username with length and uniqueness validation
        submit: Form submission button
    
    Custom Validation:
        - Username uniqueness check against existing users
        - Email uniqueness check against existing users
    """
    
    # Personal information fields with length constraints
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=25)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=25)])
    
    # Authentication fields with comprehensive validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, max=35), 
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', 
               message="Password must contain at least one letter and one number")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    
    # Form submission button
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        Custom validation to ensure username uniqueness.
        
        Args:
            username: Username field data to validate
        
        Raises:
            ValidationError: If username already exists in database
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validation to ensure email uniqueness.
        
        Args:
            email: Email field data to validate
        
        Raises:
            ValidationError: If email already exists in database
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')


class UpdateProfileForm(FlaskForm):
    """
    User profile update form for authenticated users.
    
    This form allows existing users to update their profile information
    including email, username, bio, and profile picture. It includes
    smart validation that only checks uniqueness when values actually change.
    
    Fields:
        email: Updated email address with format and uniqueness validation
        username: Updated username with length and uniqueness validation
        bio: Optional biography text with length constraint
        picture: Profile picture file upload with format restrictions
        submit: Form submission button
    
    Custom Validation:
        - Username uniqueness only checked if changed from current value
        - Email uniqueness only checked if changed from current value
    """
    
    # Profile information fields
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    bio = TextAreaField('Bio', validators=[Length(max=150)])
    
    # File upload field with format restrictions
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    
    # Form submission button
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        """
        Custom validation for username changes with smart uniqueness checking.
        
        Only validates uniqueness if the username has actually changed from
        the current user's username, preventing unnecessary database queries.
        
        Args:
            username: Username field data to validate
        
        Raises:
            ValidationError: If username already exists and has changed
        """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validation for email changes with smart uniqueness checking.
        
        Only validates uniqueness if the email has actually changed from
        the current user's email, preventing unnecessary database queries.
        
        Args:
            email: Email field data to validate
        
        Raises:
            ValidationError: If email already exists and has changed
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose a different one.')


class LoginForm(FlaskForm):
    """
    User authentication form for existing account login.
    
    This form handles user login with email/password authentication
    and includes an optional "Remember Me" checkbox for persistent sessions.
    
    Fields:
        email: User's email address for account identification
        password: User's password for authentication
        remember: Boolean checkbox for persistent login sessions
        submit: Form submission button
    """
    
    # Authentication fields
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    
    # Session management option
    remember = BooleanField('Remember Me')
    
    # Form submission button
    submit = SubmitField('Login')


def choice_query():
    """
    Query function for dynamic course selection in forms.
    
    This function provides the query object for populating course
    selection fields dynamically from the database.
    
    Returns:
        Query: SQLAlchemy query object for Course model
    """
    return Course.query


class NewLessonForm(FlaskForm):
    """
    Lesson creation form for authenticated users.
    
    This form enables users to create new lessons within existing courses,
    with rich text content editing, optional slug generation, and
    thumbnail image uploads.
    
    Fields:
        title: Lesson title with required validation
        content: Rich text content using editor integration
        slug: Optional URL-friendly identifier (auto-generated if empty)
        course: Course selection dropdown populated from database
        thumbnail: Optional lesson preview image
        submit: Form submission button
    """
    
    # Content fields with validation
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    
    # Optional slug field for custom URL generation
    slug = StringField('Slug (optional)', validators=[Optional()])
    
    # Course selection with database-driven choices
    course = SelectField('Course', coerce=int, validators=[DataRequired()])
    
    # Optional thumbnail image upload
    thumbnail = FileField('Thumbnail')
    
    # Form submission button
    submit = SubmitField("Post")


class NewCourseForm(FlaskForm):
    """
    Course creation form for authenticated users.
    
    This form enables users to create new courses with comprehensive
    information including descriptions, icons, and optional slug generation.
    
    Fields:
        title: Course title with length and uniqueness validation
        description: Course description with length constraints and placeholder
        icon: Optional course icon image upload
        slug: Optional URL-friendly identifier (auto-generated if empty)
        submit: Form submission button
    
    Custom Validation:
        - Course title uniqueness check against existing courses
    """
    
    # Course information fields
    title = StringField("Course Title", validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField("Course Description", validators=[
        DataRequired(), 
        Length(min=20, max=500)
    ], render_kw={
        "rows": 5, 
        "placeholder": "Briefly describe what this course is about..."
    })
    
    # Optional course icon with format restrictions
    icon = FileField("Course icon", validators=[FileAllowed(['jpg', 'png'])])
    
    # Optional slug field for custom URL generation
    slug = StringField('Slug (optional)', validators=[Optional()])
    
    # Form submission button
    submit = SubmitField("Create Course")
    
    def validate_title(self, title):
        """
        Custom validation to ensure course title uniqueness.
        
        Args:
            title: Title field data to validate
        
        Raises:
            ValidationError: If course title already exists in database
        """
        course = Course.query.filter_by(title=title.data).first()
        if course:
            raise ValidationError('That course title is already taken. Please choose a different one.')

class LessonUpdateForm(NewLessonForm):
    thumbnail = FileField('Thumbnail', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Lesson')