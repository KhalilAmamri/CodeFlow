from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_modals import Modal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e08fe17fe27ffc7009aba6a264a886ea81a5b5bd17f1fc97b9554c89c1464588'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)
modals = Modal(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from pythonic import routes