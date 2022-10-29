from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import urllib.request

UPLOAD_FOLDER = 'C:/uploads'

app = Flask(__name__)

app.secret_key = 'Cindy1648'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Cindy1648'
app.config['MYSQL_DB'] = 'hostels'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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

        if _first_name and _last_name and _username and _email and _passw and _confirm_passw:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM register WHERE username = % s and email = % s', (_username, _email,))
            account = cursor.fetchone()
            if account:
                return jsonify({'message': 'Account already exists!'})
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', _email):
                return jsonify({'message': 'invalid email'})
            elif not re.match(r'[A-Za-z0-9]+', _username):
                return jsonify({'message': 'username should contain characters and numbers'})
            elif not re.match(r'[A-Za-z0-9#?!@$%^&*-]+', _passw):
                return jsonify({'message': 'password should contain characters,numbers and special characters'})
            elif len(_passw) != len(_confirm_passw):
                return jsonify({'message': 'your password and confirm password should match'})
            elif not _first_name or not _last_name or not _username or not _email or not _passw or not _confirm_passw:
                return jsonify({'message': 'please fill the form'})
            else:
                cursor.execute('INSERT INTO register VALUES(NULL, % s, % s, % s, % s, % s, % s)',
                               (_first_name, _last_name, _username, _email, _passw, _confirm_passw))
                mysql.connection.commit()
                return jsonify({'message': 'You have successfully Registered'})
    except Exception as e:
        print(e)


@app.route('/property', methods=['POST', 'GET'])
def propery():
    try:
        _json = request.json
        _title = _json['title']
        _category = _json['category']
        _house_type = _json['house_type']
        _amenity = _json['amenity']
        _county = _json['county']
        _price = _json['price']
        # _image = _json['image']

        if '_title' and '_category' and '_house_type' and '_amenity' and '_county' and '_price':
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

            else:
                cursor.execute('INSERT INTO property VALUES (NULL, % s, % s, % s, % s, % s, % s)',
                               (_title, _category, _house_type, _amenity, _county, _price, ))
                mysql.connection.commit()
                return jsonify({'message': 'Congratulations, You have successfully added a property'})

    except Exception as e:
        print(e)

    # msg = ''
    # if request.method == 'POST' and 'title' in request.form and 'category' in request.form and 'house_type' \
    #         in request.form and 'amenity' in request.form and 'county' in request.form and 'price ' in 'image' in request.form:
    #     print("hellooo")
    #     title = request.form['title']
    #     category = request.form['category']
    #     house_type = request.form['house_type']
    #     amenity = request.form['amenity']
    #     county = request.form['county']
    #     price = request.form['price']
    #     image = request.form['image']
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT * FROM property WHERE title = % s', (title,))
    #     account = cursor.fetchone()
    #
    #     if account:
    #         msg = 'The property already exists'
    #     elif category != 'commercial' and category != 'residential':
    #         msg = 'System requires you to define property as residential or commercial'
    #     elif house_type != 'single room' or house_type != 'bed sitter' or house_type != 'studio':
    #         msg = 'The property should be a single room or a bed sitter or a studio'
    #     elif not title or not category or not house_type or not amenity or not county or not price or not image:
    #         msg = 'please enter the necessary credentials'
    #     else:
    #         cursor.execute('INSERT INTO property VALUES (NULL, % s, % s, % s, % s, % s, % s, % s)',
    #                        (title, category, house_type, amenity, county, price, image))
    #         mysql.connection.commit()
    #         msg = 'Congratulations, You have successfully added a property'
    #
    # elif request.method == 'POST':
    #     msg = 'Please fill out the form !'
    # return ( msg )


if __name__ == '__main__':
    app.run(debug=True)
