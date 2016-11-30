import sys

from baseconv import BaseConverter
from datetime import datetime
from random import SystemRandom

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, TextAreaField, StringField
from wtforms.validators import DataRequired

from sqlalchemy import Column, BigInteger, PickleType, DateTime

from crypto import encrypt_dump, decrypt_dump
from setup import DATABASE_URL


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'N0\xbeW\xfau\xc3O<\x80F\xb9\x95\x1a\x1b\x07'

db = SQLAlchemy(app)

characters = 'abcdefghkmnpqrstwxyz'
digits = '23456789'
base = characters + characters.upper() + digits
number_converter = BaseConverter(base)


class Bin(db.Model):
    __tablename__ = 'Bin'
    id = Column(BigInteger, primary_key=True)
    dump = Column(PickleType)
    date_created = Column(DateTime)
    expire = Column(DateTime)


class EncryptForm(FlaskForm):
    dump = TextAreaField('Data', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])


class DecryptForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])


def gen_token(long_id):
    s = Serializer(app.config['SECRET_KEY'], expires_in=30)
    token = s.dumps({'id': long_id})
    return token


def confirm_token(token, long_id):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False
    if data.get('id') != long_id:
        return False
    return True


def id_generator():
    return SystemRandom().randint(1, sys.maxsize)


def gen_short_id(long_id):
    return number_converter.encode(long_id)


def get_long_id(short_id):
    return number_converter.decode(short_id)


@app.route('/')
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    form = EncryptForm()

    if form.validate_on_submit():
        text = form.dump.data
        password = form.password.data

        number = id_generator()
        data = Bin(id=number,
                   dump=encrypt_dump(password, text),
                   date_created=datetime.utcnow())
        short_id = gen_short_id(number)

        db.session.add(data)
        db.session.commit()
        return redirect(url_for('dump', identity=short_id))
    return render_template('home.html', form=form)


@app.route('/dump/<identity>', methods=['GET', 'POST'])
def dump(identity):

    long_id = int(get_long_id(identity))
    dump = Bin.query.get_or_404(long_id)

    if request.method == 'GET':

        try:
            token = session['token']
        except:
            token = None

        if token and confirm_token(token, long_id):
            session.pop('token', None)
            return redirect(url_for('dump', identity=gen_short_id(long_id)))

        else:
            return render_template('decryption_page.html', identity=identity)

    if request.method == 'POST':

        data = decrypt_dump(request.form.get('password'), dump.dump)

        if data:
            session['token'] = gen_token(long_id)
            ## this should be redirect
            # however i need to find a better to do this
            return render_template('data_page.html', data=data)
        else:
            return redirect(url_for('dump', identity=gen_short_id(long_id)))

if __name__ == '__main__':

    app.run(debug=True)
