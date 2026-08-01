import os
import random
import csv
import io
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for, flash, request,
    session, jsonify, send_file
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from fpdf import FPDF

# App Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'quiz_platform_secret_key_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    profile_image = db.Column(db.String(200), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship('Result', backref='user_ref', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), default='General')
    difficulty = db.Column(db.String(50), default='Medium')
    marks = db.Column(db.Integer, default=1)
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to sanitize strings for JS safety
def clean_str(val):
    if not val:
        return ""
    return str(val).replace('\r', '').replace('\n', ' ').strip()

# -------------------------------------------------------------------
# Auth & Base Routes
# -------------------------------------------------------------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw, role='user')
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# -------------------------------------------------------------------
# User Dashboard & Profile
# -------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    total_quizzes = Result.query.filter_by(user_id=current_user.id).count()
    total_questions = Question.query.count()
    subjects = db.session.query(Question.subject).distinct().all()
    categories = db.session.query(Question.category).distinct().all()
    
    return render_template(
        'dashboard.html',
        total_quizzes=total_quizzes,
        total_questions=total_questions,
        subjects=[s[0] for s in subjects if s[0]],
        categories=[c[0] for c in categories if c[0]]
    )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        new_pw = request.form.get('password')
        
        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Username taken.', 'danger')
                return redirect(url_for('profile'))
            current_user.username = username
        
        if new_pw:
            current_user.password = generate_password_hash(new_pw, method='pbkdf2:sha256')
            
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_image = filename
                
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('profile.html')

# -------------------------------------------------------------------
# Quiz Engine
# -------------------------------------------------------------------

@app.route('/quiz/setup', methods=['POST'])
@login_required
def quiz_setup():
    subject = request.form.get('subject')
    category = request.form.get('category')
    difficulty = request.form.get('difficulty')
    num_q = int(request.form.get('num_questions', 5))
    timer = int(request.form.get('timer', 60))

    query = Question.query
    if subject and subject != 'All':
        query = query.filter_by(subject=subject)
    if category and category != 'All':
        query = query.filter_by(category=category)
    if difficulty and difficulty != 'All':
        query = query.filter_by(difficulty=difficulty)
        
    available_q = query.all()
    if not available_q:
        flash('No questions match your selected criteria.', 'warning')
        return redirect(url_for('dashboard'))
        
    selected_questions = random.sample(available_q, min(len(available_q), num_q))
    
    # Clean string attributes to ensure safe JSON serializing
    cleaned_questions = []
    for q in selected_questions:
        opts = [clean_str(q.option1), clean_str(q.option2), clean_str(q.option3), clean_str(q.option4)]
        random.shuffle(opts)
        cleaned_questions.append({
            'id': q.id,
            'question': clean_str(q.question),
            'options': opts,
            'answer': clean_str(q.answer),
            'explanation': clean_str(q.explanation)
        })

    session['quiz'] = {
        'subject': subject or 'All Subjects',
        'category': category or 'General',
        'timer': timer,
        'questions': cleaned_questions
    }
    return redirect(url_for('quiz_play'))

@app.route('/quiz/play')
@login_required
def quiz_play():
    quiz = session.get('quiz')
    if not quiz or not quiz.get('questions'):
        flash('No active quiz session found. Please setup a quiz.', 'warning')
        return redirect(url_for('dashboard'))
    return render_template('quiz.html', quiz=quiz)

@app.route('/quiz/submit', methods=['POST'])
@login_required
def quiz_submit():
    data = request.get_json() or {}
    answers = data.get('answers', {})
    quiz = session.get('quiz')
    
    if not quiz:
        return jsonify({'error': 'Session expired'}), 400

    score = 0
    total = len(quiz['questions'])
    
    for q in quiz['questions']:
        q_id_str = str(q['id'])
        if q_id_str in answers and answers[q_id_str] == q['answer']:
            score += 1
            
    percentage = round((score / total) * 100, 2) if total > 0 else 0
    
    res = Result(
        user_id=current_user.id,
        username=current_user.username,
        subject=quiz.get('subject', 'General'),
        category=quiz.get('category', 'General'),
        score=score,
        total=total,
        percentage=percentage
    )
    db.session.add(res)
    db.session.commit()
    
    session.pop('quiz', None)
    return jsonify({'redirect': url_for('result', result_id=res.id)})

@app.route('/result/<int:result_id>')
@login_required
def result(result_id):
    res = Result.query.get_or_404(result_id)
    if res.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('result.html', result=res)

@app.route('/result/<int:result_id>/pdf')
@login_required
def download_pdf(result_id):
    res = Result.query.get_or_404(result_id)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(0, 10, "Quiz Performance Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, f"Candidate: {res.username}", ln=True)
    pdf.cell(0, 8, f"Subject: {res.subject} | Category: {res.category}", ln=True)
    pdf.cell(0, 8, f"Score: {res.score} / {res.total}", ln=True)
    pdf.cell(0, 8, f"Percentage: {res.percentage}%", ln=True)
    pdf.cell(0, 8, f"Date: {res.date.strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    
    output = io.BytesIO()
    pdf_bytes = pdf.output()
    output.write(pdf_bytes)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Quiz_Result_{res.id}.pdf"
    )

@app.route('/history')
@login_required
def history():
    results = Result.query.filter_by(user_id=current_user.id).order_by(Result.date.desc()).all()
    return render_template('history.html', results=results)

@app.route('/leaderboard')
@login_required
def leaderboard():
    top_scores = Result.query.order_by(Result.percentage.desc()).limit(10).all()
    return render_template('leaderboard.html', top_scores=top_scores)

# -------------------------------------------------------------------
# Admin Panel
# -------------------------------------------------------------------

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'users': User.query.count(),
        'questions': Question.query.count(),
        'subjects': db.session.query(Question.subject).distinct().count(),
        'categories': db.session.query(Question.category).distinct().count(),
        'results': Result.query.count()
    }
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/questions')
@login_required
@admin_required
def questions():
    q = request.args.get('q', '').strip()
    subject = request.args.get('subject', '')
    
    query = Question.query
    if q:
        query = query.filter(Question.question.contains(q))
    if subject:
        query = query.filter_by(subject=subject)
        
    question_list = query.order_by(Question.id.desc()).all()
    subjects = db.session.query(Question.subject).distinct().all()
    
    return render_template('questions.html', questions=question_list, subjects=[s[0] for s in subjects if s[0]])

@app.route('/admin/question/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question():
    if request.method == 'POST':
        q = Question(
            question=clean_str(request.form.get('question')),
            option1=clean_str(request.form.get('option1')),
            option2=clean_str(request.form.get('option2')),
            option3=clean_str(request.form.get('option3')),
            option4=clean_str(request.form.get('option4')),
            answer=clean_str(request.form.get('answer')),
            subject=clean_str(request.form.get('subject')),
            category=clean_str(request.form.get('category', 'General')),
            difficulty=clean_str(request.form.get('difficulty', 'Medium')),
            marks=int(request.form.get('marks', 1)),
            explanation=clean_str(request.form.get('explanation'))
        )
        db.session.add(q)
        db.session.commit()
        flash('Question added successfully.', 'success')
        return redirect(url_for('questions'))
    return render_template('add_question.html')

@app.route('/admin/question/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(id):
    q = Question.query.get_or_404(id)
    if request.method == 'POST':
        q.question = clean_str(request.form.get('question'))
        q.option1 = clean_str(request.form.get('option1'))
        q.option2 = clean_str(request.form.get('option2'))
        q.option3 = clean_str(request.form.get('option3'))
        q.option4 = clean_str(request.form.get('option4'))
        q.answer = clean_str(request.form.get('answer'))
        q.subject = clean_str(request.form.get('subject'))
        q.category = clean_str(request.form.get('category'))
        q.difficulty = clean_str(request.form.get('difficulty'))
        q.marks = int(request.form.get('marks', 1))
        q.explanation = clean_str(request.form.get('explanation'))
        
        db.session.commit()
        flash('Question updated successfully.', 'success')
        return redirect(url_for('questions'))
    return render_template('edit_question.html', q=q)

@app.route('/admin/question/delete/<int:id>')
@login_required
@admin_required
def delete_question(id):
    q = Question.query.get_or_404(id)
    db.session.delete(q)
    db.session.commit()
    flash('Question deleted.', 'info')
    return redirect(url_for('questions'))

@app.route('/admin/export/<format_type>')
@login_required
@admin_required
def export_questions(format_type):
    qs = Question.query.all()
    data = [{
        'Question': q.question, 'Option1': q.option1, 'Option2': q.option2,
        'Option3': q.option3, 'Option4': q.option4, 'Answer': q.answer,
        'Subject': q.subject, 'Category': q.category, 'Difficulty': q.difficulty
    } for q in qs]

    df = pd.DataFrame(data)
    output = io.BytesIO()

    if format_type == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', download_name='questions.csv', as_attachment=True)
    elif format_type == 'excel':
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='questions.xlsx', as_attachment=True)
        
    flash('Unsupported export format.', 'danger')
    return redirect(url_for('questions'))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Seed Database
def seed_database():
    # Force drop all old tables and re-create them to wipe out old dummy questions
    db.drop_all()
    db.create_all()

    # Re-create Admin Account
    admin_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
    admin = User(username='admin', email='admin@quiz.com', password=admin_pw, role='admin')
    db.session.add(admin)

    # Real Educational Questions
    real_questions = [
        # --- PYTHON ---
        {
            "subject": "Python", "category": "Data Types", "difficulty": "Easy",
            "question": "Which of the following data types in Python is immutable?",
            "option1": "Tuple", "option2": "List", "option3": "Dictionary", "option4": "Set",
            "answer": "Tuple",
            "explanation": "Tuples are immutable sequences in Python, meaning their values cannot be changed after creation."
        },
        {
            "subject": "Python", "category": "Basics", "difficulty": "Easy",
            "question": "What is the correct output of bool([]) in Python?",
            "option1": "False", "option2": "True", "option3": "TypeError", "option4": "None",
            "answer": "False",
            "explanation": "In Python, empty containers (lists, tuples, dicts, sets, strings) evaluate to False in a boolean context."
        },
        {
            "subject": "Python", "category": "Functions", "difficulty": "Medium",
            "question": "What keyword is used to create an anonymous/inline function in Python?",
            "option1": "lambda", "option2": "def", "option3": "inline", "option4": "anonymous",
            "answer": "lambda",
            "explanation": "The lambda keyword allows you to define small, anonymous single-expression functions."
        },

        # --- DATA STRUCTURES ---
        {
            "subject": "Data Structures", "category": "Stacks & Queues", "difficulty": "Easy",
            "question": "Which principle does a Stack data structure follow?",
            "option1": "LIFO (Last In, First Out)", "option2": "FIFO (First In, First Out)", "option3": "LILO (Last In, Last Out)", "option4": "Random Access",
            "answer": "LIFO (Last In, First Out)",
            "explanation": "A stack follows Last-In, First-Out (LIFO), where the element inserted last is removed first."
        },

        # --- DBMS ---
        {
            "subject": "DBMS", "category": "SQL", "difficulty": "Easy",
            "question": "Which SQL statement is used to remove all records from a table without logging individual row deletions?",
            "option1": "TRUNCATE", "option2": "DELETE", "option3": "DROP", "option4": "REMOVE",
            "answer": "TRUNCATE",
            "explanation": "TRUNCATE removes all rows from a table quickly without logging individual row deletions, unlike DELETE."
        },

        # --- COMPUTER NETWORKS ---
        {
            "subject": "Computer Networks", "category": "Protocols", "difficulty": "Easy",
            "question": "Which layer of the OSI model is responsible for routing packets across networks?",
            "option1": "Network Layer", "option2": "Data Link Layer", "option3": "Transport Layer", "option4": "Physical Layer",
            "answer": "Network Layer",
            "explanation": "The Network Layer (Layer 3) handles packet routing, logical addressing (IP addresses), and traffic control."
        },
        {
            "subject": "Computer Networks", "category": "Protocols", "difficulty": "Medium",
            "question": "What port does standard HTTP use by default?",
            "option1": "Port 80", "option2": "Port 443", "option3": "Port 21", "option4": "Port 25",
            "answer": "Port 80",
            "explanation": "HTTP defaults to port 80, whereas secure HTTPS uses port 443."
        }
    ]

    for data in real_questions:
        q = Question(
            question=data["question"],
            option1=data["option1"],
            option2=data["option2"],
            option3=data["option3"],
            option4=data["option4"],
            answer=data["answer"],
            subject=data["subject"],
            category=data["category"],
            difficulty=data["difficulty"],
            explanation=data["explanation"]
        )
        db.session.add(q)

    db.session.commit()
    print("Database forcefully reset and populated with REAL questions!")

if __name__ == '__main__':
    with app.app_context():
        seed_database()
    app.run(debug=True)