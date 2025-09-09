from flask import Blueprint, flash, redirect, request, url_for



# Local model imports for database entities
from codeflow import db
from codeflow.courses.forms import NewCourseForm
from codeflow.models import Lesson, Course


# Flask core imports for web framework functionality
from flask import render_template



from codeflow.helpers import save_picture





courses_bp = Blueprint('courses', __name__)

@courses_bp.route("/dashboard/new_course", methods=["GET", "POST"])
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
        return redirect(url_for("users.dashboard"))
    
    return render_template("new_course.html", title="New Course", new_course_form=new_course_form, active_tab='new_course')





@courses_bp.route("/<string:course_slug>")
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


@courses_bp.route("/courses")
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
