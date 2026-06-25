from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'my_secret_encryption_key_here'

# ฟังก์ชันสำหรับเชื่อมต่อ MySQL
def get_db_connection():
    return pymysql.connect(
        host='db',                # ต้องใส่คำว่า 'db' ตามชื่อ service ใน docker-compose
        user='root',              # ต้องเป็น 'root'
        password='your_password',  # ต้องตรงกับ MYSQL_ROOT_PASSWORD ใน docker-compose
        database='my_database',   # ต้องตรงกับ MYSQL_DATABASE ใน docker-compose
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def hello():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    # ลองทดสอบเชื่อมต่อฐานข้อมูลเพื่อส่งสถานะไปแสดงที่หน้าเว็บ
    db_status = "รอการเชื่อมต่อ..."
    try:
        connection = get_db_connection()
        connection.close()
        db_status = "เชื่อมต่อฐานข้อมูล MySQL สำเร็จแล้ว! 🎉"
    except Exception as e:
        db_status = f"เชื่อมต่อล้มเหลว: {e}"

    # ส่งค่า db_status ไปที่หน้าเว็บ (คุณสามารถนำไปแสดงใน index.html ได้)
    return render_template('index.html', db_status=db_status)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        # 1. ดึงการเชื่อมต่อฐานข้อมูล
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 2. เขียนคำสั่ง SQL เพื่อค้นหา Username และ Password ที่ตรงกัน
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user_record = cursor.fetchone()
            
        connection.close()
        
        # 3. ตรวจสอบผลลัพธ์
        if user_record:
            # บันทึก Username ที่ดึงมาจากฐานข้อมูลลงใน Session
            session['username'] = user_record['username']
            return redirect(url_for('dashboard'))
        else:
            return "Username หรือ Password ไม่ถูกต้อง <a href='/'>ลองใหม่</a>"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {e} <a href='/'>ลองใหม่</a>"

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('hello'))
        
    try:
        # 1. เชื่อมต่อฐานข้อมูลเพื่อดึงข้อมูลรายการทั้งหมดมาแสดงที่เว็บหลัก
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM main_items ORDER BY created_at DESC"
            cursor.execute(sql)
            items = cursor.fetchall()  # ดึงข้อมูลรายการทั้งหมดออกมาเป็น List
        connection.close()
        
        # 2. ส่งค่าข้อมูล items ไปเรนเดอร์ที่หน้าจอหลัก dashboard.html
        return render_template('dashboard.html', user=session['username'], items=items)
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการโหลดข้อมูลหน้าหลัก: {e}"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('hello'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)