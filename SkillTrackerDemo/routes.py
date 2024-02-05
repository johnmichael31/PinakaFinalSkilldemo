import hashlib
from flask import jsonify, render_template, request, redirect, url_for, session, flash
from SkillTrackerDemo import app, mysql
#login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            password_hash = data['password_hash']
            user_id = data['user_id']
            role = data['role']

            # Debug print (remove this in production)
            print(f"DB hash: {password_hash}")
            print(f"User entered password: {password_candidate}")

            # Hash the candidate password using MD5 and compare
            hashed_candidate = hashlib.md5(password_candidate.encode()).hexdigest()
            if hashed_candidate == password_hash:
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user_id
                session['role'] = role

                cur.close()

                if role == 'trainer':
                    return redirect(url_for('trainer_dashboard'))
                elif role == 'student':
                    return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid login')
        else:
            flash('Username not found')

        cur.close()

    return render_template('index.html')
 #trainer
@app.route('/trainer_dashboard')
def trainer_dashboard():
    if session.get('logged_in') and session.get('role') == 'trainer':
        # Trainer dashboard logic goes here
        return render_template('trainer_dashaboard.html')
    else:
        return redirect(url_for('login'))

#comptency management
@app.route('/competency_management')
def competency_management():
    if not session.get('logged_in') or session.get('role') != 'trainer':
        return redirect(url_for('login'))

    # Fetch competencies categorized and their learning outcomes
    basic_competencies = get_competencies_by_category('Basic')
    common_competencies = get_competencies_by_category('Common')
    core_competencies = get_competencies_by_category('Core')

    return render_template('competency_management.html',
                           basic_competencies=basic_competencies,
                           common_competencies=common_competencies,
                           core_competencies=core_competencies)
#display competency category
def get_competencies_by_category(category):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM competencies WHERE category = %s", (category,))
    competencies = cur.fetchall()
    for competency in competencies:
        competency['learning_outcomes'] = get_learning_outcomes_for_competency(competency['competency_id'])
    cur.close()
    return competencies

def get_learning_outcomes_for_competency(competency_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM learning_outcomes WHERE competency_id = %s", (competency_id,))
    outcomes = cur.fetchall()
    cur.close()
    return outcomes
#add competency
@app.route('/add_competency', methods=['POST'])
def add_competency():
    try:
        # Extract form data
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        duration = request.form.get('duration')

        # Perform your data validation here

        # Save competency to the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO competencies (title, description, nominal_duration_hrs, category) 
            VALUES (%s, %s, %s, %s)
        """, (title, description, duration, category))
        mysql.connection.commit()
        cur.close()

        # Return a success status in JSON format
        return jsonify({'status': 'success', 'message': 'Competency added successfully!'}), 200
    except Exception as e:
        # If an error occurs, return an error status in JSON format
        return jsonify({'status': 'error', 'message': str(e)}), 500
#update comptency
@app.route('/update_competency/<int:competency_id>', methods=['POST'])
def update_competency(competency_id):
    # Get form data
    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    duration = request.form.get('duration')

    # Update competency in the database
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE competencies
        SET title = %s, category = %s, description = %s, nominal_duration_hrs = %s
        WHERE competency_id = %s
    """, (title, category, description, duration, competency_id))
    mysql.connection.commit()
    cur.close()

    flash('Competency updated successfully!', 'success')
    return redirect(url_for('competency_management'))
#delete comptency
@app.route('/delete_competency/<int:competency_id>', methods=['POST'])
def delete_competency(competency_id):
    try:
        cur = mysql.connection.cursor()
        # First, delete any progress records associated with learning outcomes of this competency
        cur.execute("""
            DELETE progress
            FROM progress
            JOIN learning_outcomes ON progress.outcome_id = learning_outcomes.outcome_id
            WHERE learning_outcomes.competency_id = %s
        """, (competency_id,))
        # Then, delete the learning outcomes associated with this competency
        cur.execute("DELETE FROM learning_outcomes WHERE competency_id = %s", (competency_id,))
        # Finally, delete the competency itself
        cur.execute("DELETE FROM competencies WHERE competency_id = %s", (competency_id,))
        mysql.connection.commit()
        cur.close()
        flash('Competency deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting competency: ' + str(e), 'danger')
    return redirect(url_for('competency_management'))
# learning outcome (add)
@app.route('/add_learning_outcome', methods=['POST'])
def add_learning_outcome():
    competency_id = request.form.get('competency_id')
    description = request.form.get('description')

    if not competency_id or not description:
        return jsonify({'status': 'error', 'message': 'Competency ID and description are required.'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO learning_outcomes (competency_id, description) VALUES (%s, %s)", (competency_id, description))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'success', 'message': 'Learning outcome added successfully!'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error adding learning outcome: ' + str(e)}), 500
# learning outcome (edit)
@app.route('/edit_learning_outcome/<int:outcome_id>', methods=['POST'])
def edit_learning_outcome(outcome_id):
    description = request.form.get('description')

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE learning_outcomes
            SET description = %s
            WHERE outcome_id = %s
        """, (description, outcome_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'status': 'success', 'message': 'Learning outcome updated successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error updating learning outcome: ' + str(e)}), 500
# learning outcocme (delete)
@app.route('/delete_learning_outcome/<int:outcome_id>', methods=['POST'])
def delete_learning_outcome(outcome_id):
    try:
        cur = mysql.connection.cursor()
        # First, delete any progress records referencing this learning outcome
        cur.execute("DELETE FROM progress WHERE outcome_id = %s", (outcome_id,))
        # Then, delete the learning outcome itself
        cur.execute("DELETE FROM learning_outcomes WHERE outcome_id = %s", (outcome_id,))
        mysql.connection.commit()
        cur.close()
        # Since this is an AJAX call, return a success message in JSON format
        return jsonify({'status': 'success', 'message': 'Learning outcome deleted successfully!'}), 200
    except Exception as e:
        # Log the error and return an error message in JSON format
        print("Error deleting learning outcome:", e)
        return jsonify({'status': 'error', 'message': 'Error deleting learning outcome: ' + str(e)}), 500
 # learning outcome from editing
    @app.route('/get_learning_outcome_details/<int:outcome_id>')
    def get_learning_outcome_details(outcome_id):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM learning_outcomes WHERE outcome_id = %s", [outcome_id])
        if result > 0:
            outcome = cur.fetchone()
            return jsonify(outcome)
        else:
            return jsonify({'error': 'Learning outcome not found'}), 404
=======
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

