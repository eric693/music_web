"""
音樂補習班預約系統 - 主程式
Flask 後端，提供：
  - /                 → 模組化首頁（新）
  - /booking          → 學生預約網頁
  - /api/teachers     → 取得老師列表
  - /api/slots        → 取得可用時段
  - /api/book         → 送出預約
  - /admin            → 管理後台（查看所有預約）
  - /admin/api/...    → 管理 API
"""

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'music-school-secret-2024')

CORS(app)
db = SQLAlchemy(app)

# ─────────────────────────────────────────────
# 資料庫模型
# ─────────────────────────────────────────────

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), nullable=False)
    instrument  = db.Column(db.String(50), nullable=False)
    bio         = db.Column(db.Text, nullable=False)
    hourly_rate = db.Column(db.Integer, nullable=False, default=1000)
    is_active   = db.Column(db.Boolean, default=True)
    slots       = db.relationship('TimeSlot', backref='teacher', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'instrument': self.instrument,
            'bio': self.bio,
            'hourly_rate': self.hourly_rate,
        }


class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    id           = db.Column(db.Integer, primary_key=True)
    teacher_id   = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date         = db.Column(db.String(10), nullable=False)   # YYYY-MM-DD
    time         = db.Column(db.String(5),  nullable=False)   # HH:MM
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'date': self.date,
            'time': self.time,
            'is_available': self.is_available,
        }


class Course(db.Model):
    __tablename__ = 'courses'
    id       = db.Column(db.Integer, primary_key=True)
    group    = db.Column(db.String(50), nullable=False)
    name     = db.Column(db.String(100), nullable=False)
    price    = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'group': self.group,
            'name': self.name,
            'price': self.price,
        }


class Booking(db.Model):
    __tablename__ = 'bookings'
    id           = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(20), unique=True, nullable=False)
    teacher_id   = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    slot_id      = db.Column(db.Integer, db.ForeignKey('time_slots.id'), nullable=False)
    # 學生資料
    student_name    = db.Column(db.String(50), nullable=False)
    student_contact = db.Column(db.String(100), nullable=False)
    student_age     = db.Column(db.String(10))
    student_level   = db.Column(db.String(20))
    student_note    = db.Column(db.Text)
    # 課程（JSON 存多選）
    courses_json    = db.Column(db.Text, default='[]')
    total_price     = db.Column(db.Integer, default=0)
    # 狀態
    status          = db.Column(db.String(20), default='confirmed')   # confirmed / cancelled
    created_at      = db.Column(db.DateTime, default=datetime.now)

    teacher = db.relationship('Teacher', backref='bookings')
    slot    = db.relationship('TimeSlot', backref='booking')

    def to_dict(self):
        return {
            'id': self.id,
            'booking_code': self.booking_code,
            'teacher': self.teacher.name if self.teacher else '',
            'instrument': self.teacher.instrument if self.teacher else '',
            'date': self.slot.date if self.slot else '',
            'time': self.slot.time if self.slot else '',
            'student_name': self.student_name,
            'student_contact': self.student_contact,
            'student_age': self.student_age,
            'student_level': self.student_level,
            'student_note': self.student_note,
            'courses': json.loads(self.courses_json or '[]'),
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


# ─────────────────────────────────────────────
# 靜態頁面
# ─────────────────────────────────────────────

@app.route('/')
def index():
    """模組化首頁"""
    return send_from_directory('static', 'index.html')

@app.route('/booking')
def booking():
    """學生預約頁面"""
    return send_from_directory('static', 'booking.html')

@app.route('/admin')
def admin():
    """管理後台"""
    return send_from_directory('static', 'admin.html')


# ─────────────────────────────────────────────
# 公開 API（學生用）
# ─────────────────────────────────────────────

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    teachers = Teacher.query.filter_by(is_active=True).all()
    return jsonify([t.to_dict() for t in teachers])


@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.filter_by(is_active=True).order_by(Course.group, Course.id).all()
    # 依 group 分組
    groups = {}
    for c in courses:
        if c.group not in groups:
            groups[c.group] = []
        groups[c.group].append(c.to_dict())
    result = [{'group': g, 'items': items} for g, items in groups.items()]
    return jsonify(result)


@app.route('/api/slots', methods=['GET'])
def get_slots():
    teacher_id = request.args.get('teacher_id', type=int)
    date = request.args.get('date')          # YYYY-MM-DD
    days_ahead = request.args.get('days', 14, type=int)

    query = TimeSlot.query.filter_by(is_available=True)
    if teacher_id:
        query = query.filter_by(teacher_id=teacher_id)

    today = datetime.now().date()
    end   = today + timedelta(days=days_ahead)

    if date:
        slots = query.filter_by(date=date).order_by(TimeSlot.time).all()
    else:
        # 回傳未來 days_ahead 天有空位的日期列表
        slots = query.filter(
            TimeSlot.date >= str(today),
            TimeSlot.date <= str(end)
        ).order_by(TimeSlot.date, TimeSlot.time).all()

    return jsonify([s.to_dict() for s in slots])


@app.route('/api/book', methods=['POST'])
def create_booking():
    data = request.get_json()
    if not data:
        return jsonify({'error': '無效的請求格式'}), 400

    # 必填檢查
    required = ['teacher_id', 'slot_id', 'student_name', 'student_contact']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'缺少必填欄位：{field}'}), 400

    # 確認時段可用
    slot = TimeSlot.query.get(data['slot_id'])
    if not slot or not slot.is_available:
        return jsonify({'error': '此時段已被預約，請選擇其他時段'}), 409

    # 確認老師存在
    teacher = Teacher.query.get(data['teacher_id'])
    if not teacher:
        return jsonify({'error': '找不到老師資料'}), 404

    # 計算費用
    courses = data.get('courses', [])
    total = sum(c.get('price', 0) for c in courses)

    # 產生預約編號
    booking_code = 'MU' + datetime.now().strftime('%m%d') + str(Booking.query.count() + 1001)

    booking = Booking(
        booking_code=booking_code,
        teacher_id=data['teacher_id'],
        slot_id=data['slot_id'],
        student_name=data['student_name'],
        student_contact=data['student_contact'],
        student_age=data.get('student_age', ''),
        student_level=data.get('student_level', ''),
        student_note=data.get('student_note', ''),
        courses_json=json.dumps(courses, ensure_ascii=False),
        total_price=total,
        status='confirmed',
        created_at=datetime.now(),
    )

    slot.is_available = False
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        'success': True,
        'booking_code': booking_code,
        'booking': booking.to_dict()
    }), 201


# ─────────────────────────────────────────────
# 管理後台 API
# ─────────────────────────────────────────────

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def check_admin():
    pw = request.headers.get('X-Admin-Password') or request.args.get('pw')
    if pw != ADMIN_PASSWORD:
        abort(401)

@app.route('/admin/api/bookings', methods=['GET'])
def admin_get_bookings():
    check_admin()
    status = request.args.get('status')
    query  = Booking.query
    if status:
        query = query.filter_by(status=status)
    bookings = query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])


@app.route('/admin/api/bookings/<int:bid>/cancel', methods=['POST'])
def admin_cancel_booking(bid):
    check_admin()
    booking = Booking.query.get_or_404(bid)
    booking.status = 'cancelled'
    if booking.slot:
        booking.slot.is_available = True
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/teachers', methods=['GET'])
def admin_get_teachers():
    check_admin()
    teachers = Teacher.query.all()
    return jsonify([t.to_dict() for t in teachers])


@app.route('/admin/api/teachers', methods=['POST'])
def admin_add_teacher():
    check_admin()
    data = request.get_json()
    teacher = Teacher(
        name=data['name'],
        instrument=data['instrument'],
        bio=data.get('bio', ''),
        hourly_rate=data.get('hourly_rate', 1000),
        is_active=True,
    )
    db.session.add(teacher)
    db.session.commit()
    # 自動建立未來 14 天時段
    _generate_slots(teacher.id, data.get('times', ['10:00','14:00','16:00','19:00']))
    return jsonify(teacher.to_dict()), 201


@app.route('/admin/api/teachers/<int:tid>', methods=['DELETE'])
def admin_delete_teacher(tid):
    check_admin()
    teacher = Teacher.query.get_or_404(tid)
    teacher.is_active = False
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/slots', methods=['POST'])
def admin_add_slot():
    check_admin()
    data = request.get_json()
    slot = TimeSlot(
        teacher_id=data['teacher_id'],
        date=data['date'],
        time=data['time'],
        is_available=True,
    )
    db.session.add(slot)
    db.session.commit()
    return jsonify(slot.to_dict()), 201


@app.route('/admin/api/slots/<int:sid>', methods=['DELETE'])
def admin_delete_slot(sid):
    check_admin()
    slot = TimeSlot.query.get_or_404(sid)
    db.session.delete(slot)
    db.session.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# 工具函式
# ─────────────────────────────────────────────

def _generate_slots(teacher_id, times, days_ahead=14):
    today = datetime.now().date()
    for offset in range(1, days_ahead + 1):
        date = today + timedelta(days=offset)
        if date.weekday() == 6:   # 週日不排課
            continue
        for t in times:
            existing = TimeSlot.query.filter_by(teacher_id=teacher_id, date=str(date), time=t).first()
            if not existing:
                slot = TimeSlot(teacher_id=teacher_id, date=str(date), time=t, is_available=True)
                db.session.add(slot)
    db.session.commit()


def seed():
    """首次啟動時建立範例資料"""
    if Teacher.query.count() > 0:
        return

    teachers_data = [
        {'name': '陳雅婷', 'instrument': '鋼琴',  'bio': '國立音樂學院鋼琴系畢業，10年教學資歷，輔導多名學生通過檢定。', 'hourly_rate': 1200},
        {'name': '林建宏', 'instrument': '吉他',  'bio': '旅美爵士吉他手，Berklee 進修，專精木吉他、電吉他、烏克麗麗。', 'hourly_rate': 1000},
        {'name': '王怡婷', 'instrument': '小提琴','bio': '國際音樂大賽得獎，師承歐洲演奏家，初學至進階皆可。', 'hourly_rate': 1500},
    ]
    times = ['10:00', '14:00', '16:00', '19:00']
    for d in teachers_data:
        t = Teacher(**d, is_active=True)
        db.session.add(t)
        db.session.flush()
        _generate_slots(t.id, times)

    courses_data = [
        ('體驗課',   '初次體驗課（60分鐘）',     500),
        ('基礎課程', '基礎入門（60分鐘）',        900),
        ('基礎課程', '基礎進階（60分鐘）',       1000),
        ('進階課程', '進階技巧（60分鐘）',       1200),
        ('進階課程', '考試/比賽備考（60分鐘）',  1500),
        ('樂理與視唱','音樂理論（45分鐘）',       800),
    ]
    for group, name, price in courses_data:
        db.session.add(Course(group=group, name=name, price=price))

    db.session.commit()
    print('範例資料建立完成')


# ─────────────────────────────────────────────
# 啟動
# ─────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    with app.app_context():
        db.create_all()
        seed()
    print('\n  模組化首頁：  http://localhost:5000')
    print('  學生預約頁面：http://localhost:5000/booking')
    print('  管理後台：    http://localhost:5000/admin')
    print(f'  管理密碼：    {ADMIN_PASSWORD}\n')
    app.run(debug=True, port=5000)