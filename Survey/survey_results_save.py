import sqlite3
import json
import pandas as pd

def analyze_survey_results():
    # 连接数据库并获取数据
    conn = sqlite3.connect('survey_responses.db')
    
    # 直接查看数据库中的数据（调试用）
    print("\n检查数据库中的数据：")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses")
    rows = cursor.fetchall()
    print(f"数据库中有 {len(rows)} 条记录")
    print("数据库记录详情：")
    for row in rows:
        print(f"Survey ID: {row[0]}, Question ID: {row[1]}, Rankings: {row[2]}")
    
    # 读取所有响应
    df = pd.read_sql_query("SELECT survey_id, question_id, rankings, timestamp FROM responses", conn)
    
    # 检查DataFrame（调试用）
    print("\n读取到的DataFrame：")
    print(df)
    print("\nDataFrame的唯一问题ID：")
    print(df['question_id'].unique())
    
    # 检查是否有数据
    if len(df) == 0:
        print("数据库中没有调查数据。")
        conn.close()
        return
    
    # 加载问卷数据
    with open('surveys.json', 'r', encoding='utf-8') as f:
        surveys = json.load(f)
    
    print("\n问卷中的问题：")
    for survey_id, survey in surveys.items():
        print(f"\n问卷 {survey_id}:")
        for question in survey['questions']:
            print(f"  问题ID: {question['id']}")
    
    # 创建结果列表
    all_results = []
    
    # 按问卷和问题分组处理数据
    for survey_id, survey in surveys.items():
        survey_data = df[df['survey_id'] == survey_id]
        
        for question in survey['questions']:
            base_id = question['id'].split('_')[0]  # 获取基础问题ID (q1, q2, q3)
            question_data = survey_data[survey_data['question_id'] == base_id]
            
            results = []
            # 处理该问题的所有响应
            for _, row in question_data.iterrows():
                rankings = row['rankings'].strip().split(',')
                
                # 为每个选项创建排名记录
                for i, option in enumerate(rankings, 1):
                    option = option.strip()
                    
                    # 查找现有记录或创建新记录
                    existing_record = None
                    for record in results:
                        if record['选项'] == option:
                            existing_record = record
                            break
                    
                    if existing_record is None:
                        existing_record = {
                            '问卷': survey['title'],
                            '问题编号': question['id'],
                            '问题': question['text'],
                            '选项': option,
                            '总投票数': 0,
                            '排名1': 0,
                            '排名2': 0,
                            '排名3': 0,
                            '排名4': 0,
                            '排名5': 0
                        }
                        results.append(existing_record)
                    
                    # 更新排名计数
                    existing_record[f'排名{i}'] += 1
                    existing_record['总投票数'] += 1
            
            # 计算平均排名
            for result in results:
                total_score = sum(i * result[f'排名{i}'] for i in range(1, 6))
                result['平均排名'] = round(total_score / result['总投票数'], 2) if result['总投票数'] > 0 else 0
            
            all_results.extend(results)
    
    # 创建DataFrame并排序
    results_df = pd.DataFrame(all_results)
    
    # 按问卷和问题编号排序
    results_df = results_df.sort_values(['问卷', '问题编号', '平均排名'])
    
    # 重新排列列顺序
    column_order = ['问卷', '问题编号', '问题', '选项', '平均排名', '总投票数', 
                   '排名1', '排名2', '排名3', '排名4', '排名5']
    results_df = results_df[column_order]
    
    try:
        # 保存为Excel文件
        results_df.to_excel('survey_results.xlsx', index=False)
        print("\n分析结果已成功保存到 survey_results.xlsx")
    except Exception as e:
        print(f"\n保存Excel文件时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    analyze_survey_results() 