import tkinter as tk
from tkinter import messagebox, ttk

import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection


class MiniQuoraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Quora")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#090909")

        self.current_user = None
        self.categories = []

        self.ensure_default_admin()
        self.configure_styles()
        self.show_login_screen()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#181818",
            foreground="#f5f5f5",
            fieldbackground="#181818",
            rowheight=28,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#232323",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#ff7a00")])

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

        if commit:
            connection.commit()

        cursor.close()
        connection.close()
        return result

    def fetch_categories(self):
        self.categories = self.run_query(
            "SELECT id, name FROM categories ORDER BY name",
            fetchall=True,
        )

    def ensure_default_admin(self):
        existing_admin = self.run_query(
            "SELECT id FROM users WHERE username = %s",
            ("admin",),
            fetchone=True,
        )
        if existing_admin:
            return

        hashed_password = generate_password_hash("admin123")
        self.run_query(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            ("admin", "admin@miniquora.com", hashed_password),
            commit=True,
        )

    def build_entry(self, parent, label_text, show=None):
        tk.Label(
            parent,
            text=label_text,
            bg="#121212",
            fg="#f4f4f4",
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(fill="x", pady=(10, 4))

        entry = tk.Entry(
            parent,
            bg="#1c1c1c",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 11),
            show=show,
        )
        entry.pack(fill="x", ipady=10)
        return entry

    def show_login_screen(self):
        self.clear_root()

        outer = tk.Frame(self.root, bg="#090909")
        outer.pack(fill="both", expand=True)

        card = tk.Frame(
            outer,
            bg="#121212",
            highlightbackground="#262626",
            highlightthickness=1,
            padx=36,
            pady=36,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=500)

        tk.Label(
            card,
            text="Q",
            bg="#ff7a00",
            fg="#ffffff",
            font=("Segoe UI", 22, "bold"),
            width=2,
            height=1,
        ).pack(pady=(0, 18))

        tk.Label(
            card,
            text="Mini Quora",
            bg="#121212",
            fg="#ffffff",
            font=("Segoe UI", 24, "bold"),
        ).pack()
        tk.Label(
            card,
            text="Question & Answer Platform",
            bg="#121212",
            fg="#b8b8b8",
            font=("Segoe UI", 11),
        ).pack(pady=(6, 22))

        self.login_email = self.build_entry(card, "Username or Email")
        self.login_password = self.build_entry(card, "Password", show="*")

        tk.Button(
            card,
            text="Sign In",
            bg="#ff7a00",
            fg="#ffffff",
            activebackground="#ff9333",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            command=self.login_user,
        ).pack(fill="x", ipady=10, pady=(20, 10))

        tk.Button(
            card,
            text="Create Account",
            bg="#222222",
            fg="#ffffff",
            activebackground="#303030",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
            command=self.open_register_window,
        ).pack(fill="x", ipady=10)

        tk.Label(
            card,
            text="Mini Quora • 2026",
            bg="#121212",
            fg="#9a9a9a",
            font=("Segoe UI", 10),
        ).pack(side="bottom")

    def open_register_window(self):
        window = tk.Toplevel(self.root)
        window.title("Register - Mini Quora")
        window.geometry("430x470")
        window.configure(bg="#101010")
        window.resizable(False, False)

        card = tk.Frame(window, bg="#121212", padx=30, pady=30)
        card.place(relx=0.5, rely=0.5, anchor="center", width=370, height=400)

        tk.Label(
            card,
            text="Create Account",
            bg="#121212",
            fg="#ffffff",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(0, 12))

        username_entry = self.build_entry(card, "Username")
        email_entry = self.build_entry(card, "Email")
        password_entry = self.build_entry(card, "Password", show="*")

        def register_user():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not email or not password:
                messagebox.showerror("Error", "All fields are required.")
                return

            existing_user = self.run_query(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email),
                fetchone=True,
            )
            if existing_user:
                messagebox.showerror("Error", "Username or email already exists.")
                return

            hashed_password = generate_password_hash(password)
            self.run_query(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password),
                commit=True,
            )
            messagebox.showinfo("Success", "Registration successful. Please login.")
            window.destroy()

        tk.Button(
            card,
            text="Register",
            bg="#ff7a00",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            command=register_user,
        ).pack(fill="x", ipady=10, pady=(18, 0))

    def login_user(self):
        login_value = self.login_email.get().strip()
        password = self.login_password.get().strip()

        if not login_value or not password:
            messagebox.showerror("Error", "Please enter username/email and password.")
            return

        user = self.run_query(
            """
            SELECT id, username, email, password, created_at
            FROM users
            WHERE email = %s OR username = %s
            """,
            (login_value, login_value),
            fetchone=True,
        )

        if not user or not check_password_hash(user["password"], password):
            messagebox.showerror("Error", "Invalid username/email or password.")
            return

        self.current_user = user
        self.show_main_screen()

    def show_main_screen(self):
        self.clear_root()
        self.fetch_categories()

        container = tk.Frame(self.root, bg="#0d0d0d")
        container.pack(fill="both", expand=True)

        sidebar = tk.Frame(container, bg="#121212", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(container, bg="#0d0d0d")
        self.content.pack(side="right", fill="both", expand=True, padx=24, pady=24)

        tk.Label(
            sidebar,
            text="Mini Quora",
            bg="#121212",
            fg="#ffffff",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=(30, 4))
        tk.Label(
            sidebar,
            text="Question & Answer Platform",
            bg="#121212",
            fg="#a9a9a9",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 20))
        tk.Label(
            sidebar,
            text=f"Welcome, {self.current_user['username']}",
            bg="#121212",
            fg="#ffb164",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 20))

        self.sidebar_button(sidebar, "Home", self.show_home_page)
        self.sidebar_button(sidebar, "Ask Question", self.show_ask_page)
        self.sidebar_button(sidebar, "Profile", self.show_profile_page)
        self.sidebar_button(sidebar, "Refresh", self.show_home_page)
        self.sidebar_button(sidebar, "Logout", self.logout_user)

        self.show_home_page()

    def sidebar_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            bg="#1d1d1d",
            fg="#ffffff",
            activebackground="#ff7a00",
            activeforeground="#ffffff",
            relief="flat",
            font=("Segoe UI", 11),
            command=command,
        ).pack(fill="x", padx=18, pady=7, ipady=9)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home_page(self):
        self.clear_content()

        header = tk.Frame(self.content, bg="#151515", padx=20, pady=16)
        header.pack(fill="x", pady=(0, 16))

        tk.Label(
            header,
            text="Community Questions",
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Browse questions, open any post, and vote directly from the software.",
            bg="#151515",
            fg="#b8b8b8",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        columns = ("id", "title", "category", "author", "upvotes", "downvotes", "answers")
        self.question_tree = ttk.Treeview(self.content, columns=columns, show="headings")
        self.question_tree.pack(fill="both", expand=True)

        for column, label, width in [
            ("id", "ID", 60),
            ("title", "Title", 340),
            ("category", "Category", 130),
            ("author", "Author", 130),
            ("upvotes", "Upvotes", 80),
            ("downvotes", "Downvotes", 90),
            ("answers", "Answers", 80),
        ]:
            self.question_tree.heading(column, text=label)
            self.question_tree.column(column, width=width, anchor="center")

        self.question_tree.column("title", anchor="w")
        self.load_questions()

        actions = tk.Frame(self.content, bg="#0d0d0d")
        actions.pack(fill="x", pady=(14, 0))

        tk.Button(
            actions,
            text="Open Question",
            bg="#ff7a00",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            command=self.open_selected_question,
        ).pack(side="left", padx=(0, 10), ipadx=12, ipady=8)

        tk.Button(
            actions,
            text="Upvote",
            bg="#202020",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
            command=lambda: self.vote_question("up"),
        ).pack(side="left", padx=(0, 10), ipadx=12, ipady=8)

        tk.Button(
            actions,
            text="Downvote",
            bg="#202020",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
            command=lambda: self.vote_question("down"),
        ).pack(side="left", ipadx=12, ipady=8)

    def load_questions(self):
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)

        questions = self.run_query(
            """
            SELECT
                q.id,
                q.title,
                c.name AS category_name,
                u.username,
                q.upvotes,
                q.downvotes,
                (SELECT COUNT(*) FROM answers a WHERE a.question_id = q.id) AS answer_count
            FROM questions q
            INNER JOIN users u ON q.user_id = u.id
            INNER JOIN categories c ON q.category_id = c.id
            ORDER BY q.created_at DESC
            """,
            fetchall=True,
        )

        for question in questions:
            self.question_tree.insert(
                "",
                "end",
                values=(
                    question["id"],
                    question["title"],
                    question["category_name"],
                    question["username"],
                    question["upvotes"],
                    question["downvotes"],
                    question["answer_count"],
                ),
            )

    def get_selected_question_id(self):
        selected = self.question_tree.selection()
        if not selected:
            messagebox.showwarning("Select Question", "Please select a question first.")
            return None
        return int(self.question_tree.item(selected[0], "values")[0])

    def vote_question(self, vote_type):
        question_id = self.get_selected_question_id()
        if question_id is None:
            return

        if vote_type == "up":
            self.run_query(
                "UPDATE questions SET upvotes = upvotes + 1 WHERE id = %s",
                (question_id,),
                commit=True,
            )
            messagebox.showinfo("Success", "Upvote added.")
        else:
            self.run_query(
                "UPDATE questions SET downvotes = downvotes + 1 WHERE id = %s",
                (question_id,),
                commit=True,
            )
            messagebox.showinfo("Success", "Downvote added.")

        self.load_questions()

    def open_selected_question(self):
        question_id = self.get_selected_question_id()
        if question_id is None:
            return
        self.open_question_window(question_id)

    def open_question_window(self, question_id):
        question = self.run_query(
            """
            SELECT
                q.id,
                q.title,
                q.description,
                q.upvotes,
                q.downvotes,
                u.username,
                c.name AS category_name
            FROM questions q
            INNER JOIN users u ON q.user_id = u.id
            INNER JOIN categories c ON q.category_id = c.id
            WHERE q.id = %s
            """,
            (question_id,),
            fetchone=True,
        )

        if not question:
            messagebox.showerror("Error", "Question not found.")
            return

        answers = self.run_query(
            """
            SELECT a.answer_text, a.created_at, u.username
            FROM answers a
            INNER JOIN users u ON a.user_id = u.id
            WHERE a.question_id = %s
            ORDER BY a.created_at DESC
            """,
            (question_id,),
            fetchall=True,
        )

        window = tk.Toplevel(self.root)
        window.title("Question Details")
        window.geometry("780x620")
        window.configure(bg="#101010")

        container = tk.Frame(window, bg="#101010", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        top_card = tk.Frame(container, bg="#151515", padx=20, pady=20)
        top_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            top_card,
            text=question["title"],
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 18, "bold"),
            wraplength=700,
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            top_card,
            text=f"Category: {question['category_name']} | Posted by: {question['username']} | Upvotes: {question['upvotes']} | Downvotes: {question['downvotes']}",
            bg="#151515",
            fg="#ffb164",
            font=("Segoe UI", 10),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(8, 10))
        tk.Label(
            top_card,
            text=question["description"],
            bg="#151515",
            fg="#ececec",
            font=("Segoe UI", 11),
            wraplength=700,
            justify="left",
        ).pack(anchor="w")

        bottom_card = tk.Frame(container, bg="#151515", padx=20, pady=20)
        bottom_card.pack(fill="both", expand=True)

        tk.Label(
            bottom_card,
            text="Answers",
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        answer_list = tk.Listbox(
            bottom_card,
            bg="#1d1d1d",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
        )
        answer_list.pack(fill="both", expand=True, pady=(12, 16))

        if answers:
            for answer in answers:
                answer_list.insert("end", f"{answer['username']}: {answer['answer_text']}")
                answer_list.insert("end", f"Posted on: {answer['created_at']}")
                answer_list.insert("end", "-" * 90)
        else:
            answer_list.insert("end", "No answers yet.")

        tk.Label(
            bottom_card,
            text="Add Answer",
            bg="#151515",
            fg="#f4f4f4",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        answer_box = tk.Text(
            bottom_card,
            height=5,
            bg="#1d1d1d",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
        )
        answer_box.pack(fill="x", pady=(8, 12))

        def submit_answer():
            answer_text = answer_box.get("1.0", "end").strip()
            if not answer_text:
                messagebox.showwarning("Empty Answer", "Please write an answer.")
                return

            self.run_query(
                "INSERT INTO answers (question_id, user_id, answer_text) VALUES (%s, %s, %s)",
                (question_id, self.current_user["id"], answer_text),
                commit=True,
            )
            messagebox.showinfo("Success", "Answer added successfully.")
            window.destroy()
            self.load_questions()
            self.open_question_window(question_id)

        tk.Button(
            bottom_card,
            text="Submit Answer",
            bg="#ff7a00",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            command=submit_answer,
        ).pack(anchor="e", ipadx=12, ipady=8)

    def show_ask_page(self):
        self.clear_content()
        self.fetch_categories()

        card = tk.Frame(self.content, bg="#151515", padx=24, pady=24)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text="Ask a Question",
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            card,
            text="Fill the details below to post a new question.",
            bg="#151515",
            fg="#b8b8b8",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 18))

        title_entry = self.build_entry(card, "Question Title")

        tk.Label(
            card,
            text="Category",
            bg="#151515",
            fg="#f4f4f4",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(10, 4))

        category_box = ttk.Combobox(
            card,
            values=[category["name"] for category in self.categories],
            state="readonly",
            font=("Segoe UI", 10),
        )
        category_box.pack(fill="x", ipady=6)

        tk.Label(
            card,
            text="Description",
            bg="#151515",
            fg="#f4f4f4",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(10, 4))

        description_box = tk.Text(
            card,
            height=12,
            bg="#1d1d1d",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 10),
        )
        description_box.pack(fill="both", expand=True)

        def post_question():
            title = title_entry.get().strip()
            category_name = category_box.get().strip()
            description = description_box.get("1.0", "end").strip()

            if not title or not category_name or not description:
                messagebox.showerror("Error", "Please fill all fields.")
                return

            category = next(
                (item for item in self.categories if item["name"] == category_name),
                None,
            )
            if not category:
                messagebox.showerror("Error", "Please select a valid category.")
                return

            self.run_query(
                """
                INSERT INTO questions (user_id, category_id, title, description)
                VALUES (%s, %s, %s, %s)
                """,
                (self.current_user["id"], category["id"], title, description),
                commit=True,
            )
            messagebox.showinfo("Success", "Question posted successfully.")
            self.show_home_page()

        tk.Button(
            card,
            text="Post Question",
            bg="#ff7a00",
            fg="#ffffff",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            command=post_question,
        ).pack(anchor="e", pady=(16, 0), ipadx=12, ipady=8)

    def show_profile_page(self):
        self.clear_content()

        user = self.run_query(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (self.current_user["id"],),
            fetchone=True,
        )

        questions = self.run_query(
            """
            SELECT q.id, q.title, c.name AS category_name, q.upvotes, q.downvotes
            FROM questions q
            INNER JOIN categories c ON q.category_id = c.id
            WHERE q.user_id = %s
            ORDER BY q.created_at DESC
            """,
            (self.current_user["id"],),
            fetchall=True,
        )

        top_card = tk.Frame(self.content, bg="#151515", padx=24, pady=24)
        top_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            top_card,
            text="My Profile",
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            top_card,
            text=f"Username: {user['username']}",
            bg="#151515",
            fg="#ededed",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(14, 4))
        tk.Label(
            top_card,
            text=f"Email: {user['email']}",
            bg="#151515",
            fg="#ededed",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=4)
        tk.Label(
            top_card,
            text=f"Joined: {user['created_at']}",
            bg="#151515",
            fg="#ededed",
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=4)

        bottom_card = tk.Frame(self.content, bg="#151515", padx=24, pady=24)
        bottom_card.pack(fill="both", expand=True)

        tk.Label(
            bottom_card,
            text="My Questions",
            bg="#151515",
            fg="#ffffff",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", pady=(0, 12))

        columns = ("id", "title", "category", "upvotes", "downvotes")
        tree = ttk.Treeview(bottom_card, columns=columns, show="headings")
        tree.pack(fill="both", expand=True)

        for column, label, width in [
            ("id", "ID", 60),
            ("title", "Title", 360),
            ("category", "Category", 140),
            ("upvotes", "Upvotes", 100),
            ("downvotes", "Downvotes", 100),
        ]:
            tree.heading(column, text=label)
            tree.column(column, width=width, anchor="center")

        tree.column("title", anchor="w")

        for question in questions:
            tree.insert(
                "",
                "end",
                values=(
                    question["id"],
                    question["title"],
                    question["category_name"],
                    question["upvotes"],
                    question["downvotes"],
                ),
            )

    def logout_user(self):
        self.current_user = None
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        MiniQuoraApp(root)
        root.mainloop()
    except mysql.connector.Error as error:
        root.withdraw()
        messagebox.showerror(
            "Database Connection Error",
            "Mini Quora could not connect to MySQL.\n\n"
            "Please check:\n"
            "1. MySQL server is running\n"
            "2. The database name is mini_quora\n"
            "3. Your MySQL username/password are correct\n"
            "4. schema.sql has been imported\n\n"
            f"Error: {error}"
        )
    except Exception as error:
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"Mini Quora could not start.\n\nError: {error}"
        )
