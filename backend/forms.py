from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, URL, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter password"})
    remember_me = BooleanField('Remember me', default=False)

class StudentRegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)], 
                          render_kw={"class": "form-control", "placeholder": "Choose a username"})
    email = StringField('Email', validators=[DataRequired()], 
                       render_kw={"class": "form-control", "placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], 
                           render_kw={"class": "form-control", "placeholder": "Create a password"})
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], 
                            render_kw={"class": "form-control", "placeholder": "Confirm your password"})

class InstructorRegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)], 
                          render_kw={"class": "form-control", "placeholder": "Choose a username"})
    email = StringField('Email', validators=[DataRequired()], 
                       render_kw={"class": "form-control", "placeholder": "Enter your email"})
    instructor_key = StringField('Instructor Registration Key', validators=[DataRequired()], 
                                render_kw={"class": "form-control", "placeholder": "Enter the instructor registration key"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], 
                           render_kw={"class": "form-control", "placeholder": "Create a password"})
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], 
                            render_kw={"class": "form-control", "placeholder": "Confirm your password"})

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=200)], 
                       render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[DataRequired()], 
                               render_kw={"class": "form-control", "rows": 5})
    category_id = SelectField('Category', coerce=int, validators=[Optional()], 
                             render_kw={"class": "form-select"})
    thumbnail = FileField('Thumbnail Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])], 
                         render_kw={"class": "form-control", "accept": "image/*"})

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(max=200)], 
                       render_kw={"class": "form-control"})
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], 
                        render_kw={"class": "form-control"})
    video_url = StringField('Video URL', validators=[Optional(), URL()], 
                           render_kw={"class": "form-control", "placeholder": "https://youtube.com/watch?v=..."})
    video_file = FileField('Video File', validators=[Optional()], 
                          render_kw={"class": "form-control", "accept": "video/*"})
    text_content = TextAreaField('Text Content', validators=[Optional()], 
                                render_kw={"class": "form-control", "rows": 10})
    lesson_file = FileField('Additional File', validators=[Optional()], 
                           render_kw={"class": "form-control", "accept": ".pdf,.doc,.docx,.txt"})

