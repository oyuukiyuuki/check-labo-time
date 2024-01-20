from check_time import app
from check_time.users.views import users
from check_time.connect_dev.views import device
from check_time.main.views import main
from check_time.error_pages.handlers import error_pages

app.register_blueprint(users)
app.register_blueprint(device)
app.register_blueprint(main)
app.register_blueprint(error_pages)

# bbb

if __name__ == "__main__":
    # app.run(debug=True)
    app.run()
