from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, SelectField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User, Node
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    name = StringField(u'名字', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我简介')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          u'用户名只能有字母，数字，下划线和点')])
    role = SelectField(u'权限', coerce=int)
    name = StringField(u'名字', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我简介')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
           User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email已经注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
           User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经注册')


class PostForm(FlaskForm):
    title = TextAreaField(u'标题', validators=[Required()])
    node = SelectField(u'节点', validators=[Required()], coerce=int)
    body = PageDownField(u'内容', validators=[Required()])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.node.choices = [(node.id, node.name)
                             for node in Node.query.order_by(Node.name).all()]


class CommentForm(FlaskForm):
    body = StringField(u'评论', validators=[Required()])
    submit = SubmitField(u'提交')
