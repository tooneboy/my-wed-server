# 1. ใช้ระบบพื้นฐานเป็น Python เวอร์ชั่น 3.10
FROM python:3.10-slim

# 2. ตั้งโฟลเดอร์ทำงานหลักใน Container
WORKDIR /app

# 3. คัดลอกไฟล์จัดการไลบรารีเข้ามาก่อนเพื่อติดตั้ง
COPY requirements.txt requirements.txt

# 4. ติดตั้งไลบรารี (Flask) ที่ระบุไว้ในไฟล์
RUN pip install --no-cache-dir -r requirements.txt

# 5. คัดลอกซอร์สโค้ดทั้งหมดในโปรเจกต์ตามเข้าไป
COPY . .

# 6. เปิดช่องพอร์ต 5000 ของ Container
EXPOSE 5000

# 7. สั่งให้เปิดรันแอปด้วยคำสั่ง python app.py ทันทีเมื่อคอนเทนเนอร์ทำงาน
CMD ["python", "app.py"]