from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, \
    SubmitField
from wtforms.validators import Required
from ..models import Role, User, Node
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    title = TextAreaField(u'标题', validators=[Required()])
    node = SelectField(u'节点', validators=[Required()], coerce=int)
    body = PageDownField(u'内容', validators=[Required()])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.node.choices = [(node.id, node.name)
                             for node in Node.query.order_by(Node.name).all()]


class NodeForm(FlaskForm):
    name = TextAreaField(u'节点名称', validators=[Required()])
    intro = TextAreaField(u'简介', validators=[Required()])
    submit = SubmitField(u'提交')
