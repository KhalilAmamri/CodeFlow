from flask import Blueprint


# Flask-Login imports for user authentication and session management
from flask_login import current_user, login_required

# Local model imports for database entities
from pythonic.models import Lesson, Course

# Flask core imports for web framework functionality
from flask import render_template, url_for, flash, redirect, request, abort

# Local form imports for user input validation and processing
from pythonic.lessons.forms import NewLessonForm, LessonUpdateForm
# Local form imports for course validation and processing
from pythonic.courses.forms import NewCourseForm

from pythonic.helpers import save_picture

from pythonic.lessons.helpers import fet_previous_next_lesson, delete_picture

# Local application imports for database, encryption, and app instance
from pythonic import db

# Flask-Modals imports for dynamic modal functionality
from flask_modals import Modal, render_template_modal





lessons = Blueprint('lessons', __name__)


@lessons.route("/dashboard/new_lesson", methods=["GET", "POST"])
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
        return redirect(url_for("users.dashboard"))
    
    # Prepare modal functionality for form display
    modals = Modal().load
    return render_template_modal(
        "new_lesson.html", title="New Lesson",
        new_lesson_form=new_lesson_form, 
        active_tab='new_lesson',
        modals=modals
    )

@lessons.route("/<string:course_slug>/<string:lesson_slug>")
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
@lessons.route("/dashboard/user_lessons", methods=["GET", "POST"])
@login_required
def user_lessons():

    return render_template("user_lessons.html", title="Your Lessons", active_tab="user_lessons")

@lessons.route("/<string:course_slug>/<string:lesson_slug>/update", methods=["GET", "POST"])
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
            return redirect(url_for("lessons.user_lessons"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the lesson: {str(e)}", "danger")
            return redirect(url_for("lessons.update_lesson", course_slug=course_slug, lesson_slug=lesson_slug))
    
    return render_template("update_lesson.html", 
        title="Update | "+lesson.title,
        form=form, 
        lesson=lesson, 
        previous_lesson=previous_lesson,
        next_lesson=next_lesson
    )
@lessons.route("/<string:course_slug>/<string:lesson_slug>/delete", methods=["POST"])
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
    return redirect(url_for("lessons.user_lessons"))
