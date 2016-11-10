import datetime
import sys
import json

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


characters  = 'abcdefghkmnpqrstwxyz'
digits = '23456789'
base = characters + characters.upper() + digits
number_converter = BaseConverter(base)

class Bin(db.Model):
    __tablename__ = 'Bin'
    id = db.Column(db.BigInteger, primary_key =True)
    dump = db.Column(db.PickleType)
    date_created = db.Column(db.DateTime)
    expire = db.Column(db.DateTime)


def id_generator():
    return SystemRandom().randint(1, sys.maxsize)

def gen_short_id(long_id):
    return number_converter.encode(long_id)

def get_long_id(short_id):
    return number_converter.decode(short_id)



@app.route('/')
def home():

    return render_template('home.html')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    if request.method =='POST':
        text = request.form.get('text')
        password = request.form.get('password')

        number = id_generator()
        dump = Bin(id=number,
                   dump=encrypt_dump(password,text),
                   date_created=datetime.datetime.utcnow())
        short_id = gen_short_id(number)

        db.session.add(dump)
        db.session.commit()
        return redirect(url_for('dump', identity=short_id))


@app.route('/dump/<identity>', methods=['GET','POST'])
def dump(identity):
    long_id = int(get_long_id(identity))
    dump = Bin.query.get_or_404(long_id)

    return render_template('decryption_page.html', identity=identity)


if __name__ == '__main__':

    app.run(debug=True)
