"""
数据模型定义
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Student(db.Model):
    """学生模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # 学号
    name = db.Column(db.String(50), nullable=False)  # 姓名
    major = db.Column(db.String(50))  # 专业
    grade = db.Column(db.String(20))  # 年级

    # 兴趣测评结果（JSON格式存储各维度分数）
    interest_scores = db.Column(db.Text)  # {"arts": 80, "sports": 60, "academic": 70, "charity": 50, "tech": 90}

    # 生成的兴趣标签
    tags = db.Column(db.Text)  # "文艺,技术,创业"

    # 时间可用性（周一到周日，早中晚）
    time_available = db.Column(db.Text)  # {"mon": ["evening"], "tue": ["afternoon", "evening"], ...}

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Student {self.name}>'


class Club(db.Model):
    """社团模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 社团名称
    category = db.Column(db.String(50))  # 类别：文艺、体育、学术、公益、技术等
    description = db.Column(db.Text)  # 社团简介
    requirements = db.Column(db.Text)  # 招新要求
    tags = db.Column(db.Text)  # 社团标签 "文艺,音乐,表演"

    # 活动时间偏好
    activity_time = db.Column(db.Text)  # {"mon": ["evening"], "wed": ["afternoon"], ...}

    # 联系方式
    contact = db.Column(db.String(100))
    wechat_group = db.Column(db.String(100))

    # 招新状态
    is_recruiting = db.Column(db.Boolean, default=True)

    # 管理员密码（简化版）
    admin_password = db.Column(db.String(100), default="123456")

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Club {self.name}>'


class Application(db.Model):
    """报名记录模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    # 状态：pending(待审核), accepted(已录取), rejected(已拒绝), interview(面试中)
    status = db.Column(db.String(20), default='pending')

    # 自我介绍
    self_intro = db.Column(db.Text)

    # 面试时间
    interview_time = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    student = db.relationship('Student', backref='applications')
    club = db.relationship('Club', backref='applications')

    def __repr__(self):
        return f'<Application {self.student.name} -> {self.club.name}>'
