from flask import Blueprint
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from pythonic.models import User, Lesson, Course
from pythonic import bcrypt, db, admin

class UserModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.password = bcrypt.generate_password_hash(model.password).decode('utf-8')

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'KhalilAmamri'
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.username == 'KhalilAmamri'
admin_bp = Blueprint('admin_bp', __name__)

admin.add_view(UserModelView(User, db.session))
admin.add_view(ModelView(Lesson, db.session))
admin.add_view(ModelView(Course, db.session))

