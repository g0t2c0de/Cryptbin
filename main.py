from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from setup import DATABASE_URL

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




@app.route('/')
def home():
    return render_template('home.html')



@app.route('/decrypt/<identity>', methods=['GET','POST'])
def decrypt(identity):
    return render_template('decrypted_page.html')



if __name__ == '__main__':

    app.run(debug=True)
