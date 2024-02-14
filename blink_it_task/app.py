from flask import Flask, render_template, url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import json


app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config["UPLOAD_FOLDER"] = '/workspaces/codespaces-blank/blink_it_task/static/images'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class User_data(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    imgpath = db.Column(db.String(100), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class UploadFrom(FlaskForm):
    file = FileField("File")
    submit = SubmitField('Upload')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message= ""
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                message = "Password doesn't Match"
        else:
            message = "User not found"
    return render_template('login.html', form=form, message = message)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_id = current_user.get_id()
    user_name = User.query.filter_by(id=user_id).first().username
    form = UploadFrom()
    if form.validate_on_submit():
        file = form.file.data
        new_file = User_data(username=user_name, imgpath=str("../static/images/"+secure_filename(file.filename)))
        db.session.add(new_file)
        db.session.commit()
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
    img_list = User_data.query.filter_by(username = str(user_name))
    return render_template('dashboard.html',user_name = user_name, form = form,imglist = img_list)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    message = ""
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            message = 'That username already exists. Please choose a different one.'
        else:
            
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', form=form, message = message)


if __name__ == "__main__":
    app.run(debug=True)
