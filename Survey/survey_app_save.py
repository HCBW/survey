import json
import random
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# 数据库初始化
def init_db():
    try:
        conn = sqlite3.connect('survey_responses.db')
        c = conn.cursor()
        
        # 删除已存在的表（如果需要重置数据库的话）
        # c.execute('DROP TABLE IF EXISTS responses')
        
        # 创建表
        c.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                rankings TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

# 加载问卷数据
def load_surveys():
    with open('surveys.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 随机选择问卷并打乱问题和选项顺序
def get_random_survey():
    surveys = load_surveys()
    survey_id = random.choice(list(surveys.keys()))
    survey = surveys[survey_id]
    
    # 深拷贝问卷并打乱问题顺序
    shuffled_survey = {
        "title": survey["title"],
        "questions": survey["questions"].copy()
    }
    random.shuffle(shuffled_survey["questions"])
    
    # 打乱每个问题的选项顺序
    for question in shuffled_survey["questions"]:
        random.shuffle(question["options"])
    
    return survey_id, shuffled_survey

@app.route('/')
def index():
    survey_id, survey = get_random_survey()
    return render_template('survey.html', survey_id=survey_id, survey=survey)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        survey_id = request.form['survey_id']
        responses = {}
        
        # 打印接收到的表单数据，用于调试
        print("Received form data:", request.form)
        
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                rankings = value
                responses[question_id] = rankings
                # 打印每个问题的响应数据
                print(f"Question {question_id}: {rankings}")
        
        # 确保数据库连接正确关闭
        try:
            conn = sqlite3.connect('survey_responses.db')
            c = conn.cursor()
            
            # 打印要插入的数据
            for question_id, rankings in responses.items():
                print(f"Inserting: survey_id={survey_id}, question_id={question_id}, rankings={rankings}")
                c.execute('INSERT INTO responses (survey_id, question_id, rankings) VALUES (?, ?, ?)',
                         (survey_id, question_id, rankings))
            
            conn.commit()
            print("Data successfully saved to database")
            
        except Exception as e:
            print(f"Database error: {e}")
            return "数据保存失败", 500
        finally:
            conn.close()
        
        return redirect(url_for('thank_you'))
        
    except Exception as e:
        print(f"Error in submit: {e}")
        return "提交失败", 500

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001) 