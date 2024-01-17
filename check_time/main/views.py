from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from check_time.models import User, CheckTime
from flask_login import login_required

main = Blueprint("main", __name__)


@main.route("/state_list")
@login_required
def state_list():
    state_list = []
    user_list = User.query.order_by(User.grade.desc())  # 学年順
    for user in user_list:
        latest_time = (
            CheckTime.query.filter_by(user_id=int(user.id))
            .order_by(CheckTime.id.desc())
            .first()
        )
        state_list.append(latest_time.status) if latest_time else state_list.append(6)
    return render_template(
        "main/state_list.html", user_list=user_list, state_list=state_list
    )


@main.route("/")
def home():
    return render_template("main/home.html")
