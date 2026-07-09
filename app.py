from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'my_secret_encryption_key_here'

# ==========================================
# ฟังก์ชันสำหรับเชื่อมต่อ MySQL
# ==========================================
def get_db_connection():
    return pymysql.connect(
        host='db',                
        user='root',              
        password='your_password',  
        database='my_database',   
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================================
# Route: หน้าแรก (ทดสอบการเชื่อมต่อ)
# ==========================================
@app.route('/')
def hello():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    db_status = "รอการเชื่อมต่อ..."
    try:
        connection = get_db_connection()
        connection.close()
        db_status = "เชื่อมต่อฐานข้อมูล MySQL สำเร็จแล้ว! 🎉"
    except Exception as e:
        db_status = f"เชื่อมต่อล้มเหลว: {e}"

    return render_template('index.html', db_status=db_status)

# ==========================================
# Route: ระบบ Login
# ==========================================
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            user_record = cursor.fetchone()
            
        connection.close()
        
        if user_record:
            session['username'] = user_record['username']
            return redirect(url_for('dashboard'))
        else:
            return "Username หรือ Password ไม่ถูกต้อง <a href='/'>ลองใหม่</a>"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการตรวจสอบข้อมูล: {e} <a href='/'>ลองใหม่</a>"

# ==========================================
# Route: หน้า Dashboard หลัก
# ==========================================
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('hello'))
        
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM main_items ORDER BY created_at DESC"
            cursor.execute(sql)
            items = cursor.fetchall()
        connection.close()
        
        return render_template('dashboard.html', user=session['username'], items=items)
        
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการโหลดข้อมูลหน้าหลัก: {e}"

# ==========================================
# Route: ระบบ Logout
# ==========================================
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('hello'))
    
# ==========================================
# Route: ฟังก์ชันสำหรับเพิ่มข้อมูลใหม่ (Add)
# ==========================================
@app.route('/add', methods=['POST'])
def add_item():
    if 'username' not in session:
        return redirect(url_for('hello'))
        
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO main_items (title, description, status) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, description, status))
        connection.commit()
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเพิ่มข้อมูล: {e}"
    finally:
        connection.close()
        
    return redirect(url_for('dashboard'))

# ==========================================
# Route: ฟังก์ชันสำหรับแก้ไขข้อมูล (Edit)
# ==========================================
@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'username' not in session:
        return redirect(url_for('hello'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "UPDATE main_items SET title=%s, description=%s, status=%s WHERE id=%s"
                cursor.execute(sql, (title, description, status, item_id))
            connection.commit()
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {e}"
        finally:
            connection.close()
            
        return redirect(url_for('dashboard'))
        
    else:
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM main_items WHERE id=%s"
                cursor.execute(sql, (item_id,))
                item = cursor.fetchone()
        except Exception as e:
             return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}"
        finally:
            connection.close()
            
        return render_template('edit.html', item=item)

# ==========================================
# Route: ฟังก์ชันสำหรับลบข้อมูล (Delete)
# ==========================================
@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    if 'username' not in session:
        return redirect(url_for('hello'))
        
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # คำสั่ง SQL สำหรับลบข้อมูลตาม ID ที่ส่งมา
            sql = "DELETE FROM main_items WHERE id=%s"
            cursor.execute(sql, (item_id,))
        # ยืนยันการลบข้อมูล
        connection.commit()
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการลบข้อมูล: {e}"
    finally:
        connection.close()
        
    # ลบเสร็จแล้วให้รีไดเรกต์กลับไปหน้า Dashboard ทันที
    return redirect(url_for('dashboard'))

# ==========================================
# คำสั่งรันเซิร์ฟเวอร์ (ต้องอยู่ล่างสุดเสมอ)
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
# ==========================================
# คำสั่งรันเซิร์ฟเวอร์ (ต้องอยู่ล่างสุดเสมอ)
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)