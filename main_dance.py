from flask import Flask
from flask import Flask, redirect, \
    url_for, session, jsonify, json
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required
from urllib.parse import urlencode
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.google import make_google_blueprint, google
app = Flask(__name__)
app.config['SECRET_KEY']="9d9eff20ae24d1c667094de18f1816b3baee73514c57b6c02a059a3a2838b3e3e68807b1dbebc2c821746f1f"
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///dance_db.db"

app.config.from_pyfile("application.cfg", silent=True)
database = SQLAlchemy()
database.init_app(app)
facebook_bp = make_facebook_blueprint(
    client_id = app.config['FACEBOOK_OAUTH_CLIENT_ID'],
    client_secret=app.config['FACEBOOK_OAUTH_CLIENT_SECRET'],
    scope = "public_profile email",
    redirect_url = "/index"
)

login_manager=LoginManager()
login_manager.init_app(app)

app.register_blueprint(facebook_bp, url_prefix='/facebook_login')

"""google_bp = make_google_blueprint(
    scope=["profile", "email"],
    client_id = app.config['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret = app.config['GOOGLE_OAUTH_CLIENT_SECRET'],

)"""
# app.register_blueprint(google_bp, url_prefix='/facebook_login')
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)




class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256))
    picture = database.Column(database.String(256))
    google_id = database.Column(database.String(256))
    facebook_id = database.Column(database.String(256))


@app.route('/facebook_login')
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    response = facebook.get('/me')
    #assert resp.ok, resp.text
    print(response.json())
    return "You are @{login} on facebook".format(login = response.json()['name'])

@app.route("/")
@app.route('/index')
def index():
    return "<a href='{}'>Login with Google</a> <br>" \
        "<a href='{}'>Login with Facebook</a>". \
        format(url_for('google_login'), url_for('facebook_login'))

@app.route('/google_login')

def google_login():
    if not google.authorized:
        return redirect(urll_for('google.login'))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])

if __name__=='__main__':
    with app.app_context():
        database.create_all()
    app.run(debug=True, host="0.0.0.0")

