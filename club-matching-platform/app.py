"""
社团招新智能匹配平台 - 主应用
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Student, Club, Application
from database import create_app
from matching import get_recommendations, generate_student_tags
import json
import os

app = create_app()

# ========== 首页 ==========
@app.route('/')
def index():
    """首页"""
    clubs = Club.query.filter_by(is_recruiting=True).limit(6).all()
    return render_template('index.html', clubs=clubs)


# ========== 兴趣测评 ==========
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    """兴趣测评页面"""
    if request.method == 'POST':
        # 收集测评结果
        scores = {
            "arts": int(request.form.get('arts_score', 50)),
            "sports": int(request.form.get('sports_score', 50)),
            "academic": int(request.form.get('academic_score', 50)),
            "charity": int(request.form.get('charity_score', 50)),
            "tech": int(request.form.get('tech_score', 50))
        }

        # 收集时间可用性
        time_available = {}
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for day in days:
            times = request.form.getlist(f'time_{day}')
            if times:
                time_available[day] = times

        # 生成标签
        tags = generate_student_tags(scores)

        # 保存到 session
        session['survey_scores'] = scores
        session['survey_time'] = time_available
        session['survey_tags'] = tags

        return redirect(url_for('register'))

    return render_template('survey.html')


# ========== 用户注册 ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    """学生注册页面"""
    if request.method == 'POST':
        student = Student(
            student_id=request.form['student_id'],
            name=request.form['name'],
            major=request.form['major'],
            grade=request.form['grade'],
            interest_scores=json.dumps(session.get('survey_scores', {})),
            time_available=json.dumps(session.get('survey_time', {})),
            tags=','.join(session.get('survey_tags', []))
        )

        db.session.add(student)
        db.session.commit()

        session['student_id'] = student.id
        return redirect(url_for('recommend'))

    return render_template('register.html')


# ========== 智能推荐 ==========
@app.route('/recommend')
def recommend():
    """推荐结果页面"""
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('survey'))

    student = Student.query.get(student_id)
    clubs = Club.query.filter_by(is_recruiting=True).all()

    recommendations = get_recommendations(student, clubs, top_n=10)

    return render_template('recommend.html', student=student, recommendations=recommendations)


# ========== 社团列表 ==========
@app.route('/clubs')
def club_list():
    """社团列表页面"""
    category = request.args.get('category', '')
    if category:
        clubs = Club.query.filter_by(category=category, is_recruiting=True).all()
    else:
        clubs = Club.query.filter_by(is_recruiting=True).all()

    return render_template('club_list.html', clubs=clubs, current_category=category)


# ========== 社团详情 ==========
@app.route('/club/<int:club_id>')
def club_detail(club_id):
    """社团详情页面"""
    club = Club.query.get_or_404(club_id)
    student_id = session.get('student_id')

    # 检查是否已报名
    applied = False
    if student_id:
        applied = Application.query.filter_by(student_id=student_id, club_id=club_id).first() is not None

    return render_template('club_detail.html', club=club, applied=applied)


# ========== 报名 ==========
@app.route('/apply/<int:club_id>', methods=['GET', 'POST'])
def apply(club_id):
    """报名页面"""
    student_id = session.get('student_id')
    if not student_id:
        flash('请先完成兴趣测评', 'error')
        return redirect(url_for('survey'))

    club = Club.query.get_or_404(club_id)
    student = Student.query.get(student_id)

    # 检查是否已报名
    existing = Application.query.filter_by(student_id=student_id, club_id=club_id).first()
    if existing:
        flash('您已报名该社团', 'warning')
        return redirect(url_for('club_detail', club_id=club_id))

    if request.method == 'POST':
        application = Application(
            student_id=student_id,
            club_id=club_id,
            self_intro=request.form.get('self_intro', ''),
            status='pending'
        )

        db.session.add(application)
        db.session.commit()

        flash('报名成功！请等待社团审核', 'success')
        return redirect(url_for('my_applications'))

    return render_template('apply.html', club=club, student=student)


# ========== 我的报名 ==========
@app.route('/my-applications')
def my_applications():
    """我的报名列表"""
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('survey'))

    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template('my_applications.html', applications=applications)


# ========== 社团管理端 - 登录 ==========
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """社团管理登录"""
    if request.method == 'POST':
        club_id = request.form['club_id']
        password = request.form['password']

        club = Club.query.get(club_id)
        if club and club.admin_password == password:
            session['admin_club_id'] = club.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('社团ID或密码错误', 'error')

    return render_template('admin/login.html')


# ========== 社团管理端 - 仪表盘 ==========
@app.route('/admin/dashboard')
def admin_dashboard():
    """社团管理仪表盘"""
    club_id = session.get('admin_club_id')
    if not club_id:
        return redirect(url_for('admin_login'))

    club = Club.query.get(club_id)
    applications = Application.query.filter_by(club_id=club_id).all()

    stats = {
        'total': len(applications),
        'pending': len([a for a in applications if a.status == 'pending']),
        'accepted': len([a for a in applications if a.status == 'accepted']),
        'rejected': len([a for a in applications if a.status == 'rejected'])
    }

    return render_template('admin/dashboard.html', club=club, stats=stats, applications=applications)


# ========== 社团管理端 - 报名管理 ==========
@app.route('/admin/applicants')
def admin_applicants():
    """报名者管理"""
    club_id = session.get('admin_club_id')
    if not club_id:
        return redirect(url_for('admin_login'))

    status_filter = request.args.get('status', '')
    query = Application.query.filter_by(club_id=club_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    applications = query.all()
    return render_template('admin/applicants.html', applications=applications, status_filter=status_filter)


# ========== 更新报名状态 ==========
@app.route('/admin/application/<int:app_id>/update', methods=['POST'])
def update_application_status(app_id):
    """更新报名状态"""
    club_id = session.get('admin_club_id')
    if not club_id:
        return jsonify({'error': '未登录'}), 401

    application = Application.query.get_or_404(app_id)
    if application.club_id != club_id:
        return jsonify({'error': '无权限'}), 403

    new_status = request.form.get('status')
    if new_status in ['pending', 'accepted', 'rejected', 'interview']:
        application.status = new_status
        db.session.commit()
        flash('状态更新成功', 'success')

    return redirect(url_for('admin_applicants'))


# ========== 社团管理端 - 退出 ==========
@app.route('/admin/logout')
def admin_logout():
    """社团管理退出"""
    session.pop('admin_club_id', None)
    return redirect(url_for('admin_login'))


# ========== API: 获取匹配分数 ==========
@app.route('/api/match/<int:club_id>')
def api_match_score(club_id):
    """API: 获取匹配分数"""
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'error': '请先完成测评'}), 400

    student = Student.query.get(student_id)
    club = Club.query.get_or_404(club_id)

    from matching import calculate_match_score
    score, reasons = calculate_match_score(student, club)

    return jsonify({
        'score': score,
        'reasons': reasons
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
