from flask import Flask, redirect, \
    url_for, session, jsonify, json
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required
from urllib.parse import urlencode
from flask_login import current_user
from flask_googlelogin import GoogleLogin
from flask_sqlalchemy import SQLAlchemy
from flask_googlelogin import GoogleLogin
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database2.db"
app.config[
    'SECRET_KEY'] = '9d9eff20ae24d1c667094de18f1816b3baee73514c57b6c02a059a3a2838b3e3e68807b1dbebc2c821746f1f \
     a837dbf490d67e1908f77664151875382915e598 '
app.config['GOOGLE_LOGIN_CLIENT_ID'] = '594813004745-1hcngg3mvnl0pur2rm6qtlo3agevaa7m.apps.googleusercontent.com'
app.config['GOOGLE_LOGIN_CLIENT_SECRET'] = 'gn-Hg1txIHtffY-cjDXJ0p-v'
app.config['GOOGLE_LOGIN_SCOPES'] = 'openid email profile'
app.config['GOOGLE_LOGIN_REDIRECT_SCHEME'] = "http"
app.config['GOOGLE_LOGIN_REDIRECT_URI'] = "https://localhost:8080/oauth2callback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
database = SQLAlchemy()
database.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

google_login = GoogleLogin()
google_login.init_app(app, login_manager)

class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256))
    picture = database.Column(database.String(256))
    google_id = database.Column(database.String(256))
    facebook_id = database.Column(database.String(256))


@login_manager.user_loader
def standard_user_loader(user_id):
    return User.query.get(user_id)


@google_login.user_loader
def get_user(userid):
    return User.query.get(userid)


@app.route('/get_access_token')
@login_required
def get_access_token():
    refresh_token = json.loads(session['token'])['refresh_token']
    return jsonify(google_login.get_access_token(refresh_token))


@app.route('/oauth2callback')
@google_login.oauth2callback
def create_or_update_user(token, userinfo, **params):
    user = User.query.filter_by(google_id=userinfo['id']).first()
    if user:
        user.name = userinfo['name']
        user.picture = userinfo['picture']
    else:
        user = User()
        user.google_id = userinfo['id']
        user.name = userinfo['name']
        user.avatar = userinfo['picture']
    database.session.add(user)
    database.session.commit()
    login_user(user, remember=True)
    return redirect(url_for('profile'))

@app.route('/')
def index():
    return "<a href='{}'>Login with Google</a> <br>". \
        format(google_login.login_url(
         params={'approval_prompt': 'force',
                'access_type': 'offline'})
               )


@app.route('/profile')
@login_required
def profile():
    return "<p>" \
           "You are " \
           "logged in " \
           "To sign out " \
           "<a href={}>" \
           "Click here" \
           "</a>" \
           "</p>".format(url_for('logout'))


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/">Return to /</a></p>
        """


if __name__ == "__main__":
    with app.app_context():
        database.create_all()
    app.run(debug=True, host="localhost", port=8080, ssl_context="adhoc")
