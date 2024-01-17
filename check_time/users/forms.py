from check_time.models import User
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email("正しいメールアドレスを入力してください")]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class RegistrationForm(FlaskForm):
    email = StringField(
        "メールアドレス", validators=[DataRequired(), Email(message="正しいメールアドレスを入力してください")]
    )
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(), EqualTo("pass_confirm", message="パスワードが一致していません")],
    )
    pass_confirm = PasswordField("パスワード(確認)", validators=[DataRequired()])
    grade = IntegerField("学年", validators=[DataRequired()])
    submit = SubmitField("登録")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザ名はすでに使われてます")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスはすでに使われてます")

    def validate_grade(self, field):
        if int(field.data) < 0:
            raise ValidationError("存在しない学年です")


class UpdataUserForm(FlaskForm):
    email = StringField(
        "メールアドレス", validators=[DataRequired(), Email(message="正しいメッセージを入力してください")]
    )
    username = StringField("ユーザ名", validators=[DataRequired()])
    grade = StringField("学年", validators=[DataRequired()])

    password = PasswordField(
        "パスワード", validators=[EqualTo("pass_confirm", message="パスワードが一致していません")]
    )
    pass_confirm = PasswordField("パスワード(確認)")
    submit = SubmitField("更新")

    def __init__(self, user_id, *args, **kwargs):
        super(UpdataUserForm, self).__init__(*args, **kwargs)
        self.id = user_id

    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザ名はすでに使われてます")

    def validate_email(self, field):
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスはすでに使われてます")

    def validate_grade(self, field):
        if int(field.data) < 0:
            raise ValidationError("存在しない学年です")
