import os
from flask import Flask, make_response, jsonify
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.jinja_env.filters["zip"] = zip

app.config["SECRET_KEY"] = "mysecretkey"
basedir = os.path.abspath(os.path.dirname(__file__))
uri = os.environ.get("DATABASE_URL")
if uri:
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
else:
    # app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:0Y1u1u2ki@localhost"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"


def localize_callback(*args, **kwargs):
    return "このページにアクセスするには、ログインが必要です。"


login_manager.localize_callback = localize_callback

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")  # JWTに署名する際の秘密鍵
app.config["JWT_ALGORITHM"] = "HS256"  # 暗号化署名のアルゴリズム
app.config["JWT_LEEWAY"] = 0  # 有効期限に対する余裕時間
app.config["JWT_EXPIRATION_DELTA"] = timedelta(days=30)  # トークンの有効期間を30日に設定
app.config["JWT_NOT_BEFORE_DELTA"] = timedelta(seconds=0)  # トークンの使用を開始する相対時間


def jwt_unauthorized_loader_handler(reason):
    return make_response(jsonify({"error": "Unauthorized"}), 401)


jwt = JWTManager(app)
jwt.unauthorized_loader(jwt_unauthorized_loader_handler)
