# 🎯 Online Quiz Platform

A modern, full-stack **Online Quiz Platform** built with **Python Flask** and **SQLite**. The application provides a secure role-based authentication system, interactive quizzes with a countdown timer, automatic submission, and an admin panel for managing quiz content.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 📖 Project Overview

Online Quiz Platform is a responsive web application designed for students and administrators.

Students can register, log in, attempt quizzes, track scores, and view previous results.

Administrators can manage users and maintain the quiz database by adding, editing, and deleting questions.

The project is developed using Flask, SQLAlchemy, SQLite, HTML5, CSS3, JavaScript, Bootstrap 5, and Jinja2.

---

# ✨ Key Features

## 👤 User Authentication

- Secure Registration & Login
- Password Hashing
- Role-Based Authentication
- Student Dashboard
- Admin Dashboard
- Session Management

## 📝 Dynamic Quiz Interface

- Single-page quiz experience
- Next / Previous navigation
- Dynamic countdown timer
- Progress bar
- Auto submission when time expires
- Manual submission
- Instant score calculation

## 📚 Question Management

- Add Questions
- Edit Questions
- Delete Questions
- Subject-wise questions
- Category-wise questions
- Difficulty-wise questions

## 📊 Result System

- Quiz Score
- Percentage
- Correct Answers
- Wrong Answers
- Quiz History

## 🌱 Database Seeding

Sample educational questions are available for:

- Python
- DBMS
- Data Structures
- Computer Networks
- HTML & CSS
- General Knowledge

Questions are organized by subject, category, and difficulty.

---

# 🛠 Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Python |
| Framework | Flask |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Template Engine | Jinja2 |
| Database | SQLite |
| Frontend | HTML5 |
| Styling | CSS3 |
| UI | Bootstrap 5 |
| Icons | Bootstrap Icons |
| JavaScript | Vanilla ES6 |

---

# 📂 Folder Structure

```text
Online-Quiz-Platform/
│
├── app.py
├── requirements.txt
├── instance/
│   └── quiz.db
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── quiz.html
│   ├── result.html
│   ├── history.html
│   ├── add_question.html
│   ├── questions.html
│   └── profile.html
│
└── README.md
```

---

# 🚀 Quick Start Guide

## 1. Clone the Repository

```bash
git clone <REPOSITORY_URL>
```

---

## 2. Move into the Project Folder

```bash
cd Online-Quiz-Platform
```

---

## 3. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install flask flask-sqlalchemy flask-login werkzeug
```

or

```bash
pip install -r requirements.txt
```

---

## 5. Run the Project

```bash
python app.py
```

---

## 6. Open Your Browser

```
http://127.0.0.1:5000
```

---

# 🌱 Database Seeding

The application includes a database seeding feature for generating sample educational questions.

Subjects include:

- Python
- DBMS
- Data Structures
- Computer Networks
- HTML
- CSS
- General Knowledge

---

# 🔐 Default Admin Credentials

| Email | Password |
|--------|----------|
| admin@quiz.com | admin123 |

> **Note:** Change the default password after deployment for better security.

---

# 📌 Future Improvements

- Leaderboard
- PDF Result Export
- CSV Import & Export
- Question Analytics
- AI Question Generation
- Dark Mode
- Multi-language Support
- Email Verification
- Password Reset

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Rakesh Yadav**

- 🎓 BCA Student
- 💻 Python & Flask Developer
- 🌐 Web Developer

GitHub: **https://github.com/rakeshyadav78950555-bot**

---

## ⭐ If you like this project, please give it a Star!
