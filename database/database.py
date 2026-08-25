import os
import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DB_PATH = os.path.join(
    DATA_DIR,
    "bsc_app.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def connect_database():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password):

    return generate_password_hash(
        password
    )


def verify_password(
    password_hash,
    password
):

    return check_password_hash(
        password_hash,
        password
    )


# ============================================================
# DATABASE MIGRATION HELPER
# ============================================================

def ensure_column(
    cursor,
    table_name,
    column_name,
    column_definition
):

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if column_name not in columns:

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition}
            """
        )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = connect_database()
    cursor = connection.cursor()


    # ========================================================
    # DEPARTMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (

            department_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL,

            description TEXT,

            hod_name TEXT,

            hod_email TEXT,

            hod_phone TEXT,

            department_location TEXT
        )
    """)

    ensure_column(
        cursor,
        "departments",
        "department_location",
        "TEXT"
    )


    # ========================================================
    # BSC COMBINATIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combinations (

            combination_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE NOT NULL,

            description TEXT
        )
    """)


    # ========================================================
    # STUDENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (

            student_id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            email TEXT UNIQUE,

            phone TEXT,

            date_of_birth TEXT,

            address TEXT,

            password TEXT NOT NULL,

            year INTEGER NOT NULL,

            combination_id INTEGER,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (combination_id)
            REFERENCES combinations(combination_id)
        )
    """)

    ensure_column(
        cursor,
        "students",
        "phone",
        "TEXT"
    )

    ensure_column(
        cursor,
        "students",
        "date_of_birth",
        "TEXT"
    )

    ensure_column(
        cursor,
        "students",
        "address",
        "TEXT"
    )

    ensure_column(
        cursor,
        "students",
        "created_at",
        "TEXT"
    )


    # ========================================================
    # ADMINS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (

            admin_id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            email TEXT,

            password TEXT NOT NULL,

            role TEXT NOT NULL,

            department_id INTEGER,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
        )
    """)

    ensure_column(
        cursor,
        "admins",
        "role",
        "TEXT"
    )

    ensure_column(
        cursor,
        "admins",
        "department_id",
        "INTEGER"
    )


    # ========================================================
    # FACULTY
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (

            faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            designation TEXT,

            qualification TEXT,

            email TEXT,

            phone TEXT,

            office_location TEXT,

            photo TEXT,

            department_id INTEGER NOT NULL,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
        )
    """)

    ensure_column(
        cursor,
        "faculty",
        "office_location",
        "TEXT"
    )

    ensure_column(
        cursor,
        "faculty",
        "photo",
        "TEXT"
    )


    # ========================================================
    # SUBJECTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (

            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            subject_code TEXT,

            department_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            semester INTEGER,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
        )
    """)

    # Fix older database versions
    ensure_column(
        cursor,
        "subjects",
        "subject_code",
        "TEXT"
    )

    ensure_column(
        cursor,
        "subjects",
        "semester",
        "INTEGER"
    )


    # ========================================================
    # COMBINATION SUBJECTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combination_subjects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            combination_id INTEGER NOT NULL,

            subject_id INTEGER NOT NULL,

            UNIQUE(
                combination_id,
                subject_id
            ),

            FOREIGN KEY (combination_id)
            REFERENCES combinations(combination_id),

            FOREIGN KEY (subject_id)
            REFERENCES subjects(subject_id)
        )
    """)


    # ========================================================
    # TIMETABLE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (

            timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,

            combination_id INTEGER NOT NULL,

            year INTEGER NOT NULL,

            day TEXT NOT NULL,

            period1 TEXT,

            period2 TEXT,

            period3 TEXT,

            period4 TEXT,

            period5 TEXT,

            UNIQUE(
                combination_id,
                year,
                day
            ),

            FOREIGN KEY (combination_id)
            REFERENCES combinations(combination_id)
        )
    """)

    ensure_column(
        cursor,
        "timetable",
        "period5",
        "TEXT"
    )


    # ========================================================
    # ATTENDANCE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (

            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            subject_id INTEGER NOT NULL,

            attendance_month TEXT,

            present_classes INTEGER NOT NULL,

            total_classes INTEGER NOT NULL,

            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (student_id)
            REFERENCES students(student_id),

            FOREIGN KEY (subject_id)
            REFERENCES subjects(subject_id)
        )
    """)

    # Upgrade older attendance table
    ensure_column(
        cursor,
        "attendance",
        "attendance_month",
        "TEXT"
    )

    ensure_column(
        cursor,
        "attendance",
        "updated_at",
        "TEXT"
    )

    # If old database used month + academic_year,
    # convert those values to YYYY-MM.
    cursor.execute(
        "PRAGMA table_info(attendance)"
    )

    attendance_columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if (
        "month" in attendance_columns
        and
        "academic_year" in attendance_columns
    ):

        cursor.execute("""
            UPDATE attendance

            SET attendance_month =
                printf(
                    '%04d-%02d',
                    academic_year,
                    month
                )

            WHERE
                attendance_month IS NULL
                OR attendance_month = ''
        """)


    # ========================================================
    # RESULTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (

            result_id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            subject_id INTEGER NOT NULL,

            semester INTEGER NOT NULL,

            academic_year TEXT,

            marks REAL,

            max_marks REAL,

            grade TEXT,

            result_status TEXT,

            FOREIGN KEY (student_id)
            REFERENCES students(student_id),

            FOREIGN KEY (subject_id)
            REFERENCES subjects(subject_id)
        )
    """)

    ensure_column(
        cursor,
        "results",
        "academic_year",
        "TEXT"
    )

    ensure_column(
        cursor,
        "results",
        "result_status",
        "TEXT"
    )


    # ========================================================
    # NOTICES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notices (

            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            message TEXT NOT NULL,

            category TEXT DEFAULT 'General',

            image TEXT,

            issued_department_id INTEGER,

            target_department_id INTEGER,

            target_year INTEGER,

            created_by TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (issued_department_id)
            REFERENCES departments(department_id),

            FOREIGN KEY (target_department_id)
            REFERENCES departments(department_id),

            FOREIGN KEY (created_by)
            REFERENCES admins(admin_id)
        )
    """)


    # ========================================================
    # UPGRADE OLD NOTICE TABLE
    # ========================================================

    ensure_column(
        cursor,
        "notices",
        "category",
        "TEXT DEFAULT 'General'"
    )

    ensure_column(
        cursor,
        "notices",
        "image",
        "TEXT"
    )

    ensure_column(
        cursor,
        "notices",
        "issued_department_id",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "notices",
        "target_department_id",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "notices",
        "target_year",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "notices",
        "created_by",
        "TEXT"
    )

    ensure_column(
        cursor,
        "notices",
        "created_at",
        "TEXT"
    )

    ensure_column(
    cursor,
    "notices",
    "is_pinned",
    "INTEGER DEFAULT 0"
)

    # ========================================================
    # FAQ / KNOWLEDGE BASE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (

            faq_id INTEGER PRIMARY KEY AUTOINCREMENT,

            question TEXT NOT NULL,

            answer TEXT NOT NULL,

            department_id INTEGER,

            subject_id INTEGER,

            created_by TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id),

            FOREIGN KEY (subject_id)
            REFERENCES subjects(subject_id),

            FOREIGN KEY (created_by)
            REFERENCES admins(admin_id)
        )
    """)

    ensure_column(
        cursor,
        "faqs",
        "department_id",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "faqs",
        "subject_id",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "faqs",
        "created_by",
        "TEXT"
    )


    # ========================================================
    # LIBRARY
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS library (

            library_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            description TEXT,

            opening_time TEXT,

            closing_time TEXT,

            librarian_name TEXT,

            librarian_email TEXT,

            contact TEXT,

            location TEXT
        )
    """)


    # ========================================================
    # LIBRARY BOOK CATALOGUE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (

            book_id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            author TEXT NOT NULL,

            description TEXT,

            availability TEXT DEFAULT 'Available',

            added_by TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(title, author),

            FOREIGN KEY (added_by)
            REFERENCES admins(admin_id)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_recommendations (

            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,

            book_id INTEGER NOT NULL,

            department_id INTEGER NOT NULL,

            recommended_by TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(book_id, department_id),

            FOREIGN KEY (book_id)
            REFERENCES books(book_id)
            ON DELETE CASCADE,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id),

            FOREIGN KEY (recommended_by)
            REFERENCES admins(admin_id)
        )
    """)


    # ========================================================
    # ANONYMOUS STUDENT COMPLAINTS
    # No student identity or account reference is stored.
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anonymous_complaints (

            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,

            subject TEXT NOT NULL,

            category TEXT NOT NULL,

            complaint_text TEXT NOT NULL,

            status TEXT DEFAULT 'New',

            admin_note TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            reviewed_at TEXT
        )
    """)


    # ========================================================
    # COLLEGE INFORMATION
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college_info (

            college_id INTEGER PRIMARY KEY AUTOINCREMENT,

            college_name TEXT,

            description TEXT,

            history TEXT,

            address TEXT,

            phone TEXT,

            email TEXT,

            website TEXT,

            map_link TEXT,

            principal_name TEXT,

            office_hours TEXT
        )
    """)


    # ========================================================
    # LABORATORIES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laboratories (

            lab_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT,

            location TEXT,

            department_id INTEGER,

            image TEXT,

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
        )
    """)


    # ========================================================
    # DEFAULT DEPARTMENTS
    # ========================================================

    departments = [

        ("Mathematics",),
        ("Physics",),
        ("Computer Science",),
        ("Statistics",),
        ("Chemistry",),
        ("Zoology",),
        ("Botany",),
        ("Library",)

    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO departments (
            name
        )

        VALUES (?)
    """, departments)


    # ========================================================
    # DEFAULT COMBINATIONS
    # ========================================================

    combinations = [

        (
            "PMCS",
            "Physics, Mathematics, Computer Science and Statistics"
        ),

        (
            "PMC",
            "Physics, Mathematics and Computer Science"
        ),

        (
            "CZBT",
            "Chemistry, Zoology and Botany"
        )

    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO combinations (
            name,
            description
        )

        VALUES (?, ?)
    """, combinations)


    # ========================================================
    # DEFAULT SUBJECTS - YEAR 1
    # ========================================================

    subject_data = [

        (
            "Physics",
            "PHY101",
            "Physics",
            1,
            1
        ),

        (
            "Mathematics",
            "MAT101",
            "Mathematics",
            1,
            1
        ),

        (
            "Computer Science",
            "CSC101",
            "Computer Science",
            1,
            1
        ),

        (
            "Statistics",
            "STA101",
            "Statistics",
            1,
            1
        ),

        (
            "Chemistry",
            "CHE101",
            "Chemistry",
            1,
            1
        ),

        (
            "Zoology",
            "ZOO101",
            "Zoology",
            1,
            1
        ),

        (
            "Botany",
            "BOT101",
            "Botany",
            1,
            1
        )

    ]


    for (
        subject_name,
        subject_code,
        department_name,
        year,
        semester
    ) in subject_data:

        cursor.execute("""
            SELECT department_id

            FROM departments

            WHERE name = ?
        """, (
            department_name,
        ))

        department = cursor.fetchone()

        if department:

            cursor.execute("""
                SELECT subject_id

                FROM subjects

                WHERE
                    name = ?
                    AND department_id = ?
                    AND year = ?
            """, (
                subject_name,
                department["department_id"],
                year
            ))

            existing_subject = cursor.fetchone()

            if existing_subject:

                cursor.execute("""
                    UPDATE subjects

                    SET
                        subject_code = ?,
                        semester = ?

                    WHERE subject_id = ?
                """, (
                    subject_code,
                    semester,
                    existing_subject["subject_id"]
                ))

            else:

                cursor.execute("""
                    INSERT INTO subjects (
                        name,
                        subject_code,
                        department_id,
                        year,
                        semester
                    )

                    VALUES (?, ?, ?, ?, ?)
                """, (
                    subject_name,
                    subject_code,
                    department["department_id"],
                    year,
                    semester
                ))


    # ========================================================
    # CONNECT SUBJECTS TO COMBINATIONS
    # ========================================================

    combination_subject_map = {

        "PMCS": [
            "Physics",
            "Mathematics",
            "Computer Science",
            "Statistics"
        ],

        "PMC": [
            "Physics",
            "Mathematics",
            "Computer Science"
        ],

        "CZBT": [
            "Chemistry",
            "Zoology",
            "Botany"
        ]

    }


    for (
        combination_name,
        subject_names
    ) in combination_subject_map.items():

        cursor.execute("""
            SELECT combination_id

            FROM combinations

            WHERE name = ?
        """, (
            combination_name,
        ))

        combination = cursor.fetchone()

        if combination:

            for subject_name in subject_names:

                cursor.execute("""
                    SELECT subject_id

                    FROM subjects

                    WHERE
                        name = ?
                        AND year = 1
                """, (
                    subject_name,
                ))

                subject = cursor.fetchone()

                if subject:

                    cursor.execute("""
                        INSERT OR IGNORE INTO
                        combination_subjects (
                            combination_id,
                            subject_id
                        )

                        VALUES (?, ?)
                    """, (
                        combination["combination_id"],
                        subject["subject_id"]
                    ))


    # ========================================================
    # TEST STUDENT
    # ========================================================

    cursor.execute("""
        SELECT combination_id

        FROM combinations

        WHERE name = ?
    """, (
        "PMCS",
    ))

    pmcs = cursor.fetchone()

    if pmcs:

        cursor.execute("""
            SELECT student_id

            FROM students

            WHERE student_id = ?
        """, (
            "BSC001",
        ))

        student_exists = cursor.fetchone()

        if student_exists is None:

            cursor.execute("""
                INSERT INTO students (

                    student_id,
                    name,
                    email,
                    phone,
                    date_of_birth,
                    address,
                    password,
                    year,
                    combination_id

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (

                "BSC001",

                "Demo Student",

                "student@bsc.app",

                "",

                "",

                "",

                hash_password("1234"),

                1,

                pmcs["combination_id"]

            ))


    # ========================================================
    # SUPER ADMIN
    # ========================================================

    cursor.execute("""
        SELECT admin_id

        FROM admins

        WHERE admin_id = ?
    """, (
        "ADMIN001",
    ))

    admin_exists = cursor.fetchone()

    if admin_exists is None:

        cursor.execute("""
            INSERT INTO admins (

                admin_id,
                name,
                email,
                password,
                role,
                department_id

            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (

            "ADMIN001",

            "Super Admin",

            "admin@bsc.app",

            hash_password("786"),

            "super_admin",

            None

        ))

            # ========================================================
    # DEFAULT DEPARTMENT ADMINS
    # ========================================================

    department_admins = [

        (
            "MATH001",
            "Mathematics Admin",
            "Mathematics",
            "math123"
        ),

        (
            "PHY001",
            "Physics Admin",
            "Physics",
            "physics123"
        ),

        (
            "CS001",
            "Computer Science Admin",
            "Computer Science",
            "cs123"
        ),

        (
            "STAT001",
            "Statistics Admin",
            "Statistics",
            "stat123"
        ),

        (
            "CHEM001",
            "Chemistry Admin",
            "Chemistry",
            "chem123"
        ),

        (
            "ZOO001",
            "Zoology Admin",
            "Zoology",
            "zoo123"
        ),

        (
            "BOT001",
            "Botany Admin",
            "Botany",
            "bot123"
        ),

        (
            "LIB001",
            "Library Admin",
            "Library",
            "library123"
        )

    ]


    for (
        admin_id,
        admin_name,
        department_name,
        password
    ) in department_admins:

        cursor.execute("""
            SELECT department_id
            FROM departments
            WHERE name = ?
        """, (
            department_name,
        ))

        department = cursor.fetchone()

        if department:

            cursor.execute("""
                SELECT admin_id
                FROM admins
                WHERE admin_id = ?
            """, (
                admin_id,
            ))

            existing_admin = cursor.fetchone()

            if existing_admin is None:

                cursor.execute("""
                    INSERT INTO admins (
                        admin_id,
                        name,
                        email,
                        password,
                        role,
                        department_id
                    )

                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    admin_id,
                    admin_name,
                    "",
                    hash_password(password),
                    "department_admin",
                    department["department_id"]
                ))


    # ========================================================
    # SAVE DATABASE
    # ========================================================

    connection.commit()
    connection.close()


# ============================================================
# STUDENT LOGIN
# ============================================================

def login_student(
    student_id,
    password
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            students.*,
            combinations.name
            AS combination_name

        FROM students

        LEFT JOIN combinations

        ON students.combination_id =
           combinations.combination_id

        WHERE students.student_id = ?
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    connection.close()

    if student is None:

        return None

    if verify_password(
        student["password"],
        password
    ):

        return student

    return None


# ============================================================
# ADMIN LOGIN
# ============================================================

def login_admin(
    admin_id,
    password
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            admins.*,

            departments.name
            AS department_name

        FROM admins

        LEFT JOIN departments

        ON admins.department_id =
           departments.department_id

        WHERE admins.admin_id = ?
    """, (
        admin_id,
    ))

    admin = cursor.fetchone()

    connection.close()

    if admin is None:

        return None

    if verify_password(
        admin["password"],
        password
    ):

        return admin

    return None


# ============================================================
# GET STUDENT
# ============================================================

def get_student(
    student_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            students.student_id,

            students.name,

            students.email,

            students.phone,

            students.date_of_birth,

            students.address,

            students.year,

            students.combination_id,

            combinations.name
            AS combination_name

        FROM students

        LEFT JOIN combinations

        ON students.combination_id =
           combinations.combination_id

        WHERE students.student_id = ?
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    connection.close()

    return student


# ============================================================
# GET ALL STUDENTS
# ============================================================

def get_all_students():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            students.student_id,

            students.name,

            students.year,

            combinations.name
            AS combination_name

        FROM students

        LEFT JOIN combinations

        ON students.combination_id =
           combinations.combination_id

        ORDER BY students.name
    """)

    students = cursor.fetchall()

    connection.close()

    return students


# ============================================================
# GET ALL DEPARTMENTS
# ============================================================

def get_all_departments():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM departments

        ORDER BY name
    """)

    departments = cursor.fetchall()

    connection.close()

    return departments


# ============================================================
# GET ALL COMBINATIONS
# ============================================================

def get_all_combinations():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM combinations

        ORDER BY name
    """)

    combinations = cursor.fetchall()

    connection.close()

    return combinations


# ============================================================
# GET SUBJECTS FOR STUDENT
# ============================================================

def get_subjects_for_student(
    student_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT

            subjects.subject_id,

            subjects.name,

            subjects.subject_code

        FROM students

        JOIN combination_subjects

        ON students.combination_id =
           combination_subjects.combination_id

        JOIN subjects

        ON combination_subjects.subject_id =
           subjects.subject_id

        WHERE
            students.student_id = ?

        ORDER BY subjects.name
    """, (
        student_id,
    ))

    subjects = cursor.fetchall()

    connection.close()

    return subjects


# ============================================================
# GET ATTENDANCE FOR ONE MONTH
# ============================================================

def get_attendance_for_month(
    student_id,
    attendance_month
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            attendance.*,

            subjects.name
            AS subject_name

        FROM attendance

        JOIN subjects

        ON attendance.subject_id =
           subjects.subject_id

        WHERE
            attendance.student_id = ?
            AND attendance.attendance_month = ?

        ORDER BY subjects.name
    """, (
        student_id,
        attendance_month
    ))

    attendance = cursor.fetchall()

    connection.close()

    return attendance


# ============================================================
# GET ALL ATTENDANCE FOR STUDENT
# ============================================================

def get_student_attendance(
    student_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            attendance.attendance_id,

            attendance.attendance_month,

            attendance.present_classes,

            attendance.total_classes,

            subjects.subject_id,

            subjects.name
            AS subject_name

        FROM attendance

        JOIN subjects

        ON attendance.subject_id =
           subjects.subject_id

        WHERE attendance.student_id = ?

        ORDER BY
            attendance.attendance_month ASC,
            subjects.name ASC
    """, (
        student_id,
    ))

    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# GET NOTICES FOR STUDENT
# ============================================================

def get_notices_for_student(
    year
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM notices

        WHERE
            target_year IS NULL

            OR target_year = ?

        ORDER BY created_at DESC

        LIMIT 5
    """, (
        year,
    ))

    notices = cursor.fetchall()

    connection.close()

    return notices

# ============================================================
# SAVE / UPDATE RESULT
# ============================================================

def save_result(
    student_id,
    subject_id,
    semester,
    academic_year,
    marks,
    max_marks,
    grade,
    result_status
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT result_id
        FROM results

        WHERE student_id = ?
        AND subject_id = ?
        AND semester = ?
        AND academic_year = ?
    """, (
        student_id,
        subject_id,
        semester,
        academic_year
    ))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE results

            SET
                marks = ?,
                max_marks = ?,
                grade = ?,
                result_status = ?

            WHERE result_id = ?
        """, (
            marks,
            max_marks,
            grade,
            result_status,
            existing["result_id"]
        ))

    else:

        cursor.execute("""
            INSERT INTO results (
                student_id,
                subject_id,
                semester,
                academic_year,
                marks,
                max_marks,
                grade,
                result_status
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            subject_id,
            semester,
            academic_year,
            marks,
            max_marks,
            grade,
            result_status
        ))

    connection.commit()
    connection.close()


# ============================================================
# GET RESULTS FOR ONE SEMESTER
# ============================================================

def get_results_for_semester(
    student_id,
    semester,
    academic_year
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            results.*,
            subjects.name AS subject_name

        FROM results

        JOIN subjects
        ON results.subject_id =
           subjects.subject_id

        WHERE results.student_id = ?
        AND results.semester = ?
        AND results.academic_year = ?

        ORDER BY subjects.name
    """, (
        student_id,
        semester,
        academic_year
    ))

    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# GET ALL RESULTS FOR STUDENT
# ============================================================

def get_student_results(student_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            results.*,
            subjects.name AS subject_name,
            subjects.subject_code

        FROM results

        JOIN subjects
        ON results.subject_id =
           subjects.subject_id

        WHERE results.student_id = ?

        ORDER BY
            results.academic_year DESC,
            results.semester DESC,
            subjects.name
    """, (
        student_id,
    ))

    records = cursor.fetchall()

    connection.close()

    return records

    # ============================================================
# GET ONE DEPARTMENT
# ============================================================

def get_department(department_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM departments
        WHERE department_id = ?
    """, (
        department_id,
    ))

    department = cursor.fetchone()

    connection.close()

    return department


# ============================================================
# GET FACULTY BY DEPARTMENT
# ============================================================

def get_faculty_by_department(department_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM faculty
        WHERE department_id = ?
        ORDER BY name
    """, (
        department_id,
    ))

    faculty = cursor.fetchall()

    connection.close()

    return faculty


# ============================================================
# GET SUBJECTS BY DEPARTMENT
# ============================================================

def get_subjects_by_department(department_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subjects
        WHERE department_id = ?
        ORDER BY year, semester, name
    """, (
        department_id,
    ))

    subjects = cursor.fetchall()

    connection.close()

    return subjects


# ============================================================
# UPDATE HOD / DEPARTMENT DETAILS
# ============================================================

def update_department_details(
    department_id,
    description,
    hod_name,
    hod_email,
    hod_phone,
    department_location
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE departments

        SET
            description = ?,
            hod_name = ?,
            hod_email = ?,
            hod_phone = ?,
            department_location = ?

        WHERE department_id = ?
    """, (
        description,
        hod_name,
        hod_email,
        hod_phone,
        department_location,
        department_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# ADD FACULTY
# ============================================================

def add_faculty(
    name,
    designation,
    qualification,
    email,
    phone,
    office_location,
    department_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO faculty (
            name,
            designation,
            qualification,
            email,
            phone,
            office_location,
            department_id
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        designation,
        qualification,
        email,
        phone,
        office_location,
        department_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# DELETE FACULTY
# ============================================================

def delete_faculty(faculty_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM faculty
        WHERE faculty_id = ?
    """, (
        faculty_id,
    ))

    connection.commit()
    connection.close()

    # ========================================================
# DEPARTMENT CHAT CONVERSATIONS
# ========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (

        conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,

        student_id TEXT NOT NULL,

        department_id INTEGER NOT NULL,

        status TEXT DEFAULT 'open',

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        last_message_at TEXT DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(student_id, department_id),

        FOREIGN KEY (student_id)
        REFERENCES students(student_id),

        FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
    )
""")


# ========================================================
# DEPARTMENT CHAT MESSAGES
# ========================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (

        message_id INTEGER PRIMARY KEY AUTOINCREMENT,

        conversation_id INTEGER NOT NULL,

        sender_type TEXT NOT NULL,

        sender_id TEXT NOT NULL,

        message_text TEXT,

        image TEXT,

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,

        is_read INTEGER DEFAULT 0,

        FOREIGN KEY (conversation_id)
        REFERENCES conversations(conversation_id)
        ON DELETE CASCADE
    )
""")

    # ============================================================
# GET FAQS BY DEPARTMENT
# ============================================================

def get_faqs_by_department(department_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            faqs.*,
            subjects.name AS subject_name

        FROM faqs

        LEFT JOIN subjects
        ON faqs.subject_id = subjects.subject_id

        WHERE faqs.department_id = ?

        ORDER BY faqs.created_at DESC
    """, (
        department_id,
    ))

    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# ADD FAQ
# ============================================================

def add_faq(
    question,
    answer,
    department_id,
    subject_id,
    created_by
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO faqs (
            question,
            answer,
            department_id,
            subject_id,
            created_by
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        question,
        answer,
        department_id,
        subject_id,
        created_by
    ))

    connection.commit()
    connection.close()


# ============================================================
# DELETE FAQ
# ============================================================

def delete_faq(
    faq_id,
    department_id
):

    connection = connect_database()
    cursor = connection.cursor()

    # Department admin can only delete
    # FAQ from their own department
    cursor.execute("""
        DELETE FROM faqs

        WHERE faq_id = ?
        AND department_id = ?
    """, (
        faq_id,
        department_id
    ))

    connection.commit()
    connection.close()



# ============================================================
# SEARCH ALL FAQ KNOWLEDGE
# ============================================================

def search_faqs(
    search_text,
    department_id=None,
    subject_id=None
):

    connection = connect_database()
    cursor = connection.cursor()


    # ========================================================
    # LOAD KNOWLEDGE
    # ========================================================

    # If a department is supplied, filtering still works.
    # If no department is supplied, search ALL departments.

    if department_id and subject_id:

        cursor.execute("""
            SELECT
                faqs.*,
                departments.name AS department_name,
                subjects.name AS subject_name

            FROM faqs

            JOIN departments
            ON faqs.department_id =
               departments.department_id

            LEFT JOIN subjects
            ON faqs.subject_id =
               subjects.subject_id

            WHERE faqs.department_id = ?

            AND (
                faqs.subject_id = ?
                OR faqs.subject_id IS NULL
            )
        """, (
            department_id,
            subject_id
        ))


    elif department_id:

        cursor.execute("""
            SELECT
                faqs.*,
                departments.name AS department_name,
                subjects.name AS subject_name

            FROM faqs

            JOIN departments
            ON faqs.department_id =
               departments.department_id

            LEFT JOIN subjects
            ON faqs.subject_id =
               subjects.subject_id

            WHERE faqs.department_id = ?
        """, (
            department_id,
        ))


    else:

        # ----------------------------------------------------
        # GENERAL STUDENT ASSISTANT
        # SEARCH EVERY DEPARTMENT
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                faqs.*,
                departments.name AS department_name,
                subjects.name AS subject_name

            FROM faqs

            JOIN departments
            ON faqs.department_id =
               departments.department_id

            LEFT JOIN subjects
            ON faqs.subject_id =
               subjects.subject_id
        """)


    records = cursor.fetchall()

    connection.close()


    # ========================================================
    # CLEAN STUDENT QUESTION
    # ========================================================

    cleaned_query = ""

    for character in search_text.lower():

        if character.isalnum():

            cleaned_query += character

        else:

            cleaned_query += " "


    query_words = set(
        cleaned_query.split()
    )


    # ========================================================
    # IGNORE COMMON WORDS
    # ========================================================

    ignored_words = {
        "what",
        "is",
        "the",
        "a",
        "an",
        "of",
        "for",
        "in",
        "to",
        "and",
        "who",
        "where",
        "how",
        "can",
        "could",
        "would",
        "i",
        "my",
        "me",
        "do",
        "does",
        "are",
        "was",
        "when"
    }


    query_words = (
        query_words - ignored_words
    )


    # ========================================================
    # SCORE ANSWERS
    # ========================================================

    scored_results = []


    for record in records:

        question_text = (
            record["question"]
            or ""
        ).lower()


        answer_text = (
            record["answer"]
            or ""
        ).lower()


        department_text = (
            record["department_name"]
            or ""
        ).lower()


        subject_text = (
            record["subject_name"]
            or ""
        ).lower()


        score = 0


        for word in query_words:

            # FAQ question is most important
            if word in question_text:
                score += 4

            # Department name helps identify context
            if word in department_text:
                score += 3

            # Subject name also helps
            if word in subject_text:
                score += 3

            # Answer text is useful but less important
            if word in answer_text:
                score += 1


        if score > 0:

            scored_results.append(
                (
                    score,
                    record
                )
            )


    # Highest scoring answer first

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )


    return [
        item[1]
        for item in scored_results[:5]
    ]

# ============================================================
# GET OR CREATE CONVERSATION
# ============================================================

def get_or_create_conversation(
    student_id,
    department_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM conversations

        WHERE student_id = ?
        AND department_id = ?
    """, (
        student_id,
        department_id
    ))

    conversation = cursor.fetchone()

    if conversation:

        connection.close()
        return conversation


    cursor.execute("""
        INSERT INTO conversations (
            student_id,
            department_id
        )

        VALUES (?, ?)
    """, (
        student_id,
        department_id
    ))

    conversation_id = (
        cursor.lastrowid
    )

    connection.commit()


    cursor.execute("""
        SELECT *

        FROM conversations

        WHERE conversation_id = ?
    """, (
        conversation_id,
    ))

    conversation = cursor.fetchone()

    connection.close()

    return conversation


# ============================================================
# GET ONE CONVERSATION
# ============================================================

def get_conversation(
    conversation_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            conversations.*,

            students.name
            AS student_name,

            departments.name
            AS department_name

        FROM conversations

        JOIN students
        ON conversations.student_id =
           students.student_id

        JOIN departments
        ON conversations.department_id =
           departments.department_id

        WHERE conversations.conversation_id = ?
    """, (
        conversation_id,
    ))

    conversation = cursor.fetchone()

    connection.close()

    return conversation


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    conversation_id,
    sender_type,
    sender_id,
    message_text=None,
    image=None
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            conversation_id,
            sender_type,
            sender_id,
            message_text,
            image,
            is_read
        )

        VALUES (?, ?, ?, ?, ?, 0)
    """, (
        conversation_id,
        sender_type,
        sender_id,
        message_text,
        image
    ))


    cursor.execute("""
        UPDATE conversations

        SET last_message_at =
            CURRENT_TIMESTAMP

        WHERE conversation_id = ?
    """, (
        conversation_id,
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET CONVERSATION MESSAGES
# ============================================================

def get_conversation_messages(
    conversation_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM messages

        WHERE conversation_id = ?

        ORDER BY
            created_at ASC,
            message_id ASC
    """, (
        conversation_id,
    ))

    messages = cursor.fetchall()

    connection.close()

    return messages


# ============================================================
# STUDENT CONVERSATION LIST
# ============================================================

def get_student_conversations(student_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            conversations.*,

            departments.name AS department_name,

            (
                SELECT message_text

                FROM messages

                WHERE
                    messages.conversation_id =
                    conversations.conversation_id

                ORDER BY message_id DESC

                LIMIT 1
            )
            AS last_message,

            (
                SELECT COUNT(*)

                FROM messages

                WHERE
                    messages.conversation_id =
                    conversations.conversation_id

                AND messages.sender_type != 'student'

                AND messages.is_read = 0
            )
            AS unread_count

        FROM conversations

        JOIN departments

        ON conversations.department_id =
           departments.department_id

        WHERE conversations.student_id = ?

        ORDER BY
            conversations.last_message_at DESC
    """, (
        student_id,
    ))

    conversations = cursor.fetchall()

    connection.close()

    return conversations


# ============================================================
# DEPARTMENT CONVERSATION LIST
# ============================================================

def get_department_conversations(
    department_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            conversations.*,

            students.name
            AS student_name,

            students.year,

            combinations.name
            AS combination_name,

            (
                SELECT message_text

                FROM messages

                WHERE
                    messages.conversation_id =
                    conversations.conversation_id

                ORDER BY message_id DESC

                LIMIT 1
            )
            AS last_message,

            (
                SELECT COUNT(*)

                FROM messages

                WHERE
                    messages.conversation_id =
                    conversations.conversation_id

                AND messages.sender_type =
                    'student'

                AND messages.is_read = 0
            )
            AS unread_count

        FROM conversations

        JOIN students
        ON conversations.student_id =
           students.student_id

        LEFT JOIN combinations
        ON students.combination_id =
           combinations.combination_id

        WHERE conversations.department_id = ?

        ORDER BY
            conversations.last_message_at DESC
    """, (
        department_id,
    ))

    conversations = cursor.fetchall()

    connection.close()

    return conversations


# ============================================================
# MARK MESSAGES AS READ
# ============================================================

def mark_messages_read(
    conversation_id,
    reader_type
):

    connection = connect_database()
    cursor = connection.cursor()


    # Department opening the conversation
    if reader_type == "department":

        cursor.execute("""
            UPDATE messages

            SET is_read = 1

            WHERE conversation_id = ?
            AND sender_type = 'student'
        """, (
            conversation_id,
        ))


    # Student opening the conversation
    elif reader_type == "student":

        cursor.execute("""
            UPDATE messages

            SET is_read = 1

            WHERE conversation_id = ?
            AND sender_type != 'student'
        """, (
            conversation_id,
        ))


    connection.commit()
    connection.close()

# ============================================================
# GET STUDENTS CONNECTED TO A DEPARTMENT
# ============================================================

def get_students_for_department(department_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT
            students.student_id,
            students.name,
            students.year,
            combinations.name AS combination_name

        FROM students

        JOIN combinations
        ON students.combination_id =
           combinations.combination_id

        JOIN combination_subjects
        ON combinations.combination_id =
           combination_subjects.combination_id

        JOIN subjects
        ON combination_subjects.subject_id =
           subjects.subject_id

        WHERE subjects.department_id = ?

        ORDER BY students.name
    """, (
        department_id,
    ))

    students = cursor.fetchall()

    connection.close()

    return students

# ============================================================
# INITIALIZE MESSAGING TABLES
# ============================================================

def initialize_messaging_tables():

    connection = connect_database()
    cursor = connection.cursor()


    # ========================================================
    # CONVERSATIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT NOT NULL,

            department_id INTEGER NOT NULL,

            status TEXT DEFAULT 'open',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            last_message_at TEXT DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(
                student_id,
                department_id
            ),

            FOREIGN KEY (student_id)
            REFERENCES students(student_id),

            FOREIGN KEY (department_id)
            REFERENCES departments(department_id)
        )
    """)


    # ========================================================
    # MESSAGES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            message_id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL,

            sender_type TEXT NOT NULL,

            sender_id TEXT NOT NULL,

            message_text TEXT,

            image TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            is_read INTEGER DEFAULT 0,

            FOREIGN KEY (conversation_id)
            REFERENCES conversations(conversation_id)
            ON DELETE CASCADE
        )
    """)


    connection.commit()
    connection.close()

# ============================================================
# SAVE / UPDATE TIMETABLE
# ============================================================

def save_timetable(
    combination_id,
    year,
    day,
    period1,
    period2,
    period3,
    period4,
    period5
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO timetable (
            combination_id,
            year,
            day,
            period1,
            period2,
            period3,
            period4,
            period5
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(
            combination_id,
            year,
            day
        )

        DO UPDATE SET

            period1 = excluded.period1,
            period2 = excluded.period2,
            period3 = excluded.period3,
            period4 = excluded.period4,
            period5 = excluded.period5
    """, (
        combination_id,
        year,
        day,
        period1,
        period2,
        period3,
        period4,
        period5
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET TIMETABLE
# ============================================================

def get_timetable(
    combination_id,
    year
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM timetable

        WHERE combination_id = ?
        AND year = ?
    """, (
        combination_id,
        year
    ))

    records = cursor.fetchall()

    connection.close()


    day_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }


    records = sorted(
        records,
        key=lambda row: day_order.get(
            row["day"],
            99
        )
    )

    return records

# ============================================================
# CREATE STUDENT
# ============================================================

def create_student(
    student_id,
    name,
    email,
    phone,
    date_of_birth,
    address,
    password,
    year,
    combination_id
):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO students (
                student_id,
                name,
                email,
                phone,
                date_of_birth,
                address,
                password,
                year,
                combination_id
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            name,
            email if email else None,
            phone,
            date_of_birth,
            address,
            hash_password(password),
            year,
            combination_id
        ))

        connection.commit()

        return True, "Student added successfully."

    except sqlite3.IntegrityError:

        return (
            False,
            "Student ID or email already exists."
        )

    finally:

        connection.close()


# ============================================================
# UPDATE STUDENT
# ============================================================

def update_student(
    student_id,
    name,
    email,
    phone,
    date_of_birth,
    address,
    year,
    combination_id
):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE students

            SET
                name = ?,
                email = ?,
                phone = ?,
                date_of_birth = ?,
                address = ?,
                year = ?,
                combination_id = ?

            WHERE student_id = ?
        """, (
            name,
            email if email else None,
            phone,
            date_of_birth,
            address,
            year,
            combination_id,
            student_id
        ))

        connection.commit()

        return True, "Student updated successfully."

    except sqlite3.IntegrityError:

        return (
            False,
            "That email is already being used by another student."
        )

    finally:

        connection.close()


# ============================================================
# RESET STUDENT PASSWORD
# ============================================================

def reset_student_password(
    student_id,
    new_password
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE students

        SET password = ?

        WHERE student_id = ?
    """, (
        hash_password(new_password),
        student_id
    ))

    connection.commit()
    connection.close()


# ============================================================
# DELETE STUDENT
# ============================================================

def delete_student(
    student_id
):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        # Remove attendance
        cursor.execute("""
            DELETE FROM attendance
            WHERE student_id = ?
        """, (
            student_id,
        ))


        # Remove results
        cursor.execute("""
            DELETE FROM results
            WHERE student_id = ?
        """, (
            student_id,
        ))


        # Remove conversations.
        # Messages connected to these conversations
        # are deleted by ON DELETE CASCADE.
        cursor.execute("""
            DELETE FROM conversations
            WHERE student_id = ?
        """, (
            student_id,
        ))


        # Finally remove student
        cursor.execute("""
            DELETE FROM students
            WHERE student_id = ?
        """, (
            student_id,
        ))


        connection.commit()

        return True

    except sqlite3.Error:

        connection.rollback()

        return False

    finally:

        connection.close()


# ============================================================
# SEARCH STUDENTS
# ============================================================

def search_students(
    search_text=""
):

    connection = connect_database()
    cursor = connection.cursor()


    if search_text:

        search_value = (
            "%"
            + search_text
            + "%"
        )

        cursor.execute("""
            SELECT
                students.student_id,
                students.name,
                students.email,
                students.phone,
                students.year,

                combinations.name
                AS combination_name

            FROM students

            LEFT JOIN combinations
            ON students.combination_id =
               combinations.combination_id

            WHERE
                students.student_id LIKE ?
                OR students.name LIKE ?
                OR students.email LIKE ?

            ORDER BY students.name
        """, (
            search_value,
            search_value,
            search_value
        ))

    else:

        cursor.execute("""
            SELECT
                students.student_id,
                students.name,
                students.email,
                students.phone,
                students.year,

                combinations.name
                AS combination_name

            FROM students

            LEFT JOIN combinations
            ON students.combination_id =
               combinations.combination_id

            ORDER BY students.name
        """)


    students = cursor.fetchall()

    connection.close()

    return students


# ============================================================
# GET TIMETABLE
# ============================================================

def get_timetable(
    combination_id,
    year
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM timetable

        WHERE combination_id = ?
        AND year = ?

        ORDER BY
            CASE day
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                ELSE 7
            END
    """, (
        combination_id,
        year
    ))

    records = cursor.fetchall()

    connection.close()

    return records


# ============================================================
# SAVE / UPDATE ONE TIMETABLE DAY
# ============================================================

def save_timetable_day(
    combination_id,
    year,
    day,
    period1,
    period2,
    period3,
    period4,
    period5
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timetable_id

        FROM timetable

        WHERE combination_id = ?
        AND year = ?
        AND day = ?
    """, (
        combination_id,
        year,
        day
    ))

    existing = cursor.fetchone()


    if existing:

        cursor.execute("""
            UPDATE timetable

            SET
                period1 = ?,
                period2 = ?,
                period3 = ?,
                period4 = ?,
                period5 = ?

            WHERE timetable_id = ?
        """, (
            period1,
            period2,
            period3,
            period4,
            period5,
            existing["timetable_id"]
        ))

    else:

        cursor.execute("""
            INSERT INTO timetable (
                combination_id,
                year,
                day,
                period1,
                period2,
                period3,
                period4,
                period5
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            combination_id,
            year,
            day,
            period1,
            period2,
            period3,
            period4,
            period5
        ))


    connection.commit()
    connection.close()

    # ============================================================
# GET TODAY'S TIMETABLE FOR STUDENT
# ============================================================

def get_student_timetable_for_day(
    student_id,
    day
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            timetable.*,
            combinations.name AS combination_name,
            students.year

        FROM students

        JOIN combinations
        ON students.combination_id =
           combinations.combination_id

        JOIN timetable
        ON timetable.combination_id =
           students.combination_id

        WHERE students.student_id = ?
        AND timetable.year = students.year
        AND LOWER(timetable.day) = LOWER(?)

        LIMIT 1
    """, (
        student_id,
        day
    ))

    timetable = cursor.fetchone()

    connection.close()

    return timetable

# ============================================================
# CREATE NOTICE
# ============================================================

def create_notice(
    title,
    message,
    category,
    image,
    issued_department_id,
    target_department_id,
    target_year,
    created_by
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO notices (

            title,
            message,
            category,
            image,
            issued_department_id,
            target_department_id,
            target_year,
            created_by

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        title,
        message,
        category,
        image,
        issued_department_id,
        target_department_id,
        target_year,
        created_by

    ))

    connection.commit()
    connection.close()


# ============================================================
# GET NOTICES FOR ADMIN
# ============================================================

def get_notices_for_admin(
    role,
    department_id=None
):

    connection = connect_database()
    cursor = connection.cursor()


    # --------------------------------------------------------
    # SUPER ADMIN
    # --------------------------------------------------------

    if role == "super_admin":

        cursor.execute("""
            SELECT

                notices.*,

                issued_department.name
                AS issued_department_name,

                target_department.name
                AS target_department_name

            FROM notices

            LEFT JOIN departments
                AS issued_department

            ON notices.issued_department_id =
               issued_department.department_id


            LEFT JOIN departments
                AS target_department

            ON notices.target_department_id =
               target_department.department_id


            ORDER BY
                notices.created_at DESC
        """)


    # --------------------------------------------------------
    # DEPARTMENT ADMIN
    # --------------------------------------------------------

    else:

        cursor.execute("""
            SELECT

                notices.*,

                issued_department.name
                AS issued_department_name,

                target_department.name
                AS target_department_name

            FROM notices

            LEFT JOIN departments
                AS issued_department

            ON notices.issued_department_id =
               issued_department.department_id


            LEFT JOIN departments
                AS target_department

            ON notices.target_department_id =
               target_department.department_id


            WHERE
                notices.issued_department_id = ?


            ORDER BY
                notices.created_at DESC
        """, (
            department_id,
        ))


    notices = cursor.fetchall()

    connection.close()

    return notices


# ============================================================
# DELETE NOTICE
# ============================================================

def delete_notice(
    notice_id,
    role,
    department_id=None
):

    connection = connect_database()
    cursor = connection.cursor()


    # Super Admin can delete any notice
    if role == "super_admin":

        cursor.execute("""
            DELETE FROM notices
            WHERE notice_id = ?
        """, (
            notice_id,
        ))


    # Department admin can delete
    # only their own department notices
    else:

        cursor.execute("""
            DELETE FROM notices

            WHERE notice_id = ?

            AND issued_department_id = ?
        """, (
            notice_id,
            department_id
        ))


    connection.commit()
    connection.close()


# ============================================================
# GET NOTICE IMAGE
# ============================================================

def get_notice(
    notice_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *

        FROM notices

        WHERE notice_id = ?
    """, (
        notice_id,
    ))

    notice = cursor.fetchone()

    connection.close()

    return notice


# ============================================================
# GET FILTERED NOTICES FOR STUDENT
# ============================================================

def get_filtered_notices_for_student(
    student_id
):

    connection = connect_database()
    cursor = connection.cursor()


    # --------------------------------------------------------
    # GET STUDENT
    # --------------------------------------------------------

    cursor.execute("""
        SELECT

            student_id,
            year,
            combination_id

        FROM students

        WHERE student_id = ?
    """, (
        student_id,
    ))

    student = cursor.fetchone()


    if student is None:

        connection.close()

        return []


    # --------------------------------------------------------
    # DEPARTMENTS CONNECTED TO STUDENT'S COMBINATION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT DISTINCT
            subjects.department_id

        FROM combination_subjects

        JOIN subjects

        ON combination_subjects.subject_id =
           subjects.subject_id

        WHERE
            combination_subjects.combination_id = ?
    """, (
        student["combination_id"],
    ))


    department_rows = cursor.fetchall()


    department_ids = [

        row["department_id"]

        for row in department_rows

    ]


    # --------------------------------------------------------
    # GET POSSIBLE NOTICES
    # --------------------------------------------------------

    cursor.execute("""
        SELECT

            notices.*,

            issued_department.name
            AS issued_department_name,

            target_department.name
            AS target_department_name

        FROM notices


        LEFT JOIN departments
            AS issued_department

        ON notices.issued_department_id =
           issued_department.department_id


        LEFT JOIN departments
            AS target_department

        ON notices.target_department_id =
           target_department.department_id


        WHERE
            (
                notices.target_year IS NULL
                OR notices.target_year = ?
            )


      ORDER BY
    notices.is_pinned DESC,
    notices.created_at DESC
    """, (
        student["year"],
    ))


    possible_notices = cursor.fetchall()

    connection.close()


    # --------------------------------------------------------
    # DEPARTMENT FILTER
    # --------------------------------------------------------

    final_notices = []


    for notice in possible_notices:

        target_department = (
            notice[
                "target_department_id"
            ]
        )


        # NULL = whole college / all departments
        if target_department is None:

            final_notices.append(
                notice
            )

            continue


        # Student studies a subject from this department
        if target_department in department_ids:

            final_notices.append(
                notice
            )


    return final_notices[:10]

# ============================================================
# UPDATE NOTICE
# ============================================================

def update_notice(
    notice_id,
    title,
    message,
    category,
    target_department_id,
    target_year,
    image,
    is_pinned,
    role,
    department_id=None
):

    connection = connect_database()
    cursor = connection.cursor()


    # ========================================================
    # SUPER ADMIN
    # ========================================================

    if role == "super_admin":

        if image:

            cursor.execute("""
                UPDATE notices

                SET
                    title = ?,
                    message = ?,
                    category = ?,
                    target_department_id = ?,
                    target_year = ?,
                    image = ?,
                    is_pinned = ?

                WHERE notice_id = ?
            """, (
                title,
                message,
                category,
                target_department_id,
                target_year,
                image,
                is_pinned,
                notice_id
            ))

        else:

            cursor.execute("""
                UPDATE notices

                SET
                    title = ?,
                    message = ?,
                    category = ?,
                    target_department_id = ?,
                    target_year = ?,
                    is_pinned = ?

                WHERE notice_id = ?
            """, (
                title,
                message,
                category,
                target_department_id,
                target_year,
                is_pinned,
                notice_id
            ))


    # ========================================================
    # DEPARTMENT ADMIN
    # ========================================================

    else:

        if image:

            cursor.execute("""
                UPDATE notices

                SET
                    title = ?,
                    message = ?,
                    category = ?,
                    target_year = ?,
                    image = ?,
                    is_pinned = ?

                WHERE notice_id = ?
                AND issued_department_id = ?
            """, (
                title,
                message,
                category,
                target_year,
                image,
                is_pinned,
                notice_id,
                department_id
            ))

        else:

            cursor.execute("""
                UPDATE notices

                SET
                    title = ?,
                    message = ?,
                    category = ?,
                    target_year = ?,
                    is_pinned = ?

                WHERE notice_id = ?
                AND issued_department_id = ?
            """, (
                title,
                message,
                category,
                target_year,
                is_pinned,
                notice_id,
                department_id
            ))


    connection.commit()
    connection.close()

    # ============================================================
# SAVE / UPDATE ATTENDANCE
# ============================================================

def save_attendance(
    student_id,
    subject_id,
    month,
    present,
    total
):

    connection = connect_database()
    cursor = connection.cursor()


    # Check whether attendance already exists
    # for this student, subject and month.

    cursor.execute("""
        SELECT attendance_id

        FROM attendance

        WHERE student_id = ?
        AND subject_id = ?
        AND attendance_month = ?
    """, (
        student_id,
        subject_id,
        month
    ))

    existing_attendance = cursor.fetchone()


    # ========================================================
    # UPDATE EXISTING ATTENDANCE
    # ========================================================

    if existing_attendance:

        cursor.execute("""
            UPDATE attendance

            SET
                present_classes = ?,
                total_classes = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE attendance_id = ?
        """, (
            present,
            total,
            existing_attendance["attendance_id"]
        ))


    # ========================================================
    # CREATE NEW ATTENDANCE
    # ========================================================

    else:

        cursor.execute("""
            INSERT INTO attendance (
                student_id,
                subject_id,
                attendance_month,
                present_classes,
                total_classes
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            subject_id,
            month,
            present,
            total
        ))


    connection.commit()
    connection.close()  


    # ============================================================
# PUBLIC GENERAL NOTICES
# ============================================================

def get_public_general_notices():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            notices.*

        FROM notices

        WHERE
            LOWER(
                COALESCE(
                    notices.category,
                    'General'
                )
            ) = 'general'

        AND notices.issued_department_id IS NULL

        AND notices.target_department_id IS NULL

        AND notices.target_year IS NULL

        ORDER BY
            notices.is_pinned DESC,
            notices.created_at DESC

        LIMIT 6
    """)

    notices = cursor.fetchall()

    connection.close()

    return notices

    # ============================================================
# GET COLLEGE INFORMATION
# ============================================================

def get_college_info():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM college_info
        ORDER BY college_id ASC
        LIMIT 1
    """)

    college = cursor.fetchone()

    connection.close()

    return college


# ============================================================
# LIBRARY BOOKS
# ============================================================

def get_library_books(search_text=""):

    connection = connect_database()
    cursor = connection.cursor()

    search_pattern = (
        f"%{search_text.strip().lower()}%"
    )

    cursor.execute("""
        SELECT
            books.*,

            GROUP_CONCAT(
                DISTINCT departments.name
            ) AS recommended_departments

        FROM books

        LEFT JOIN book_recommendations
        ON books.book_id =
           book_recommendations.book_id

        LEFT JOIN departments
        ON book_recommendations.department_id =
           departments.department_id

        WHERE
            LOWER(books.title) LIKE ?
            OR LOWER(books.author) LIKE ?

        GROUP BY books.book_id

        ORDER BY
            books.title COLLATE NOCASE ASC,
            books.author COLLATE NOCASE ASC
    """, (
        search_pattern,
        search_pattern
    ))

    books = cursor.fetchall()

    connection.close()

    return books


def add_library_book(
    title,
    author,
    description,
    availability,
    added_by,
    recommended_department_id=None
):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO books (
                title,
                author,
                description,
                availability,
                added_by
            )

            VALUES (?, ?, ?, ?, ?)
        """, (
            title,
            author,
            description,
            availability,
            added_by
        ))

        book_id = cursor.lastrowid


        if recommended_department_id:

            cursor.execute("""
                INSERT OR IGNORE INTO
                book_recommendations (
                    book_id,
                    department_id,
                    recommended_by
                )

                VALUES (?, ?, ?)
            """, (
                book_id,
                recommended_department_id,
                added_by
            ))


        connection.commit()
        connection.close()

        return True, "Book added successfully."


    except sqlite3.IntegrityError:

        connection.rollback()
        connection.close()

        return (
            False,
            "A book with this title and author already exists."
        )


def recommend_library_book(
    book_id,
    department_id,
    recommended_by
):

    connection = connect_database()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT OR IGNORE INTO
            book_recommendations (
                book_id,
                department_id,
                recommended_by
            )

            VALUES (?, ?, ?)
        """, (
            book_id,
            department_id,
            recommended_by
        ))

        added = cursor.rowcount > 0

        connection.commit()
        connection.close()

        if added:
            return True, "Book recommended successfully."

        return False, "This department already recommends the book."


    except sqlite3.IntegrityError:

        connection.rollback()
        connection.close()

        return False, "The book or department was not found."


def remove_library_recommendation(
    book_id,
    department_id
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM book_recommendations

        WHERE book_id = ?
        AND department_id = ?
    """, (
        book_id,
        department_id
    ))

    removed = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return removed


def delete_library_book(book_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM books
        WHERE book_id = ?
    """, (
        book_id,
    ))

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


# ============================================================
# ANONYMOUS STUDENT COMPLAINTS
# ============================================================

def create_anonymous_complaint(
    subject,
    category,
    complaint_text
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO anonymous_complaints (
            subject,
            category,
            complaint_text
        )

        VALUES (?, ?, ?)
    """, (
        subject,
        category,
        complaint_text
    ))

    complaint_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return complaint_id


def get_anonymous_complaints(status_filter=""):

    connection = connect_database()
    cursor = connection.cursor()

    if status_filter:

        cursor.execute("""
            SELECT *
            FROM anonymous_complaints
            WHERE status = ?
            ORDER BY
                CASE status
                    WHEN 'New' THEN 1
                    WHEN 'Reviewing' THEN 2
                    WHEN 'Resolved' THEN 3
                    ELSE 4
                END,
                created_at DESC,
                complaint_id DESC
        """, (
            status_filter,
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM anonymous_complaints
            ORDER BY
                CASE status
                    WHEN 'New' THEN 1
                    WHEN 'Reviewing' THEN 2
                    WHEN 'Resolved' THEN 3
                    ELSE 4
                END,
                created_at DESC,
                complaint_id DESC
        """)

    complaints = cursor.fetchall()

    connection.close()

    return complaints


def update_anonymous_complaint(
    complaint_id,
    status,
    admin_note
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE anonymous_complaints

        SET
            status = ?,
            admin_note = ?,
            reviewed_at = CURRENT_TIMESTAMP

        WHERE complaint_id = ?
    """, (
        status,
        admin_note,
        complaint_id
    ))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


def delete_anonymous_complaint(complaint_id):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM anonymous_complaints
        WHERE complaint_id = ?
    """, (
        complaint_id,
    ))

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted
