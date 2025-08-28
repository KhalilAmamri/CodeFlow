from tokenize import String
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
from pythonic.models import Course, User

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=25)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35), Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', message="Password must contain at least one letter and one number")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')


class UpdateProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    bio = TextAreaField('Bio', validators=[Length(max=150)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Profile')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please choose a different one.')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
def choice_query():
    return Course.query
class NewLessonForm(FlaskForm):
    course = QuerySelectField('Course', query_factory=choice_query, get_label='title')
    title = StringField("Lesson Title", validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField("Lesson Content", validators=[DataRequired(), Length(min=20)], render_kw={"rows": 10, "placeholder": "Write your lesson content here..."})
    slug = StringField("Lesson Slug", validators=[DataRequired(), Length(min=3, max=50)], render_kw={"placeholder": "Descriptive short version of your title. SEO friendly!"})
    thumbnail = FileField("Lesson Thumbnail", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Post")

class NewCourseForm(FlaskForm):
    title = StringField("Course Title", validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField("Course Description", validators=[DataRequired(), Length(min=20, max=500)], render_kw={"rows": 5, "placeholder": "Briefly describe what this course is about..."})
    icon = FileField("Course icon", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Create Course")