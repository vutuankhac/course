import MySQLdb
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

from config import Config

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
                session['userid'] = user["id"]
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


# Schedules Routes
@app.route('/schedule/create', methods=['GET', 'POST'])
def schedule_create():
    if 'loggedin' in session:
        if request.method == 'POST':
            tenHoatDong = request.form['tenHoatDong']
            thuTrongTuan = request.form['thuTrongTuan']
            thoiGianBatDau = request.form['thoiGianBatDau']
            thoiGianKetThuc = request.form['thoiGianKetThuc']
            user_id = session['userid']

            try:
                cursor = mysql.connection.cursor()

                # Câu lệnh SQL với tham số parameterized để tránh SQL injection
                query = """
                INSERT INTO schedules
                (activity_name, day_of_week, start_time, end_time, user_id)
                VALUES (%s, %s, %s, %s, %s)
                """

                # Thực thi câu lệnh với các giá trị từ form
                cursor.execute(query,
                               (tenHoatDong, thuTrongTuan, thoiGianBatDau, thoiGianKetThuc, user_id))

                # Commit thay đổi vào database
                mysql.connection.commit()

                # Đóng cursor
                cursor.close()

                flash('Thêm hoạt động thành công!', 'success')
                return redirect(url_for('schedule_list'))

            except Exception as e:
                # Xử lý lỗi nếu có
                mysql.connection.rollback()
                flash(f'Có lỗi xảy ra: {str(e)}', 'error')
                return redirect(url_for('index'))

        return render_template('schedules/create.html')
    return redirect(url_for('login'))


@app.route('/schedule/list', methods=['GET'])
def schedule_list():
    if 'loggedin' in session:
        # Lấy user_id từ session
        user_id = session['userid']

        # Kết nối database và lấy dữ liệu
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query lấy tất cả schedule của user hiện tại
        query = """
            SELECT * FROM schedules 
            WHERE user_id = %s
            ORDER BY start_time ASC
        """

        cursor.execute(query, (user_id,))
        schedules = cursor.fetchall()

        # Đóng kết nối
        cursor.close()

        print("schedules", schedules)
        # Truyền dữ liệu vào template
        return render_template('schedules/list.html', schedules=schedules)

    return redirect(url_for('login'))


@app.route('/schedule/edit', methods=['GET', 'POST'])
def schedule_edit():
    if 'loggedin' in session:
        if request.method == 'POST':
            tenHoatDong = request.form['tenHoatDong']
            thuTrongTuan = request.form['thuTrongTuan']
            thoiGianBatDau = request.form['thoiGianBatDau']
            thoiGianKetThuc = request.form['thoiGianKetThuc']
            schedule_id = request.form['schedule_id']
            user_id = session['userid']

            try:
                cursor = mysql.connection.cursor()

                # Câu lệnh SQL với tham số parameterized để tránh SQL injection
                query = """
                    UPDATE schedules
                    SET activity_name = %s,
                        day_of_week = %s,
                        start_time = %s,
                        end_time = %s,
                        user_id = %s
                    WHERE schedule_id = %s
                """

                # Thực thi câu lệnh với các giá trị từ form
                cursor.execute(query, (
                    tenHoatDong,
                    thuTrongTuan,
                    thoiGianBatDau,
                    thoiGianKetThuc,
                    user_id,
                    schedule_id  # Thêm schedule_id vào cuối
                ))

                # Commit thay đổi vào database
                mysql.connection.commit()

                # Đóng cursor
                cursor.close()

                flash('Cập nhật hoạt động thành công!', 'success')
                return redirect(url_for('schedule_list'))

            except Exception as e:
                # Xử lý lỗi nếu có
                mysql.connection.rollback()
                flash(f'Có lỗi xảy ra: {str(e)}', 'error')
                return redirect(url_for('index'))

        user_id = session['userid']
        schedule_id = request.args.get('schedule_id', default='', type=str)
        # Kết nối database và lấy dữ liệu
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query lấy tất cả schedule của user hiện tại
        query = """
            SELECT * FROM schedules 
            WHERE user_id = %s AND schedule_id = %s
            ORDER BY start_time ASC
        """

        cursor.execute(query, (user_id, schedule_id))
        schedule = cursor.fetchone()

        return render_template('schedules/edit.html', schedule=schedule)
    return redirect(url_for('login'))


@app.route('/schedule/delete/<int:schedule_id>', methods=['GET'])
def schedule_delete(schedule_id):
    if 'loggedin' in session:
        user_id = session['userid']

        cursor = mysql.connection.cursor()
        query = "DELETE FROM schedules WHERE schedule_id = %s AND user_id = %s"
        cursor.execute(query, (schedule_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('schedule_list'))

    return redirect(url_for('login'))


@app.route('/game')
def game():
    return render_template('game/index.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)

@app.route('/game/score', methods=['GET', 'POST'])
def game_score():
    if 'loggedin' in session:
        if request.method == 'POST':
            diemSo = request.form['diemSo']
            user_id = session['userid']

            try:
                cursor = mysql.connection.cursor()

                # Câu lệnh SQL với tham số parameterized để tránh SQL injection
                query = """
                            SELECT * FROM score_game 
                            WHERE user_id = %s
                        """

                cursor.execute(query, (user_id))
                score_game_record = cursor.fetchone()

                if score_game_record:
                    # Câu lệnh SQL với tham số parameterized để tránh SQL injection
                    query = """
                        UPDATE score_game
                        SET score = %s,
                            updated_date = now()
                        WHERE user_id = %s
                    """

                    # Thực thi câu lệnh với các giá trị từ form
                    cursor.execute(query, (
                        tenHoatDong,
                        thuTrongTuan,
                        thoiGianBatDau,
                        thoiGianKetThuc,
                        user_id,
                        schedule_id  # Thêm schedule_id vào cuối
                    ))

                # Commit thay đổi vào database
                mysql.connection.commit()

                # Đóng cursor
                cursor.close()

                flash('Cập nhật hoạt động thành công!', 'success')
                return redirect(url_for('schedule_list'))

            except Exception as e:
                # Xử lý lỗi nếu có
                mysql.connection.rollback()
                flash(f'Có lỗi xảy ra: {str(e)}', 'error')
                return redirect(url_for('index'))

        user_id = session['userid']
        schedule_id = request.args.get('schedule_id', default='', type=str)
        # Kết nối database và lấy dữ liệu
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query lấy tất cả schedule của user hiện tại
        query = """
            SELECT * FROM schedules 
            WHERE user_id = %s AND schedule_id = %s
            ORDER BY start_time ASC
        """

        cursor.execute(query, (user_id, schedule_id))
        schedule = cursor.fetchone()

        return render_template('schedules/edit.html', schedule=schedule)
    return redirect(url_for('login'))
