from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages

# Simple in-memory data store for users and expenses
users_db = {}
expenses_db = {}  # Stores expense data

@app.route('/', methods=['GET', 'POST'])
def home():
    # Check if the user is logged in
    if 'username' not in session:
        flash('You need to log in first!', 'error')
        return redirect(url_for('login'))

    # Get the selected category from the request
    selected_category = request.args.get('category', '')

    # Calculate total expenses and balance
    total_expenses = sum(float(expense['amount']) for expense in expenses_db.values())
    balance = session.get('income', 0) - total_expenses

    # Filter expenses by category if selected
    if selected_category:
        filtered_expenses = {k: v for k, v in expenses_db.items() if v['category'] == selected_category}
    else:
        filtered_expenses = expenses_db

    # Get all categories to populate the dropdown
    categories = set(expense['category'] for expense in expenses_db.values())

    return render_template('home.html',
                           balance=balance,
                           total_expenses=total_expenses,
                           expenses=filtered_expenses,
                           categories=categories,
                           selected_category=selected_category)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the password and confirmation password match
        if password != confirm_password:
            flash('Passwords do not match! Please re-enter your password.', 'error')
            return redirect(url_for('register'))  # Redirect to register page

        # Check if the username already exists
        if username in users_db:
            flash('Username already exists!', 'error')  # Flash message for duplicate username
            return redirect(url_for('register'))  # Redirect to register page

        # Save the new user (in-memory database)
        users_db[username] = password
        flash('Registration successful! Please log in.', 'success')  # Flash message for successful registration
        return redirect(url_for('login'))  # Redirect to login page

    return render_template('register.html')  # Show the registration page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists
        if username not in users_db:
            flash('Username does not exist!', 'error')  # Flash message for non-existent username
            return redirect(url_for('login'))

        # Check if the password matches
        if users_db[username] != password:
            flash('Incorrect password!', 'error')  # Flash message for incorrect password
            return redirect(url_for('login'))

        # Set the session variable for the logged-in user
        session['username'] = username

        flash('Login successful!', 'success')  # Flash message for successful login
        return redirect(url_for('home'))  # Redirect to home page after successful login

    return render_template('login.html')  # Show the login page

@app.route('/logout')
def logout():
    # Clear any flash messages that might be lingering in the session
    session.clear()  # Clears the entire session, including user data
    flash('You have been logged out.', 'success')  # Flash message for logout
    return redirect(url_for('login'))  # Redirect to login page after logging out

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        expense_name = request.form['name']
        expense_amount = request.form['amount']
        expense_category = request.form['category']
        expense_date = request.form['date']

        # Generate a unique ID for each expense
        expense_id = len(expenses_db) + 1

        # Store the expense
        expenses_db[expense_id] = {
            'name': expense_name,
            'amount': expense_amount,
            'category': expense_category,
            'date': expense_date
        }

        flash('Expense added successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    # Retrieve expenses from session or database
    expenses = session.get('expenses', {})

    if request.method == 'POST':
        try:
            # Get the income values from the form
            income_name = request.form['income_name']
            income_amount = float(request.form['income_amount'])
            income_category = request.form['income_category']

            # Check if incomes are stored in the session, if not, initialize as an empty list
            if 'incomes' not in session:
                session['incomes'] = []

            # Append the new income with its name, amount, and category
            income_data = {
                'name': income_name,
                'amount': income_amount,
                'category': income_category
            }
            session['incomes'].append(income_data)

            # Update total income in the session by summing all income entries
            total_income = sum(item['amount'] for item in session['incomes'])
            session['income'] = total_income  # Update the session with the new total income

            flash(f'Income "{income_name}" of {income_amount} added successfully!', 'success')
        except ValueError:
            flash('Invalid income value! Please enter a valid number.', 'error')
        return redirect(url_for('home'))

    return render_template('add_income.html', expenses=expenses)  # Make sure expenses are passed to the template

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    # Check if the expense exists
    if expense_id not in expenses_db:
        flash('Expense not found!', 'error')
        return redirect(url_for('home'))

    expense = expenses_db[expense_id]

    if request.method == 'POST':
        # Update the expense details
        expense['name'] = request.form['name']
        expense['amount'] = float(request.form['amount'])
        expense['category'] = request.form['category']
        expense['date'] = request.form['date']

        flash('Expense updated successfully!', 'success')
        return redirect(url_for('home'))

    # Render the edit form with current expense data
    return render_template('edit_expense.html', expense=expense)


@app.route('/delete_expense/<int:expense_id>', methods=['GET', 'POST'])
def delete_expense(expense_id):
    if expense_id in expenses_db:
        del expenses_db[expense_id]  # Delete the expense from the database
        flash('Expense deleted successfully!', 'success')
    else:
        flash('Expense not found!', 'error')
    return redirect(url_for('home'))  # Redirect to home page after deletion

if __name__ == '__main__':
    app.run(debug=True)
