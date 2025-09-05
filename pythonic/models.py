# Standard library imports for datetime functionality
from datetime import datetime

# Local application imports for database and login management
from pythonic import db, login_manager, app

# Flask-Login import for user authentication mixin
from flask_login import UserMixin

from itsdangerous import URLSafeSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    """
    User loader function for Flask-Login integration.
    
    This function is required by Flask-Login to retrieve user objects
    from the database based on user ID stored in the session.
    
    Args:
        user_id (str): User ID from session (converted to int)
    
    Returns:
        User: User object if found, None otherwise
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    User model representing application users and their profiles.
    
    This model extends Flask-Login's UserMixin to provide authentication
    functionality and manages user account information, profile data,
    and relationships with content they create.
    
    Attributes:
        id (int): Primary key, unique user identifier
        first_name (str): User's first name (required)
        last_name (str): User's last name (required)
        username (str): Unique username for login and display (required)
        email (str): Unique email address for account management (required)
        bio (str): Optional user biography text
        password (str): Hashed password for authentication (required)
        image_file (str): Profile picture filename with default
        lessons (relationship): One-to-many relationship with Lesson model
    
    Relationships:
        - One-to-many with Lesson: Users can create multiple lessons
        - Backref 'author' provides easy access to lesson creator
    """
    
    # Primary key and identification fields
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    
    # Profile and authentication fields
    bio = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    
    # Relationship to lessons created by this user
    lessons = db.relationship('Lesson', backref='author', lazy=True)
    
    def get_reset_token(self):
        """
        Generate a reset token for the user.
        """
        s = Serializer(app.config['SECRET_KEY'], salt='password-reset-salt')
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, age=3600):
        """
        Verify the reset token and return the user if it is valid.
        """
        s = Serializer(app.config['SECRET_KEY'], salt='password-reset-salt')
        try:
            user_id = s.loads(token, max_age=age)['user_id']
            return User.query.get(user_id)
        except:
            return None

    def __repr__(self):
        """
        String representation of User object for debugging and logging.
        
        Returns:
            str: Formatted string containing key user information
        """
        return f"User('{self.first_name}', '{self.last_name}', '{self.username}', '{self.email}', '{self.image_file}')"


class Lesson(db.Model):
    """
    Lesson model representing individual learning content within courses.
    
    This model manages lesson data including content, metadata, and
    relationships with users (authors) and courses. Lessons are the
    primary content units that users consume for learning.
    
    Attributes:
        id (int): Primary key, unique lesson identifier
        title (str): Lesson title displayed to users (required)
        date_posted (datetime): Publication timestamp with auto-default
        content (str): Main lesson content in text format (required)
        thumbnail (str): Lesson preview image filename with default
        slug (str): URL-friendly identifier for routing (required)
        user_id (int): Foreign key to User model (author)
        course_id (int): Foreign key to Course model (parent course)
    
    Relationships:
        - Many-to-one with User: Each lesson has one author
        - Many-to-one with Course: Each lesson belongs to one course
        - Backref 'author' provides easy access to lesson creator
        - Backref 'course_name' provides easy access to parent course
    """
    
    # Primary key and content fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    
    # Media and identification fields
    thumbnail = db.Column(db.String(20), nullable=False, default='default_thumbnail.jpg')
    slug = db.Column(db.String(32), nullable=False)
    
    # Foreign key relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        """
        String representation of Lesson object for debugging and logging.
        
        Returns:
            str: Formatted string containing lesson title and slug
        """
        return f"Lesson('{self.title}', '{self.slug}')"


class Course(db.Model):
    """
    Course model representing learning paths and content organization.
    
    This model manages course data including descriptions, metadata,
    and relationships with lessons. Courses provide structure and
    context for organizing related learning content.
    
    Attributes:
        id (int): Primary key, unique course identifier
        title (str): Course title displayed to users (required, unique)
        description (str): Course description and overview (required)
        icon (str): Course icon image filename with default
        date_posted (datetime): Publication timestamp with auto-default
        slug (str): URL-friendly identifier for routing (required, unique)
        lessons (relationship): One-to-many relationship with Lesson model
    
    Relationships:
        - One-to-many with Lesson: Courses contain multiple lessons
        - Backref 'course_name' provides easy access to parent course
        - Lessons are ordered by date_posted for logical progression
    """
    
    # Primary key and content fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    
    # Media and metadata fields
    icon = db.Column(db.String(20), nullable=False, default='default_icon.png')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationship to lessons within this course
    lessons = db.relationship('Lesson', backref='course_name', lazy=True)
    
    def __repr__(self):
        """
        String representation of Course object for debugging and logging.
        
        Returns:
            str: Formatted string containing course title and description
        """
        return f"Course('{self.title}', '{self.description}')"
