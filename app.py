from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

# MySQL Configuration
mysql = MySQL(app)


# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        colums = [col[0] for col in cursor.description]
        user_row = cursor.fetchone()
        cursor.close()

        if user_row:
            user = dict(zip(colums, user_row))
        else:
            user = None

        try:
            if user and bcrypt.checkpw(password, user.get("password").encode('utf-8')):
                session['loggedin'] = True
                session['userid'] = user["userid"]
                session['username'] = user["username"]
                session['email'] = user["email"]
                return redirect(url_for('index'))
            else:
                flash("Email hoặc mật khẩu không đúng!")
        except Exception as e:
            print("Lỗi ở đây là:", e)
            flash("Email của bạn không đúng!")

    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
                       (username, email, hashed))
        mysql.connection.commit()
        cursor.close()

        flash("Đăng ký thành công! Vui lòng đăng nhập.")
        return redirect(url_for('login'))

    return render_template('auth/register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Profile Routes
@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (session['userid'],))
        user = cursor.fetchone()
        cursor.close()

        return render_template('profile.html', user=user)
    return redirect(url_for('login'))


# Calendar Routes
@app.route('/calendar')
def calendar():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE user_id=%s", (session['userid'],))
        events = cursor.fetchall()
        cursor.close()

        return render_template('calendar.html', events=events)
    return redirect(url_for('login'))


@app.route('/add_event', methods=['POST'])
def add_event():
    if 'loggedin' in session:
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO events(user_id, title, start, end) VALUES(%s, %s, %s, %s)",
                       (session['userid'], title, start, end))
        mysql.connection.commit()
        cursor.close()

        flash("Sự kiện đã được thêm!")
    return redirect(url_for('calendar'))


# Notes Routes
@app.route('/notes')
def notes():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM notes WHERE user_id=%s", (session['userid'],))
        notes = cursor.fetchall()
        cursor.close()

        return render_template('notes.html', notes=notes)
    return redirect(url_for('login'))


@app.route('/add_note', methods=['POST'])
def add_note():
    if 'loggedin' in session:
        title = request.form['title']
        content = request.form['content']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO notes(user_id, title, content) VALUES(%s, %s, %s)",
                       (session['userid'], title, content))
        mysql.connection.commit()
        cursor.close()

        flash("Ghi chú đã được thêm!")
    return redirect(url_for('notes'))


if __name__ == '__main__':
    app.run(port=5001, debug=True)