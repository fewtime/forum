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
