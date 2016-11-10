import datetime
import sys

from random import SystemRandom

from baseconv import BaseConverter

from flask import Flask, render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from setup import DATABASE_URL

from crypto import encrypt_dump, decrypt_dump


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


class Bin(db.Model):
    __tablename__ = 'Bin'
    id = db.Column(db.BigInteger, primary_key =True)
    dumb = db.Column(db.Text)
    date_created = db.Column(db.DateTime)
    expire = db.Column(db.DateTime)


def id_generator():
    id_num = SystemRandom().randint(1, sys.maxsize)
    return id_num


@app.route('/')
def home():

    return render_template('home.html')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    if request.method =='POST':
        text = request.form.get('text')
        password = request.form.get('password')

        dump = Bin(id=id_generator(),
                   dumb=str(encrypt_dump(password,text)),
                   date_created=datetime.datetime.utcnow())

        db.session.add(dump)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/dump/<identity>')
def dump(identity):

    return render_template('home.html')


if __name__ == '__main__':

    app.run(debug=True)
