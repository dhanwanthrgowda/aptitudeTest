from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Function to save user credentials
def save_user(username, password):
    with open('user_data/users.txt', 'a') as file:
        file.write(f"{username},{password}\n")

# Function to check if user exists
def check_user(username, password):
    with open('user_data/users.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            stored_username, stored_password = user.strip().split(',')
            if stored_username == username and stored_password == password:
                return True
    return False

# Function to check if username exists
def username_exists(username):
    with open('user_data/users.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            stored_username, _ = user.strip().split(',')
            if stored_username == username:
                return True
    return False

# Function to load questions from a file
def load_questions(file_path):
    with open(file_path, 'r') as file:
        questions = file.readlines()
    return [question.strip() for question in questions]

# Define the correct answers (you can modify this as per your needs)
correct_answers_easy = ["4", "8", "4"]
correct_answers_medium = ["180", "5", "75"]
correct_answers_difficult = ["12", "247"]

# Route for Home (Registration and Login page)
@app.route('/')
def home():
    return render_template('index.html')

# Route for Registration (Save new user)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        if username_exists(username):
            return "Username already exists. Please choose a different username.", 400

        # Save user credentials
        if username and password:
            save_user(username, password)
            return redirect(url_for('home'))
        else:
            return "Please provide both username and password", 400
    
    return render_template('register.html')

# Route for Login (User login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password are correct
        if check_user(username, password):
            # Store the username in session after successful login
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

# Route for Dashboard (Select difficulty level)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('dashboard.html')

# Route for Easy Questions
@app.route('/questions/easy')
def question_easy():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    # Load questions from the file
    questions = load_questions('questions/question_easy.txt')
    return render_template('question.html', questions=questions, level="Easy")

@app.route('/questions/medium')
def question_medium():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    # Load questions from the file
    questions = load_questions('questions/question_medium.txt')
    return render_template('question.html', questions=questions, level="Medium")

@app.route('/questions/tough')
def question_tough():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    # Load questions from the file
    questions = load_questions('questions/question_difficult.txt')
    return render_template('question.html', questions=questions, level="Tough")

# Route to handle answer submission
@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get the user's answers from the form
    answers = []
    for key, value in request.form.items():
        if key.startswith('answer_'):
            answers.append(value.strip())  # Strip leading/trailing spaces from answers

    # Determine which set of correct answers to use based on the level
    level = request.form.get('level')
    print(f"Level received: {level}")  
    if level == "Easy":
        correct_answers = correct_answers_easy
    elif level == "Medium":
        correct_answers = correct_answers_medium
    else:
        correct_answers = correct_answers_difficult

    # Compare answers (case insensitive and stripped of extra spaces)
    score = 0
    for user_answer, correct_answer in zip(answers, correct_answers):
        if user_answer.strip().lower() == correct_answer.strip().lower():  # Strip and convert to lower case for comparison
            score += 1

    # Render the result page with the score, answers, and level
    return render_template('results.html', 
                           level=level, 
                           score=score, 
                           total=len(correct_answers), 
                           answers=answers, 
                           correct_answers=correct_answers)

# Route for Logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to home page (login/registration)

if __name__ == '__main__':
    app.run(debug=True)  