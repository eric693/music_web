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


class Student(db.Model):
    __tablename__ = 'students'
    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.String(20), unique=True, nullable=False)
    name            = db.Column(db.String(50), nullable=False)
    contact         = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(100))
    age             = db.Column(db.Integer)
    level           = db.Column(db.String(20))
    instrument      = db.Column(db.String(50))
    parent_name     = db.Column(db.String(50))
    parent_contact  = db.Column(db.String(100))
    address         = db.Column(db.Text)
    note            = db.Column(db.Text)
    enrollment_date = db.Column(db.DateTime, default=datetime.now)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'contact': self.contact,
            'email': self.email,
            'age': self.age,
            'level': self.level,
            'instrument': self.instrument,
            'parent_name': self.parent_name,
            'parent_contact': self.parent_contact,
            'address': self.address,
            'note': self.note,
            'enrollment_date': self.enrollment_date.strftime('%Y-%m-%d') if self.enrollment_date else '',
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount          = db.Column(db.Integer, nullable=False)
    payment_date    = db.Column(db.DateTime, default=datetime.now)
    payment_method  = db.Column(db.String(20))  # cash, transfer, credit_card
    status          = db.Column(db.String(20), default='paid')  # paid, pending, cancelled
    month           = db.Column(db.String(7))  # YYYY-MM
    note            = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship('Student', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'amount': self.amount,
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else '',
            'payment_method': self.payment_method,
            'status': self.status,
            'month': self.month,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Expense(db.Model):
    __tablename__ = 'expenses'
    id              = db.Column(db.Integer, primary_key=True)
    category        = db.Column(db.String(50), nullable=False)
    amount          = db.Column(db.Integer, nullable=False)
    expense_date    = db.Column(db.DateTime, default=datetime.now)
    description     = db.Column(db.Text)
    note            = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'expense_date': self.expense_date.strftime('%Y-%m-%d') if self.expense_date else '',
            'description': self.description,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id              = db.Column(db.Integer, primary_key=True)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date            = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    check_time      = db.Column(db.String(5), nullable=False)   # HH:MM
    status          = db.Column(db.String(20), nullable=False)  # present, late, absent, leave
    late_minutes    = db.Column(db.Integer, default=0)
    course          = db.Column(db.String(50))
    note            = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    student = db.relationship('Student', backref='attendance_records')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'date': self.date,
            'check_time': self.check_time,
            'status': self.status,
            'late_minutes': self.late_minutes,
            'course': self.course,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Exam(db.Model):
    __tablename__ = 'exams'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    date            = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    max_score       = db.Column(db.Integer, default=100)
    pass_score      = db.Column(db.Integer, default=60)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'max_score': self.max_score,
            'pass_score': self.pass_score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Grade(db.Model):
    __tablename__ = 'grades'
    id              = db.Column(db.Integer, primary_key=True)
    exam_id         = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id      = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    score           = db.Column(db.Integer, nullable=False)
    rank            = db.Column(db.Integer)
    trend           = db.Column(db.String(10))  # up, down, stable
    note            = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.now)

    exam = db.relationship('Exam', backref='grades')
    student = db.relationship('Student', backref='grades')

    def to_dict(self):
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'exam_name': self.exam.name if self.exam else '',
            'exam_date': self.exam.date if self.exam else '',
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'score': self.score,
            'rank': self.rank,
            'trend': self.trend,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Shift(db.Model):
    __tablename__ = 'shifts'
    id              = db.Column(db.Integer, primary_key=True)
    teacher_id      = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date            = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    start_time      = db.Column(db.String(5), nullable=False)   # HH:MM
    end_time        = db.Column(db.String(5), nullable=False)   # HH:MM
    course          = db.Column(db.String(100))
    created_at      = db.Column(db.DateTime, default=datetime.now)

    teacher = db.relationship('Teacher', backref='shifts')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else '',
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'course': self.course,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Substitute(db.Model):
    __tablename__ = 'substitutes'
    id                      = db.Column(db.Integer, primary_key=True)
    original_teacher_id     = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    substitute_teacher_id   = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    date                    = db.Column(db.String(10), nullable=False)
    time_slot               = db.Column(db.String(20), nullable=False)
    reason                  = db.Column(db.Text)
    status                  = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    created_at              = db.Column(db.DateTime, default=datetime.now)

    original_teacher = db.relationship('Teacher', foreign_keys=[original_teacher_id], backref='original_substitutes')
    substitute_teacher = db.relationship('Teacher', foreign_keys=[substitute_teacher_id], backref='substitute_shifts')

    def to_dict(self):
        return {
            'id': self.id,
            'original_teacher_id': self.original_teacher_id,
            'original_teacher_name': self.original_teacher.name if self.original_teacher else '',
            'substitute_teacher_id': self.substitute_teacher_id,
            'substitute_teacher_name': self.substitute_teacher.name if self.substitute_teacher else '',
            'date': self.date,
            'time_slot': self.time_slot,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


class Leave(db.Model):
    __tablename__ = 'leaves'
    id              = db.Column(db.Integer, primary_key=True)
    teacher_id      = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    leave_type      = db.Column(db.String(20), nullable=False)  # sick, personal, annual, other
    start_date      = db.Column(db.String(10), nullable=False)
    end_date        = db.Column(db.String(10), nullable=False)
    days            = db.Column(db.Integer, nullable=False)
    reason          = db.Column(db.Text)
    status          = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at      = db.Column(db.DateTime, default=datetime.now)

    teacher = db.relationship('Teacher', backref='leaves')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else '',
            'leave_type': self.leave_type,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'days': self.days,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
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
    """學生預約頁面"""
    return send_from_directory('static', 'booking.html')

@app.route('/admin')
def admin_login():
    """管理後台登入頁"""
    return send_from_directory('static', 'admin.html')

@app.route('/dashboard')
def dashboard():
    """模組管理首頁（需登入）"""
    return send_from_directory('static', 'index.html')

@app.route('/booking-admin')
def booking_admin():
    """預約管理頁面（iframe用）"""
    return send_from_directory('static', 'booking-admin.html')

@app.route('/teacher-mgmt')
def teacher_mgmt():
    """師生管理頁面（iframe用）"""
    return send_from_directory('static', 'teacher-mgmt.html')

@app.route('/finance')
def finance():
    """財務報表頁面（iframe用）"""
    return send_from_directory('static', 'finance.html')

@app.route('/accounting')
def accounting():
    """會計科目頁面（iframe用）"""
    return send_from_directory('static', 'accounting.html')

@app.route('/course-schedule')
def course_schedule():
    """課表系統頁面（iframe用）"""
    return send_from_directory('static', 'course-schedule.html')

@app.route('/ceo-report')
def ceo_report():
    """CEO每日報頁面（iframe用）"""
    return send_from_directory('static', 'ceo-report.html')

@app.route('/line-messages')
def line_messages():
    """LINE 訊息推播頁面（iframe用）"""
    return send_from_directory('static', 'line-messages.html')

@app.route('/line-notifications')
def line_notifications():
    """LINE 通知設定頁面（iframe用）"""
    return send_from_directory('static', 'line-notifications.html')

@app.route('/line-interactive')
def line_interactive():
    """LINE 互動功能頁面（iframe用）"""
    return send_from_directory('static', 'line-interactive.html')

@app.route('/website-design')
def website_design():
    """網站設計頁面（iframe用）"""
    return send_from_directory('static', 'website-design.html')

@app.route('/website-content')
def website_content():
    """內容管理頁面（iframe用）"""
    return send_from_directory('static', 'website-content.html')

@app.route('/online-booking')
def online_booking():
    """線上報名頁面（iframe用）"""
    return send_from_directory('static', 'online-booking.html')

@app.route('/attendance')
def attendance():
    """出席打卡頁面（iframe用）"""
    return send_from_directory('static', 'attendance.html')

@app.route('/grades')
def grades():
    """成績管理頁面（iframe用）"""
    return send_from_directory('static', 'grades.html')

@app.route('/staff-schedule')
def staff_schedule():
    """排班管理頁面（iframe用）"""
    return send_from_directory('static', 'staff-schedule.html')


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
# 學生管理 API
# ─────────────────────────────────────────────

@app.route('/admin/api/students', methods=['GET'])
def admin_get_students():
    check_admin()
    students = Student.query.order_by(Student.created_at.desc()).all()
    return jsonify([s.to_dict() for s in students])


@app.route('/admin/api/students', methods=['POST'])
def admin_add_student():
    check_admin()
    data = request.get_json()
    
    # 產生學生編號
    student_count = Student.query.count()
    student_id = 'S' + datetime.now().strftime('%Y%m') + str(student_count + 1001)
    
    student = Student(
        student_id=student_id,
        name=data['name'],
        contact=data.get('contact', ''),
        email=data.get('email', ''),
        age=data.get('age'),
        level=data.get('level', ''),
        instrument=data.get('instrument', ''),
        parent_name=data.get('parent_name', ''),
        parent_contact=data.get('parent_contact', ''),
        address=data.get('address', ''),
        note=data.get('note', ''),
        enrollment_date=datetime.now(),
        is_active=True,
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@app.route('/admin/api/students/<int:sid>', methods=['PUT'])
def admin_update_student(sid):
    check_admin()
    student = Student.query.get_or_404(sid)
    data = request.get_json()
    
    student.name = data.get('name', student.name)
    student.contact = data.get('contact', student.contact)
    student.email = data.get('email', student.email)
    student.age = data.get('age', student.age)
    student.level = data.get('level', student.level)
    student.instrument = data.get('instrument', student.instrument)
    student.parent_name = data.get('parent_name', student.parent_name)
    student.parent_contact = data.get('parent_contact', student.parent_contact)
    student.address = data.get('address', student.address)
    student.note = data.get('note', student.note)
    
    db.session.commit()
    return jsonify(student.to_dict())


@app.route('/admin/api/students/<int:sid>', methods=['DELETE'])
def admin_delete_student(sid):
    check_admin()
    student = Student.query.get_or_404(sid)
    student.is_active = False
    db.session.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# 繳費管理 API
# ─────────────────────────────────────────────

@app.route('/admin/api/payments', methods=['GET'])
def admin_get_payments():
    check_admin()
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return jsonify([p.to_dict() for p in payments])


@app.route('/admin/api/payments', methods=['POST'])
def admin_add_payment():
    check_admin()
    data = request.get_json()
    
    payment = Payment(
        student_id=data['student_id'],
        amount=data['amount'],
        payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d') if data.get('payment_date') else datetime.now(),
        payment_method=data.get('payment_method', 'cash'),
        status='paid',
        month=data.get('month', ''),
        note=data.get('note', ''),
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(payment.to_dict()), 201


@app.route('/admin/api/payments/<int:pid>', methods=['DELETE'])
def admin_delete_payment(pid):
    check_admin()
    payment = Payment.query.get_or_404(pid)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# 支出管理 API
# ─────────────────────────────────────────────

@app.route('/admin/api/expenses', methods=['GET'])
def admin_get_expenses():
    check_admin()
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])


@app.route('/admin/api/expenses', methods=['POST'])
def admin_add_expense():
    check_admin()
    data = request.get_json()
    
    expense = Expense(
        category=data['category'],
        amount=data['amount'],
        expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d') if data.get('expense_date') else datetime.now(),
        description=data.get('description', ''),
        note=data.get('note', ''),
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201


@app.route('/admin/api/expenses/<int:eid>', methods=['DELETE'])
def admin_delete_expense(eid):
    check_admin()
    expense = Expense.query.get_or_404(eid)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# 財務報表 API
# ─────────────────────────────────────────────

@app.route('/admin/api/finance/summary', methods=['GET'])
def admin_get_finance_summary():
    check_admin()
    month = request.args.get('month')  # YYYY-MM
    
    # 收入統計
    payments_query = Payment.query.filter_by(status='paid')
    if month:
        payments_query = payments_query.filter(Payment.month == month)
    
    total_income = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'paid'
    ).scalar() or 0
    
    # 支出統計
    expenses_query = Expense.query
    if month:
        start_date = month + '-01'
        end_date = month + '-31'
        expenses_query = expenses_query.filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    
    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    
    # 學生統計
    active_students = Student.query.filter_by(is_active=True).count()
    
    # 本月收入
    current_month = datetime.now().strftime('%Y-%m')
    month_income = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.month == current_month,
        Payment.status == 'paid'
    ).scalar() or 0
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net_income': total_income - total_expense,
        'active_students': active_students,
        'month_income': month_income,
        'current_month': current_month,
    })


# ─────────────────────────────────────────────
# 出席打卡 API
# ─────────────────────────────────────────────

@app.route('/admin/api/attendance', methods=['GET'])
def admin_get_attendance():
    check_admin()
    date = request.args.get('date')
    student_id = request.args.get('student_id', type=int)
    
    query = Attendance.query
    if date:
        query = query.filter_by(date=date)
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    records = query.order_by(Attendance.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route('/admin/api/attendance', methods=['POST'])
def admin_add_attendance():
    check_admin()
    data = request.get_json()
    
    check_time_str = data.get('check_time', '')
    if check_time_str:
        check_datetime = datetime.fromisoformat(check_time_str.replace('Z', '+00:00'))
        date = check_datetime.strftime('%Y-%m-%d')
        time = check_datetime.strftime('%H:%M')
    else:
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M')
    
    attendance = Attendance(
        student_id=data['student_id'],
        date=date,
        check_time=time,
        status=data.get('status', 'present'),
        late_minutes=data.get('late_minutes', 0),
        course=data.get('course', ''),
        note=data.get('note', ''),
    )
    db.session.add(attendance)
    db.session.commit()
    return jsonify(attendance.to_dict()), 201


@app.route('/admin/api/attendance/<int:aid>', methods=['DELETE'])
def admin_delete_attendance(aid):
    check_admin()
    attendance = Attendance.query.get_or_404(aid)
    db.session.delete(attendance)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/attendance/stats', methods=['GET'])
def admin_get_attendance_stats():
    check_admin()
    
    # 統計每個學生的出席情況
    students = Student.query.filter_by(is_active=True).all()
    stats = []
    
    for student in students:
        records = Attendance.query.filter_by(student_id=student.id).all()
        total = len(records)
        present = len([r for r in records if r.status == 'present'])
        late = len([r for r in records if r.status == 'late'])
        absent = len([r for r in records if r.status == 'absent'])
        leave = len([r for r in records if r.status == 'leave'])
        
        rate = round((present + late) / total * 100, 1) if total > 0 else 0
        
        stats.append({
            'student_id': student.id,
            'student_name': student.name,
            'total': total,
            'present': present,
            'late': late,
            'absent': absent,
            'leave': leave,
            'attendance_rate': rate
        })
    
    return jsonify(stats)


# ─────────────────────────────────────────────
# 成績管理 API
# ─────────────────────────────────────────────

@app.route('/admin/api/exams', methods=['GET'])
def admin_get_exams():
    check_admin()
    exams = Exam.query.order_by(Exam.date.desc()).all()
    return jsonify([e.to_dict() for e in exams])


@app.route('/admin/api/exams', methods=['POST'])
def admin_add_exam():
    check_admin()
    data = request.get_json()
    
    exam = Exam(
        name=data['name'],
        date=data['date'],
        max_score=data.get('max_score', 100),
        pass_score=data.get('pass_score', 60),
    )
    db.session.add(exam)
    db.session.commit()
    return jsonify(exam.to_dict()), 201


@app.route('/admin/api/exams/<int:eid>', methods=['DELETE'])
def admin_delete_exam(eid):
    check_admin()
    exam = Exam.query.get_or_404(eid)
    db.session.delete(exam)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/grades', methods=['GET'])
def admin_get_grades():
    check_admin()
    exam_id = request.args.get('exam_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    query = Grade.query
    if exam_id:
        query = query.filter_by(exam_id=exam_id)
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    grades = query.order_by(Grade.created_at.desc()).all()
    return jsonify([g.to_dict() for g in grades])


@app.route('/admin/api/grades', methods=['POST'])
def admin_add_grade():
    check_admin()
    data = request.get_json()
    
    grade = Grade(
        exam_id=data['exam_id'],
        student_id=data['student_id'],
        score=data['score'],
        note=data.get('note', ''),
    )
    db.session.add(grade)
    db.session.commit()
    
    # 計算排名
    _calculate_ranks(data['exam_id'])
    
    return jsonify(grade.to_dict()), 201


@app.route('/admin/api/grades/<int:gid>', methods=['DELETE'])
def admin_delete_grade(gid):
    check_admin()
    grade = Grade.query.get_or_404(gid)
    exam_id = grade.exam_id
    db.session.delete(grade)
    db.session.commit()
    
    # 重新計算排名
    _calculate_ranks(exam_id)
    
    return jsonify({'success': True})


def _calculate_ranks(exam_id):
    """計算某次考試的排名"""
    grades = Grade.query.filter_by(exam_id=exam_id).order_by(Grade.score.desc()).all()
    
    for idx, grade in enumerate(grades, 1):
        grade.rank = idx
        
        # 計算進退步趨勢
        student_grades = Grade.query.filter_by(student_id=grade.student_id).order_by(Grade.created_at).all()
        if len(student_grades) >= 2:
            prev_score = student_grades[-2].score
            curr_score = grade.score
            if curr_score > prev_score + 5:
                grade.trend = 'up'
            elif curr_score < prev_score - 5:
                grade.trend = 'down'
            else:
                grade.trend = 'stable'
    
    db.session.commit()


# ─────────────────────────────────────────────
# 排班管理 API
# ─────────────────────────────────────────────

@app.route('/admin/api/shifts', methods=['GET'])
def admin_get_shifts():
    check_admin()
    shifts = Shift.query.order_by(Shift.date, Shift.start_time).all()
    return jsonify([s.to_dict() for s in shifts])


@app.route('/admin/api/shifts', methods=['POST'])
def admin_add_shift():
    check_admin()
    data = request.get_json()
    
    shift = Shift(
        teacher_id=data['teacher_id'],
        date=data['date'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        course=data.get('course', ''),
    )
    db.session.add(shift)
    db.session.commit()
    return jsonify(shift.to_dict()), 201


@app.route('/admin/api/shifts/<int:sid>', methods=['DELETE'])
def admin_delete_shift(sid):
    check_admin()
    shift = Shift.query.get_or_404(sid)
    db.session.delete(shift)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/substitutes', methods=['GET'])
def admin_get_substitutes():
    check_admin()
    substitutes = Substitute.query.order_by(Substitute.created_at.desc()).all()
    return jsonify([s.to_dict() for s in substitutes])


@app.route('/admin/api/substitutes', methods=['POST'])
def admin_add_substitute():
    check_admin()
    data = request.get_json()
    
    substitute = Substitute(
        original_teacher_id=data['original_teacher_id'],
        substitute_teacher_id=data['substitute_teacher_id'],
        date=data['date'],
        time_slot=data['time_slot'],
        reason=data.get('reason', ''),
        status='pending',
    )
    db.session.add(substitute)
    db.session.commit()
    return jsonify(substitute.to_dict()), 201


@app.route('/admin/api/substitutes/<int:sid>/approve', methods=['POST'])
def admin_approve_substitute(sid):
    check_admin()
    substitute = Substitute.query.get_or_404(sid)
    substitute.status = 'approved'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/substitutes/<int:sid>/reject', methods=['POST'])
def admin_reject_substitute(sid):
    check_admin()
    substitute = Substitute.query.get_or_404(sid)
    substitute.status = 'rejected'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/leaves', methods=['GET'])
def admin_get_leaves():
    check_admin()
    leaves = Leave.query.order_by(Leave.created_at.desc()).all()
    return jsonify([l.to_dict() for l in leaves])


@app.route('/admin/api/leaves', methods=['POST'])
def admin_add_leave():
    check_admin()
    data = request.get_json()
    
    leave = Leave(
        teacher_id=data['teacher_id'],
        leave_type=data['leave_type'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        days=data['days'],
        reason=data.get('reason', ''),
        status='pending',
    )
    db.session.add(leave)
    db.session.commit()
    return jsonify(leave.to_dict()), 201


@app.route('/admin/api/leaves/<int:lid>/approve', methods=['POST'])
def admin_approve_leave(lid):
    check_admin()
    leave = Leave.query.get_or_404(lid)
    leave.status = 'approved'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/leaves/<int:lid>/reject', methods=['POST'])
def admin_reject_leave(lid):
    check_admin()
    leave = Leave.query.get_or_404(lid)
    leave.status = 'rejected'
    db.session.commit()
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# LINE 串接 API
# ─────────────────────────────────────────────

@app.route('/admin/api/line/config', methods=['GET'])
def get_line_config():
    """取得 LINE 設定狀態（不返回實際 token）"""
    check_admin()
    access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET', '')
    
    return jsonify({
        'configured': bool(access_token and channel_secret),
        'has_access_token': bool(access_token),
        'has_channel_secret': bool(channel_secret)
    })


@app.route('/admin/api/line/test', methods=['POST'])
def test_line_connection():
    """測試 LINE API 連線"""
    check_admin()
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'error': '缺少 Access Token'}), 400
    
    try:
        import requests
        response = requests.get(
            'https://api.line.me/v2/bot/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            return jsonify({
                'success': True,
                'bot_name': bot_info.get('displayName'),
                'bot_id': bot_info.get('userId'),
                'message': '連線成功！'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Access Token 無效',
                'details': response.text
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'連線失敗: {str(e)}'
        }), 500


@app.route('/admin/api/line/broadcast', methods=['POST'])
def line_broadcast():
    """發送 LINE 群發訊息"""
    check_admin()
    data = request.get_json()
    
    access_token = data.get('access_token') or os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    if not access_token:
        return jsonify({'error': '尚未設定 LINE Channel Access Token'}), 400
    
    message = data.get('message')
    recipients = data.get('recipients', 'all')
    
    if not message:
        return jsonify({'error': '訊息內容不可為空'}), 400
    
    try:
        import requests
        
        # 群發訊息 API
        url = 'https://api.line.me/v2/bot/message/broadcast'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'messages': [
                {
                    'type': 'text',
                    'text': message
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': '訊息已發送',
                'recipients': recipients
            })
        else:
            return jsonify({
                'success': False,
                'error': 'LINE API 呼叫失敗',
                'details': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發送失敗: {str(e)}'
        }), 500


@app.route('/admin/api/line/push', methods=['POST'])
def line_push():
    """發送 LINE 推送訊息給特定用戶"""
    check_admin()
    data = request.get_json()
    
    access_token = data.get('access_token') or os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    if not access_token:
        return jsonify({'error': '尚未設定 LINE Channel Access Token'}), 400
    
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'error': '缺少必要參數'}), 400
    
    try:
        import requests
        
        url = 'https://api.line.me/v2/bot/message/push'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': message
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': '訊息已發送'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'LINE API 呼叫失敗',
                'details': response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'發送失敗: {str(e)}'
        }), 500


@app.route('/webhook/line', methods=['POST'])
def line_webhook():
    """LINE Webhook 接收訊息與事件"""
    
    # 取得 Channel Secret
    channel_secret = os.environ.get('LINE_CHANNEL_SECRET', '')
    
    # 取得簽名驗證
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    # 驗證簽名
    if channel_secret:
        try:
            import hashlib
            import hmac
            import base64
            
            hash_value = hmac.new(
                channel_secret.encode('utf-8'),
                body.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            expected_signature = base64.b64encode(hash_value).decode()
            
            if signature != expected_signature:
                return jsonify({'error': 'Invalid signature'}), 403
        except Exception as e:
            print(f'Signature verification error: {e}')
            return jsonify({'error': 'Signature verification failed'}), 403
    
    # 處理事件
    try:
        events = request.json.get('events', [])
        access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
        
        for event in events:
            event_type = event.get('type')
            
            if event_type == 'message':
                # 處理訊息事件
                reply_token = event.get('replyToken')
                message = event.get('message', {})
                message_type = message.get('type')
                user_id = event.get('source', {}).get('userId')
                
                if message_type == 'text':
                    message_text = message.get('text', '').lower()
                    
                    # 簡單的關鍵字回覆
                    reply_text = '您好！感謝您的訊息。'
                    
                    if '課程' in message_text or '上課' in message_text:
                        reply_text = '我們提供鋼琴、吉他、小提琴等多種音樂課程。詳細資訊請來電洽詢：02-1234-5678'
                    elif '收費' in message_text or '價格' in message_text:
                        reply_text = '課程收費：\n鋼琴 NT$1,200/堂\n吉他 NT$1,000/堂\n小提琴 NT$1,500/堂\n歡迎預約體驗！'
                    elif '地址' in message_text or '位置' in message_text:
                        reply_text = '地址：台北市中正區音樂街123號\n營業時間：週一至週日 09:00-21:00'
                    elif '預約' in message_text or '報名' in message_text:
                        reply_text = '預約方式：\n1. 線上預約：https://music-web.com\n2. 來電預約：02-1234-5678\n3. LINE 私訊預約'
                    
                    # 回覆訊息
                    if access_token and reply_token:
                        _line_reply(access_token, reply_token, reply_text)
                        
            elif event_type == 'follow':
                # 用戶加入好友
                user_id = event.get('source', {}).get('userId')
                reply_token = event.get('replyToken')
                
                welcome_message = '歡迎加入音樂補習班！\n\n您可以透過 LINE 查詢：\n• 課程資訊\n• 收費標準\n• 預約課程\n• 地址與營業時間\n\n請直接傳送訊息給我們！'
                
                if access_token and reply_token:
                    _line_reply(access_token, reply_token, welcome_message)
                
                # 可以將 user_id 儲存到資料庫
                print(f'New follower: {user_id}')
                
            elif event_type == 'unfollow':
                # 用戶封鎖
                user_id = event.get('source', {}).get('userId')
                print(f'User unfollowed: {user_id}')
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f'Webhook error: {e}')
        return jsonify({'error': str(e)}), 500


def _line_reply(access_token, reply_token, text):
    """回覆 LINE 訊息的輔助函式"""
    try:
        import requests
        
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'replyToken': reply_token,
            'messages': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
        
        requests.post(url, headers=headers, json=payload, timeout=10)
    except Exception as e:
        print(f'LINE reply error: {e}')


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
# 應用程式初始化（適用於 Render/Production）
# ─────────────────────────────────────────────

# 確保資料表存在（對於 Render 等使用 gunicorn 的環境很重要）
with app.app_context():
    try:
        db.create_all()
        print('✓ 資料庫初始化完成')
        # 建立範例資料（如果需要）
        if Teacher.query.count() == 0:
            seed()
            print('✓ 範例資料建立完成')
    except Exception as e:
        print(f'⚠ 資料庫初始化錯誤: {e}')


# ─────────────────────────────────────────────
# 啟動
# ─────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    with app.app_context():
        # 建立所有資料表（包括新增的）
        # 這個指令只會建立不存在的資料表，不會影響已存在的資料表
        db.create_all()
        print('✓ 資料庫已初始化（所有資料表已建立）')
        seed()
    print('\n  學生預約頁面：http://localhost:5000')
    print('  管理後台登入：http://localhost:5000/admin')
    print('  模組管理首頁：http://localhost:5000/dashboard')
    print(f'  管理密碼：    {ADMIN_PASSWORD}\n')
    app.run(debug=True, port=5000)