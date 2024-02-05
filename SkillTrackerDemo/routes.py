from flask import flash, redirect, render_template, session
from SkillTrackerDemo import app,mysql





# student
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('logged_in') and session.get('role') == 'student':
        user_id = session.get('user_id')
        progress_data, overall_progress_percentage = get_student_progress(user_id)
        learning_outcomes = get_upcoming_learning_outcomes(user_id)  # Keep this line to fetch learning outcomes

        return render_template('student_dashboard.html', 
                               progress_data=progress_data, 
                               overall_progress_percentage=overall_progress_percentage,
                               learning_outcomes=learning_outcomes)  # Pass learning outcomes to the template
    else:
        return redirect(url_for('login'))

def get_student_progress(user_id):
    # Connect to the database
    cur = mysql.connection.cursor()
    
    # Fetch individual progress records
    cur.execute("""
        SELECT c.title AS competency_title, lo.description AS outcome_description, p.status, p.date_completed
        FROM progress p
        JOIN learning_outcomes lo ON p.outcome_id = lo.outcome_id
        JOIN competencies c ON lo.competency_id = c.competency_id
        WHERE p.user_id = %s
    """, (user_id,))
    progress_records = cur.fetchall()
    
    # Calculate the overall progress percentage
    # Here we assume that each learning outcome contributes equally to the overall progress.
    # Adjust this logic based on your application's rules for calculating overall progress.
    num_outcomes = len(progress_records)
    completed_outcomes = sum(1 for record in progress_records if record['status'] == 'completed')
    overall_progress_percentage = (completed_outcomes / num_outcomes * 100) if num_outcomes > 0 else 0
    
    # Format progress data for the template
    progress_data = [
        {
            'competency_title': record['competency_title'],
            'outcome_description': record['outcome_description'],
            'status': record['status'],
            'date_completed': record['date_completed'].strftime('%B %d, %Y') if record['date_completed'] else 'Not completed'
        }
        for record in progress_records
    ]
    
    cur.close()
    
    return progress_data, overall_progress_percentage

def get_upcoming_learning_outcomes(user_id):
    # Connect to the database
    cur = mysql.connection.cursor()
    
    # Query to join learning_outcomes with progress based on user_id
    cur.execute("""
        SELECT lo.description, p.status
        FROM learning_outcomes lo
        INNER JOIN progress p ON lo.outcome_id = p.outcome_id
        WHERE p.user_id = %s
    """, (user_id,))
    
    # Fetch all the results
    outcomes_records = cur.fetchall()
    
    # Close the connection
    cur.close()
    
    # Process the records into the expected format
    learning_outcomes = [
        {
            'description': record['description'],
            'status': record['status'] if record['status'] else 'not_started'  # Default to 'not_started' if status is None
        }
        for record in outcomes_records
    ]
    
    return learning_outcomes



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

