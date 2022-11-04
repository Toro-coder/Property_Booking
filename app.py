from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import uuid
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename

import urllib.request

UPLOAD_FOLDER =  'C:/Users/KIM/PycharmProjects/salesProperty/pictures/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
bcrypt = Bcrypt(app)
mail = Mail(app)


app.secret_key = 'Cindy1648'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_ROOT'] = '3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cindy1648'
app.config['MYSQL_DB'] = 'hostels'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "cynthiajepkemei11@gmail.com"
app.config["MAIL_PASSWORD"] = "36662695"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        _json = request.json
        _username = _json['username']
        _passw = _json['passw']

        if _username and _passw:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM register WHERE username = % s AND passw = % s', (_username, _passw,))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return jsonify({'message': 'Logged in successfully'})
            else:
                resp = jsonify({'message': 'Check your password please'})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({'message': 'Invalid Credentials'})
            resp.status_code = 400
            return resp
    except Exception as e:
        print(e)


@app.route('/forgot_password', methods=["POST", "GET "])
def forgot_password():
    try:
        email = request.form['email']
        token = str(uuid.uuid4())
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM register WHERE email = % s', (email,))
        account = cursor.fetchone()
        if account:
            # msg = Message(subject="Forgot password request", sender="cynthiatoro@gmail.com", recipients=email)
            # msg.body = render_template('sent.html', token=token, account=account)
            # mail.send(msg)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE register SET token = % s WHERE email = % s', (token, email))
            mysql.connection.commit()
            cursor.close()
            return "Email already sent to your email"

        else:
            return "Email do not match"

    except Exception as e:
        print(e)


@app.route('/reset/<token>', methods=['POST', 'GET'])
def reset(token):
    try:
        _json = request.json
        passw = _json['passw']
        confirm_passw = _json['confirm_passw']
        token1 = str(uuid.uuid4())
        if passw != confirm_passw:
            return jsonify({"message": "Password and confirm do not match"})
        passw = bcrypt.generate_password_hash(passw)
        confirm_passw = bcrypt.generate_password_hash(confirm_passw)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM register WHERE token = % s', (token,))
        user = cursor.fetchone()
        if user:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE register SET token = % s, passw = % s, confirm_passw = % s WHERE token = % s',
                           (token1, passw, confirm_passw, token))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "your password has been successfully updated"})
        else:
            return jsonify({"message": "Invalid token"})

    except Exception as e:
        print(e)


# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        _json = request.json
        _first_name = _json['first_name']
        _last_name = _json['last_name']
        _username = _json['username']
        _email = _json['email']
        _passw = _json['passw']
        _confirm_passw = _json['confirm_passw']
        token = str(uuid.uuid4())

        if _first_name and _last_name and _username and _email and _passw and _confirm_passw and token:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM register WHERE username = % s and email = % s', (_username, _email,))
            account = cursor.fetchone()
            print('hereeee')
            if account:
                return jsonify({'message': 'Account already exists!'})
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
                return jsonify({'message': 'invalid email'})
            elif not re.match(r'[A-Za-z0-9]+', _username):
                return jsonify({'message': 'username should contain characters and numbers'})
            elif not re.match(r'[A-Za-z0-9#?!@$%^&*-]+', _passw):
                return jsonify({'message': 'password should contain characters,numbers and special characters'})
            elif _passw != _confirm_passw:
                return jsonify({'message': 'your password and confirm password should match'})
            elif not _first_name or not _last_name or not _username or not _email or not _passw or not _confirm_passw:
                return jsonify({'message': 'please fill the form'})
            else:
                cursor.execute('INSERT INTO register VALUES(NULL, % s, % s, % s, % s, % s, % s, % s)',
                               (_first_name, _last_name, _username, _email, _passw, _confirm_passw, token))
                mysql.connection.commit()
                return jsonify({'message': 'You have successfully Registered'})
    except Exception as e:
        print(e)


@app.route('/property', methods=['POST', 'GET'])
def propery():
    try:
        _json = request.json
        file = request.files
        _title = _json['title']
        _category = _json['category']
        _house_type = _json['house_type']
        _amenity = _json['amenity']
        _county = _json['county']
        _price = _json['price']
        _image = file['image']

        if _title and _category and _house_type and _amenity and _county and _price and _image:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM property WHERE title = % s', (_title,))
            account = cursor.fetchone()
            if account:
                return jsonify({'message': 'The property already exists'})
            elif _category != 'commercial' and _category != 'residential':
                return jsonify({'message': 'System requires you to define property as residential or commercial'})
            elif _house_type != 'single room' and _house_type != 'bed sitter' and _house_type != 'studio':
                return jsonify({'message': 'The property should be a single room or a bed sitter or a studio'})
            elif not _title or not _category or not _house_type or not _amenity or not _county or not _price:
                return jsonify({'message': 'please enter the necessary credentials'})
            # elif _image:
            #     _image.save(secure_filename(_image.filename))
            #     return jsonify({'message': 'File successfully uploaded'})

            files = request.files.getlist('files[]')
            for _image in files:
                if _image and allowed_file(_image.filename):
                    filename = secure_filename(_image.filename)
                    _image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    success = True
                else:
                    return jsonify({"message": "file type not allowed"})

                if success:
                    resp = jsonify({'message': 'File successfully uploaded'})
                    resp.status_code = 201
                    return resp
            else:
                cursor.execute('INSERT INTO property VALUES (NULL, % s, % s, % s, % s, % s, % s, % s)',
                               (_title, _category, _house_type, _amenity, _county, _price, _image))
                mysql.connection.commit()
                return jsonify({'message': 'Congratulations, You have successfully added a property'})

    except Exception as e:
        print(e)


@app.route('/upload_image', methods=['POST', 'GET'])
def upload_image():
    if 'image' not in request.files:
        resp = jsonify({"message": "No file part in the request"})
        resp.status_code = 400
        return resp

    image = request.files['image']
    property_id = request.form['property_id']
    if image.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        url_pic = UPLOAD_FOLDER + filename
        print(url_pic)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO images VALUES (NULL,% s, % s)',
                       (url_pic, property_id))
        mysql.connection.commit()
        resp = jsonify({'message' : 'File success uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file type are checked'})
        resp.status_code = 400
        return resp


@app.route('/search', methods=['POST', 'GET'])
def search():
    _json = request.json
    _title = _json['title']
    if _title:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM property WHERE title = % s', (_title,))
        account = cursor.fetchall()
        if account:
            return jsonify(account)
        else:
            return jsonify({'message': 'The property does not exist'})


if __name__ == '__main__':
    app.run(debug=True)
