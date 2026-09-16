# db.py — All database functions used by the app.
import sqlite3

DB_FILE = "quiz_system.db"

# Opens and returns a new database connection.
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Runs a SELECT and returns all matching rows as a list.
def fetch_all(query, params=()):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(query.replace('%s', '?'), params)
    rows   = cursor.fetchall()
    conn.close()
    return rows

# Runs a SELECT and returns only the first row (or None if nothing found).
def fetch_one(query, params=()):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(query.replace('%s', '?'), params)
    row    = cursor.fetchone()
    conn.close()
    return row

# Runs INSERT / UPDATE / DELETE. Returns the ID of the new row.
def run_query(query, params=()):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(query.replace('%s', '?'), params)
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'student'
        );
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            time_limit INTEGER NOT NULL DEFAULT 10
        );
        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            marks INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS options (
            option_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            option_text VARCHAR(255) NOT NULL,
            is_correct INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES questions (question_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id) ON DELETE CASCADE
        );
        INSERT OR IGNORE INTO users (user_id, username, password, role) VALUES (1, 'admin', 'Admin123', 'admin');
    """)
    conn.commit()
    conn.close()

init_db()

# ── Auth helpers ──────────────────────────────────────────
# Returns the user row if username+password match, else None.
def get_user(username, password):
    return fetch_one(
        "SELECT user_id, username, password, role FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

# Registers a new student account. Returns the new user_id.
def register_user(username, password):
    return run_query(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')",
        (username, password)
    )

# Returns True if the username is already taken.
def username_exists(username):
    return fetch_one("SELECT user_id FROM users WHERE username=%s", (username,)) is not None

# ── Quiz helpers ──────────────────────────────────────────

# Returns all quizzes as (quiz_id, title, time_limit).
def get_all_quizzes():
    return fetch_all("SELECT quiz_id, title, time_limit FROM quizzes")

# Adds a new quiz. Returns the new quiz_id.
def add_quiz(title, time_limit):
    return run_query("INSERT INTO quizzes (title, time_limit) VALUES (%s, %s)", (title, time_limit))

# Deletes a quiz and all its questions, options, and attempts (CASCADE).
def delete_quiz(quiz_id):
    run_query("DELETE FROM quizzes WHERE quiz_id=%s", (quiz_id,))

# ── Question helpers ──────────────────────────────────────

# Returns all questions for a quiz as (question_id, quiz_id, text, marks).
def get_questions(quiz_id):
    return fetch_all(
        "SELECT question_id, quiz_id, question_text, marks FROM questions WHERE quiz_id=%s",
        (quiz_id,)
    )

# Adds a question to a quiz. Returns the new question_id.
def add_question(quiz_id, question_text, marks):
    return run_query(
        "INSERT INTO questions (quiz_id, question_text, marks) VALUES (%s, %s, %s)",
        (quiz_id, question_text, marks)
    )

# Updates an existing question's text and marks.
def update_question(question_id, new_text, new_marks):
    run_query(
        "UPDATE questions SET question_text=%s, marks=%s WHERE question_id=%s",
        (new_text, new_marks, question_id)
    )

# ── Option helpers ────────────────────────────────────────

# Returns all 4 options for a question as (option_id, q_id, text, is_correct).
def get_options(question_id):
    return fetch_all(
        "SELECT option_id, question_id, option_text, is_correct FROM options WHERE question_id=%s",
        (question_id,)
    )

# Adds one answer option. is_correct = 1 for correct, 0 for wrong.
def add_option(question_id, option_text, is_correct):
    run_query(
        "INSERT INTO options (question_id, option_text, is_correct) VALUES (%s, %s, %s)",
        (question_id, option_text, is_correct)
    )

# Sets all options for a question to is_correct=0 (call before updating).
def clear_correct_options(question_id):
    run_query("UPDATE options SET is_correct=0 WHERE question_id=%s", (question_id,))

# Updates one option's text and whether it is the correct answer.
def update_option(option_id, option_text, is_correct):
    run_query(
        "UPDATE options SET option_text=%s, is_correct=%s WHERE option_id=%s",
        (option_text, is_correct, option_id)
    )

# ── Attempt helpers ───────────────────────────────────────

# Saves a completed quiz attempt with the student's score.
def save_attempt(user_id, quiz_id, score):
    run_query(
        "INSERT INTO attempts (user_id, quiz_id, score, status) VALUES (%s, %s, %s, 'completed')",
        (user_id, quiz_id, score)
    )

# Returns all past attempts for one student, newest first.
def get_student_attempts(user_id):
    return fetch_all(
        """SELECT a.attempt_id, q.title, a.score, a.status
           FROM   attempts a
           JOIN   quizzes  q ON a.quiz_id = q.quiz_id
           WHERE  a.user_id = %s
           ORDER  BY a.attempt_id DESC""",
        (user_id,)
    )

# Returns every student's attempt — used by the admin gradebook.
def get_all_attempts():
    return fetch_all(
        """SELECT a.attempt_id, u.username, q.title, a.score, a.status
           FROM   attempts a
           JOIN   users   u ON a.user_id  = u.user_id
           JOIN   quizzes q ON a.quiz_id  = q.quiz_id
           ORDER  BY a.attempt_id DESC"""
    )

# Returns all student accounts (excludes admins).
def get_all_students():
    return fetch_all(
        "SELECT user_id, username FROM users WHERE role='student' ORDER BY username"
    )

# Returns each quiz and the student's best score (or None if not attempted).
# Used for the per-student progress view in the admin panel.
def get_student_progress(user_id):
    return fetch_all(
        """SELECT q.quiz_id, q.title, q.time_limit,
                  MAX(a.score)  AS best_score,
                  COUNT(a.attempt_id) AS attempts
           FROM   quizzes q
           LEFT JOIN attempts a ON a.quiz_id = q.quiz_id AND a.user_id = %s
           GROUP  BY q.quiz_id
           ORDER  BY q.title""",
        (user_id,)
    )

# Updates a quiz's title and time limit.
def update_quiz(quiz_id, title, time_limit):
    run_query(
        "UPDATE quizzes SET title=%s, time_limit=%s WHERE quiz_id=%s",
        (title, time_limit, quiz_id)
    )

