import os
from flask import current_app

# Import models for database queries
from pythonic.models import Course, Lesson


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
            picture_path = os.path.join(current_app.root_path, path, picture_name)
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