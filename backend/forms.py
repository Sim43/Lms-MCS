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
    category_code = SelectField('Category Code', coerce=str, validators=[Optional()], 
                               choices=[('', 'Select a category (optional)')], 
                               render_kw={"class": "form-select", "id": "category_code"})
    category_other = StringField('Other Category Code', validators=[Optional(), Length(max=10)], 
                                render_kw={"class": "form-control", "placeholder": "Enter course code (e.g., EE, CS)", 
                                          "style": "text-transform: uppercase", "id": "category_other", "pattern": "[A-Z0-9]{2,10}"})
    thumbnail = FileField('Thumbnail Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])], 
                         render_kw={"class": "form-control", "accept": "image/*"})
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # Always set choices - WTForms requires choices to be set before validation
        try:
            from .category_codes import get_category_code_choices
            self.category_code.choices = get_category_code_choices()
        except (ImportError, RuntimeError):
            # Fallback to default if import fails or outside app context
            if not self.category_code.choices:
                self.category_code.choices = [('', 'Select a category (optional)')]

class EnrollmentForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired(), Length(min=6, max=20)], 
                             render_kw={"class": "form-control", "placeholder": "Enter 8-character course code", "style": "text-transform: uppercase"})

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

