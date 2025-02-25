import sqlite3
import json
import pandas as pd
import random

def analyze_survey_results():
    # Connect to database and get data
    conn = sqlite3.connect('survey_responses.db')
    
    # Debug: Print all data from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responses")
    print("Raw database data:", cursor.fetchall())
    
    # Read all responses with the correct schema
    df = pd.read_sql_query("""
        SELECT question_id, selected_option, not_selected_option, demographics, timestamp 
        FROM responses
    """, conn)
    
    print("DataFrame length:", len(df))
    print("DataFrame head:", df.head())
    
    # Check if data exists
    if len(df) == 0:
        print("No survey data in database.")
        # Create empty DataFrame with correct columns
        results_df = pd.DataFrame(columns=[
            'Question ID', 'Question', 'Option Number', 'Option', 
            'Times Selected', 'Times Lost', 'Selection Rate', 'Demographics'
        ])
        try:
            results_df.to_excel('survey_results.xlsx', index=False)
            print("Empty results file created as survey_results.xlsx")
        except Exception as e:
            print(f"\nError saving Excel file: {e}")
        finally:
            conn.close()
        return
    
    # Load survey data
    with open('surveys.json', 'r', encoding='utf-8') as f:
        survey_data = json.load(f)
    
    # Create results list
    all_results = []
    
    # Process each question from the survey data
    for question in survey_data['questions']:
        q_id = question['id']
        question_data = df[df['question_id'] == q_id]
        
        # Get all options for this question
        options = [
            question['option1'],
            question['option2'],
            question['option3'],
            question['option4'],
            question['option5']
        ]
        
        # Initialize counters for each option
        for option_num in range(1, 6):
            # Count wins (times selected) and losses (times explicitly not selected)
            times_selected = len(question_data[question_data['selected_option'] == option_num])
            times_not_selected = len(question_data[question_data['not_selected_option'] == option_num])
            total_appearances = times_selected + times_not_selected
            
            result = {
                'Question ID': q_id,
                'Question': question['text'],
                'Option Number': option_num,
                'Option': options[option_num - 1],
                'Times Selected': times_selected,
                'Times Lost': times_not_selected,
                'Selection Rate': round(times_selected / total_appearances, 3) if total_appearances > 0 else 0,
                'Demographics': question_data['demographics'].iloc[0] if len(question_data) > 0 else 0
            }
            all_results.append(result)
    
    # Create DataFrame and sort
    results_df = pd.DataFrame(all_results)
    
    # Convert Question ID to numeric by removing 'q' prefix and convert to numeric
    results_df['Question ID'] = results_df['Question ID'].str.replace('q', '').astype(int)
    results_df = results_df.sort_values('Question ID', ascending=True)
    
    # Reorder columns
    column_order = ['Question ID', 'Question', 'Option Number', 'Option', 
                   'Times Selected', 'Times Lost', 'Selection Rate', 'Demographics']
    results_df = results_df[column_order]
    
    try:
        # Save to Excel file
        results_df.to_excel('survey_results.xlsx', index=False)
        print("\nAnalysis results successfully saved to survey_results.xlsx")
    except Exception as e:
        print(f"\nError saving Excel file: {e}")
    finally:
        conn.close()



if __name__ == '__main__':
    analyze_survey_results() 