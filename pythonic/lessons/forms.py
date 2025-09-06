
"""
Lesson Forms

This module contains WTForms for lesson creation and management
with validation for lesson data, course selection, and file uploads.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

from pythonic.models import Course


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

class LessonUpdateForm(NewLessonForm):
    thumbnail = FileField('Thumbnail', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Lesson')