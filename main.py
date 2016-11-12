import datetime
import sys
import json

from random import SystemRandom

from baseconv import BaseConverter

from flask import Flask, render_template, request, redirect,url_for,make_response,session
from flask_sqlalchemy import SQLAlchemy
from setup import DATABASE_URL

from crypto import encrypt_dump, decrypt_dump

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'N0\xbeW\xfau\xc3O<\x80F\xb9\x95\x1a\x1b\x07'

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



def gen_token(long_id):
    s = Serializer(app.config['SECRET_KEY'],expires_in=30)
    token = s.dumps({'id': long_id})
    return token

def confirm_token(token,long_id):
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
def home():
    return render_template('home.html')


@app.route('/encrypt', methods=['POST'])
def encrypt():
    if request.method =='POST':
        ## Need to put some exceptions here to validate data
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

    if request.method == 'GET':

        try:
            token = session['token']
        except:
            token = None

        if token != None and confirm_token(token,long_id):
            session['token'] = None
            return redirect(url_for('dump', identity=gen_short_id(long_id)))

        else:
            return render_template('decryption_page.html', identity=identity)

    if request.method == 'POST':

        data = decrypt_dump(request.form.get('password'), dump.dump)

        if data:
            session['token'] = gen_token(long_id)
            ## this should be redirect
            # however i need to find a better to do this
            return render_template('data_page.html',data=data)
        else:
            return redirect(url_for('dump', identity=gen_short_id(long_id)))


if __name__ == '__main__':

    app.run(debug=True)
