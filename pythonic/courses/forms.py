
"""
Course Forms

This module contains WTForms for course creation and management
with validation for course data and file uploads.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from pythonic.models import Course


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
