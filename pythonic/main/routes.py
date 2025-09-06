from flask import Blueprint

# Standard library imports for security, image processing, and file operations
import secrets
import os


# Local model imports for database entities
from pythonic.models import Lesson, Course


# Flask core imports for web framework functionality
from flask import render_template, url_for, request, jsonify


from flask import current_app


main = Blueprint('main', __name__)

# TinyMCE image upload endpoint
ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
@main.route('/upload-image', methods=['POST'])
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
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate safe unique name and save
    random_hex = secrets.token_hex(16)
    filename = f"{random_hex}{ext}"
    save_path = os.path.join(upload_dir, filename)
    image.save(save_path)

    file_url = url_for('static', filename=f'uploads/{filename}')
    # TinyMCE expects { location: 'url' }
    return jsonify({'location': file_url})

    
@main.route("/")
@main.route("/home")
def home():
    """
    Home page route - displays latest lessons and courses.
    
    Returns:
        str: Rendered home.html template with lessons and courses data.
    
    This route fetches the most recent lessons and courses from the database,
    ordered by publication date, and displays them on the main landing page.
    """
    lessons = Lesson.query.order_by(Lesson.date_posted.desc()).paginate(page=1, per_page=6)
    courses = Course.query.order_by(Course.date_posted.desc()).paginate(page=1, per_page=6)
    return render_template("home.html", lessons=lessons, courses=courses)


@main.route("/about")
def about():
    """
    About page route - displays application information.
    
    Returns:
        str: Rendered about.html template with page title.
    """
    return render_template("about.html", title="About Page")
