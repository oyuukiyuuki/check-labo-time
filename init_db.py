from check_time import db
from check_time.models import User, CheckTime
from datetime import datetime
from pytz import timezone

db.drop_all()
db.create_all()
user1 = User(
    email="oono@test.com",
    username="おおの",
    password="123",
    administrator="1",
    grade="1",
    nfc_id="3333ffff",
)
db.session.add(user1)
# db.session.commit()

# db.create_all()
# time1 = CheckTime(
#     user_id=1,
# )
time1 = CheckTime(user_id=1, in_time=datetime.now(timezone("Asia/Tokyo")))
db.session.add(time1)

user2 = User(
    email="mori@test.com",
    username="もり",
    password="123",
    administrator="0",
    grade="2",
    nfc_id="44449999",
)
db.session.add(user2)
# db.session.commit()

# db.create_all()
# time1 = CheckTime(
#     user_id=1,
# )
time2 = CheckTime(user_id=2, in_time=datetime.now(timezone("Asia/Tokyo")))
db.session.add(time2)

user3 = User(
    email="okazaki@test.com",
    username="おかざき",
    password="123",
    administrator="0",
    grade="3",
    nfc_id="333397699",
)
db.session.add(user3)
# db.session.commit()

# db.create_all()
# time1 = CheckTime(
#     user_id=1,
# )
time3 = CheckTime(user_id=3, in_time=datetime.now(timezone("Asia/Tokyo")))
db.session.add(time3)

db.session.commit()
