from check_time import db
from check_time.models import User, CheckTime
from check_time.users.forms import LoginForm, RegistrationForm, UpdataUserForm
from flask_login import current_user, login_required, login_user, logout_user
from pytz import timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from datetime import datetime

users = Blueprint("users", __name__)


@users.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)  # login_userに対してユーザを渡すことでそのユーザはログインできる
                next = request.args.get("next")  # ユーザが行きたかったページ
                if (next is None) or (not next[0] == "/"):
                    next = url_for("main.state_list")
                return redirect(next)

            else:
                flash("パスワードが一致しません")
        else:
            flash("入力されたユーザは存在しません")

    return render_template("users/login.html", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # postが来たら
        # session["email"] = form.email.data
        # session["username"] = form.username.data
        # session["password"] = form.password.data
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            administrator="0",
            grade=form.grade.data,
        )
        db.session.add(user)
        db.session.commit()
        # check_time = CheckTime(user_id=user.id, in_time=None, status=6)
        # db.session.add(check_time)
        # db.session.commit()

        flash("ユーザが登録されました")
        return redirect(url_for("users.login"))  # ユーザ管理ページに飛ばす
    return render_template("users/register.html", form=form)


@users.route("/user_maintenance")
@login_required
def user_maintenance():
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=10)  # ページネーション
    # users = User.query.order_by(User.id).all()  # 昇順で取得
    # users = User.query.order_by(User.id.desc()).all()  # 降順で取得
    return render_template("users/user_maintenance.html", users=users)


@users.route("/<int:user_id>/account", methods=["GET", "POST"])
@login_required
def account(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id and not current_user.is_administrator():
        abort(403)
    form = UpdataUserForm(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        user.grade = form.grade.data
        db.session.commit()
        flash("ユーザアカウントが更新されました")

        return redirect(url_for("users.user_maintenance"))
    elif request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
        form.grade.data = user.grade
    return render_template("users/account.html", form=form)


@users.route("/<int:user_id>/delete", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_administrator():
        abort(403)
    if user.is_administrator():
        flash("管理者は削除できません")
        return redirect(url_for("users.account", user_id=user_id))
    db.session.delete(user)
    db.session.commit()
    flash("ユーザアカウントが削除されました")
    return redirect(url_for("users.user_maintenance"))


# @users.route("/<int:user_id>/user_posts")
# @login_required
# def user_posts(user_id):
#     form = BlogSearchForm()

#     user = User.query.filter_by(id=user_id).first_or_404()

#     # ブログ記事の取得
#     page = request.args.get("page", 1, type=int)
#     blog_posts = (
#         BlogPost.query.filter_by(user_id=user_id)
#         .order_by(BlogPost.id.desc())
#         .paginate(page=page, per_page=10)
#     )

#     # 最新記事の取得
#     recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()

#     # カテゴリの取得
#     blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()

#     return render_template(
#         "index.html",
#         blog_posts=blog_posts,
#         recent_blog_posts=recent_blog_posts,
#         blog_categories=blog_categories,
#         user=user,
#         form=form,
#     )
