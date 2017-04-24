from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          u'用户名只能有字母，数字，下划线和点')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo('password2', message=u'密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email已经注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经注册')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message=u'密码必须相同')])
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'修改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()])
    submit = SubmitField(u'重置密码')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message=u'密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'提交新密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'不存在该Email')


class ChangeEmailForm(FlaskForm):
    email = StringField(u'新Email', validators=[
        Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'更新Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email已经注册.')
