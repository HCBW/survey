import json
import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import random
from datetime import datetime
import os

app = Flask(__name__)

# 数据库初始化
def init_db():
    """Initialize the database with the correct schema"""
    conn = sqlite3.connect('survey_responses.db')
    cursor = conn.cursor()
    
    # Create the table only if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id TEXT NOT NULL,
            selected_option INTEGER NOT NULL,
            not_selected_option INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            demographics INTEGER NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# 加载问卷数据
def load_surveys():
    with open('surveys.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 随机选择问卷并打乱问题和选项顺序
def get_random_questions():
    """Get a random set of questions for the survey"""
    surveys = load_surveys()
    
    # Get 15 random questions from the main questions array
    selected = random.sample(surveys['questions'], 15)
    
    # Convert numbered options to list format and select 2 random options for each question
    for q in selected:
        all_options = [
            {'number': 1, 'text': q.pop('option1')},
            {'number': 2, 'text': q.pop('option2')},
            {'number': 3, 'text': q.pop('option3')},
            {'number': 4, 'text': q.pop('option4')},
            {'number': 5, 'text': q.pop('option5')}
        ]
        # Randomly select 2 options from the 5
        selected_options = random.sample(all_options, 2)
        q['option1'] = selected_options[0]
        q['option2'] = selected_options[1]
    
    # Add the demographics question
    demographics = surveys['demographics'][0]
    selected.append(demographics)
    
    return selected

@app.route('/', methods=['GET'])
def index():
    questions = get_random_questions()
    return render_template('survey.html', 
                         questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    # Connect to database
    conn = sqlite3.connect('survey_responses.db')
    cursor = conn.cursor()
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Debug prints
    print("Form data received:", request.form)
    
    # Get demographics value first
    demographics_value = 0  # Default value
    for key, value in request.form.items():
        if key.startswith('question_d'):
            demographics_value = int(value.split(',')[0])
            print(f"Demographics value: {demographics_value}")  # Debug print
            break
    
    # Process each question's response (excluding demographics)
    for key, value in request.form.items():
        if key.startswith('question_q'):  # Only process regular questions
            question_id = key.split('_')[1]
            selected, not_selected = map(int, value.split(','))
            
            # Debug print
            print(f"Inserting: question_id={question_id}, selected={selected}, not_selected={not_selected}, demographics={demographics_value}")
            
            # Insert response into database with demographics value
            cursor.execute('''INSERT INTO responses 
                            (question_id, selected_option, not_selected_option, timestamp, demographics)
                            VALUES (?, ?, ?, ?, ?)''', 
                         (question_id, selected, not_selected, timestamp, demographics_value))
    
    # Debug: Check what was inserted
    cursor.execute("SELECT * FROM responses")
    print("Database contents after insert:", cursor.fetchall())
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

# Add this near your init_db() function to check permissions
def check_db_access():
    try:
        conn = sqlite3.connect('survey_responses.db')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("Database is accessible and writable")
        conn.close()
    except Exception as e:
        print(f"Database access error: {e}")

if __name__ == '__main__':
    check_db_access()  # Add this line before init_db()
    init_db()
    app.run(host="0.0.0.0", debug=True, port=5001)
