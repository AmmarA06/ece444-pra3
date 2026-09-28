import re
from flask import (Flask, render_template, session, redirect, url_for, flash,
                   request)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField('What is your UofT Email address?',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


def is_uoft_email(email):
    return email is not None and 'utoronto' in email


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        old_email = session.get('email')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        if is_uoft_email(form.email.data):
            return redirect(url_for('chatbot'))
        return redirect(url_for('index'))
    email = session.get('email')
    return render_template('index.html', form=form, name=session.get('name'),
                           email=email, is_uoft=is_uoft_email(email))


@app.route('/chatbot')
def chatbot():
    if not is_uoft_email(session.get('email')):
        return redirect(url_for('index'))
    return render_template('chatbot.html', name=session.get('name'))


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json["message"]
    text = message.lower()

    match = re.search(r"my name is\s+([a-z][a-z' -]*)", text)
    if "what is my name" in text:
        chat_name = session.get('chat_name')
        if chat_name:
            reply = "Your name is {}.".format(chat_name)
        else:
            reply = "I don't know your name yet. Tell me with 'My name is ...'."
    elif match:
        # store the name in the session cookie so later requests can recall it
        start, end = match.span(1)
        chat_name = message[start:end].strip()
        session['chat_name'] = chat_name
        reply = "Nice to meet you, {}!".format(chat_name)
    elif "hello" in text:
        reply = "Hello!"
    else:
        reply = "I don't understand."

    return {"reply": reply}


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
