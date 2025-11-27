from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Optional, URL


class UploadPhotoForm(FlaskForm):
    profile_photo = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Upload')
    
class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    links = StringField('Links (comma separated)', validators=[Optional()])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')