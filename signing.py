from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the sign up page
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Handle sign-up form submission
        # For demonstration purposes, assume the form is always valid
        return redirect(url_for('profile'))
    return render_template('sign_up.html')

# Route for the sign in page
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        print("Sign-in form submitted")  # Debugging statement
        # Handle sign-in form submission
        # For demonstration purposes, assume the sign-in is successful
        return redirect(url_for('dashboard'))
    return render_template('sign_in.html')

# Route for the profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    
    if request.method == 'POST':
        # Handle profile form submission
        return redirect('/dashboard')
    return render_template('profile.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
