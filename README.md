# Mini Quora

Mini Quora is a simple college DBMS mini project built with Python, MySQL, and a desktop GUI using Tkinter. It works like a small software application instead of a website, so when you run `python app.py`, a desktop window opens.

## Project Description

This project is designed for beginners and college mini project submissions. It demonstrates:

- user registration and login
- password hashing
- storing questions and answers in MySQL
- simple voting on questions
- using foreign keys between tables
- showing user profile details and posted questions

The software uses a dark theme with orange buttons to keep the interface clean, modern, and easy to present.

## Modules

### 1. User Authentication
- Register a new user
- Login with email and password
- Password hashing using `Werkzeug`
- Simple in-app login state
- Logout option

### 2. Question Posting
- Logged-in user can post a question
- Fields: title, description, category

### 3. Reply / Answer Module
- Open a question from the home screen
- Add an answer
- View all answers for that question

### 4. Voting Module
- Upvote or downvote questions
- Vote count is stored in MySQL
- Duplicate vote checking is not added to keep the project simple

### 5. Profile Module
- View logged-in user details
- View all questions posted by the user

## Database Tables

### `users`
- `id`: primary key
- `username`: unique username
- `email`: unique email
- `password`: hashed password
- `created_at`: registration date and time

### `categories`
- `id`: primary key
- `name`: category name

### `questions`
- `id`: primary key
- `user_id`: foreign key from `users`
- `category_id`: foreign key from `categories`
- `title`: question title
- `description`: question details
- `upvotes`: total upvotes
- `downvotes`: total downvotes
- `created_at`: question creation date and time

### `answers`
- `id`: primary key
- `question_id`: foreign key from `questions`
- `user_id`: foreign key from `users`
- `answer_text`: answer content
- `created_at`: answer creation date and time

## Folder Structure

```text
mini_quora/
|-- app.py
|-- db.py
|-- schema.sql
|-- requirements.txt
|-- README.md
|-- templates/
`-- static/
```

Note:
- The current runnable version is the desktop software interface in `app.py`
- The `templates` and `static` folders can be kept as reference design files if you want

## Step-by-Step VS Code Setup

### 1. Create project folder
- Open VS Code
- Create a folder named `mini_quora`
- Place all project files inside it

### 2. Create virtual environment

```powershell
python -m venv venv
```

### 3. Activate virtual environment

```powershell
venv\Scripts\activate
```

### 4. Install requirements

```powershell
pip install -r requirements.txt
```

### 5. Import `schema.sql` in MySQL

Option 1 using MySQL command line:

```sql
SOURCE path_to_your_project/schema.sql;
```

Option 2 using MySQL Workbench:
- Open MySQL Workbench
- Open `schema.sql`
- Run the script

### 6. Edit `db.py` with MySQL username and password

Update:

```python
user="root",
password="your_mysql_password",
database="mini_quora",
```

### 7. Run the software

```powershell
python app.py
```

### 8. Use the application window

- A `Mini Quora` desktop window will open
- Login or register from the software
- Use the left-side menu to open Home, Ask Question, and Profile

## Common Errors and Fixes

### 1. `Access denied for user 'root'@'localhost'`
Reason:
- Wrong MySQL username or password in `db.py`

Fix:
- Update the correct MySQL username and password in `db.py`

### 2. `Unknown database 'mini_quora'`
Reason:
- The SQL file has not been imported

Fix:
- Run `schema.sql` in MySQL before starting the project

### 3. `ModuleNotFoundError`
Reason:
- Required libraries are not installed in the current Python environment

Fix:

```powershell
pip install -r requirements.txt
```

### 4. Desktop window does not open
Reason:
- Python may be installed without Tk support

Fix:
- Install standard Python from python.org
- Then run `python app.py` again

### 5. `mysql.connector.errors.InterfaceError`
Reason:
- MySQL server is not running

Fix:
- Start MySQL service, then run the app again

## Simple Working Flow

1. Register a new account
2. Login with your account
3. Open `Ask Question`
4. Post a new question
5. Open a question from the Home screen
6. Add an answer
7. Vote on questions
8. Check your profile page

## Notes

- This project is intentionally simple for a college mini project
- No website server is required
- No complex JavaScript is used
- No duplicate vote checking is added
- The interface is easy to customize
