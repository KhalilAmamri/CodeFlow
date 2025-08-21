from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'e08fe17fe27ffc7009aba6a264a886ea81a5b5bd17f1fc97b9554c89c1464588'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


from pythonic import routes