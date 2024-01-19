from datetime import datetime

from check_time import db, login_manager
from flask_login import UserMixin
from pytz import timezone
from werkzeug.security import check_password_hash, generate_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):  # flask_loginの機能を使う為にはUserMixinクラスが必要
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    grade = db.Column(db.Integer)
    nfc_id = db.Column(db.String(20), unique=True, index=True)
    time = db.relationship("CheckTime", backref="labo_member", lazy="dynamic")  # 1対多
    # post = db.relationship("BlogPost", backref="author", uselist=False)  # 1対1

    def __init__(self, email, username, password, administrator, grade, nfc_id):
        self.email = email
        self.username = username
        self.password = password
        self.administrator = administrator
        self.grade = grade
        self.nfc_id = nfc_id

    def __repr__(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):  # passwordを取り出せないように
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):  # パスワードが設定された場合はpassword_hashに設定するようにする
        self.password_hash = generate_password_hash(password)

    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            return 0


class CheckTime(db.Model):
    __tablename__ = "check_time"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    in_time = db.Column(db.DateTime)
    out_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)  # 1:入室 0:外室 など

    def __init__(self, user_id, in_time, out_time=None, status=0):
        self.user_id = user_id
        self.in_time = in_time
        self.out_time = out_time
        self.status = status
