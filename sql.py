import sqlite3

def setup_database():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Drop existing tables if re-seeding cleanly
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS courses")

    # Create students table with expanded fields
    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            department TEXT,
            gpa REAL,
            city TEXT
        )
    """)

    # Create courses table
    cursor.execute("""
        CREATE TABLE courses (
            course_id INTEGER PRIMARY KEY,
            course_name TEXT,
            department TEXT,
            credits INTEGER
        )
    """)

    # Seed Students
    students_data = [
        (1, 'Pavan', 21, 'Computer Science', 3.85, 'Hyderabad'),
        (2, 'Rahul', 22, 'Electrical Eng', 3.50, 'Bangalore'),
        (3, 'Priya', 20, 'Computer Science', 3.92, 'Mumbai'),
        (4, 'Anjali', 19, 'Mechanical Eng', 3.25, 'Delhi'),
        (5, 'Kiran', 23, 'Business Admin', 3.60, 'Chennai'),
        (6, 'Sneha', 21, 'Data Science', 3.98, 'Pune'),
        (7, 'Vikram', 22, 'Data Science', 3.72, 'Hyderabad'),
        (8, 'Meera', 20, 'Electrical Eng', 3.45, 'Bangalore')
    ]
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", students_data)

    # Seed Courses
    courses_data = [
        (101, 'Introduction to Python', 'Computer Science', 4),
        (102, 'Data Structures & Algorithms', 'Computer Science', 4),
        (103, 'Circuit Analysis', 'Electrical Eng', 3),
        (104, 'Thermodynamics', 'Mechanical Eng', 4),
        (105, 'Machine Learning Fundamentals', 'Data Science', 4),
        (106, 'Financial Accounting', 'Business Admin', 3)
    ]
    cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?)", courses_data)

    conn.commit()

    # Quick Verification
    print("Database setup successfully!")
    print("\n--- Students Table ---")
    for row in cursor.execute("SELECT * FROM students"):
        print(row)

    print("\n--- Courses Table ---")
    for row in cursor.execute("SELECT * FROM courses"):
        print(row)

    conn.close()

if __name__ == "__main__":
    setup_database()