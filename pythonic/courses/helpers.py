

# Import the delete_picture function from main helpers
from pythonic.helpers import delete_picture


def delete_course_picture(course):
    """
    Helper function to delete course icon when course is deleted or icon is updated.
    
    Args:
        course: Course object containing icon information
    """
    if course.icon and course.icon != 'default_icon.png':
        delete_picture(course.icon, 'static/course_icons')