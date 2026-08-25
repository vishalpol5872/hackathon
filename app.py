import os
import uuid
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.utils import secure_filename

from database.database import (
    initialize_database,
    initialize_messaging_tables,

    login_student,
    login_admin,

    get_student,
    get_all_students,

    get_notices_for_student,

    get_all_departments,
    get_department,

    get_faculty_by_department,
    get_subjects_by_department,
    update_department_details,
    add_faculty,
    delete_faculty,

    get_subjects_for_student,

    save_attendance,
    get_attendance_for_month,
    get_student_attendance,

    save_result,
    get_results_for_semester,
    get_student_results,

    get_faqs_by_department,
    add_faq,
    delete_faq,
    search_faqs,

    get_or_create_conversation,
    get_conversation,
    add_message,
    get_conversation_messages,
    get_student_conversations,
    get_department_conversations,
    mark_messages_read,
    get_students_for_department,

    get_all_combinations,
    save_timetable,
    get_timetable,

    get_student_timetable_for_day,

    create_student,
    update_student,
    reset_student_password,
    delete_student,
    search_students,

    create_notice,
    get_notices_for_admin,
    delete_notice,
    get_notice,
    update_notice,
    get_public_general_notices,
    get_college_info,
    get_filtered_notices_for_student,

    get_library_books,
    add_library_book,
    recommend_library_book,
    remove_library_recommendation,
    delete_library_book,

    create_anonymous_complaint,
    get_anonymous_complaints,
    update_anonymous_complaint,
    delete_anonymous_complaint
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# ============================================================
# WEBSITE BRANDING
# ============================================================

app.config["APP_NAME"] = "Student Assistant"


@app.context_processor
def inject_app_name():
    return {
        "app_name": app.config["APP_NAME"]
    }

app.secret_key = "bsc-app-secret-key"


# ============================================================
# IMAGE UPLOAD SETTINGS
# ============================================================

# Maximum uploaded file size = 15 MB

app.config["MAX_CONTENT_LENGTH"] = (
    15 * 1024 * 1024
)


MESSAGE_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "messages"
)


os.makedirs(
    MESSAGE_UPLOAD_FOLDER,
    exist_ok=True
)


ALLOWED_MESSAGE_IMAGES = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

# ============================================================
# NOTICE IMAGE UPLOADS
# ============================================================

NOTICE_UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "notices"
)

os.makedirs(
    NOTICE_UPLOAD_FOLDER,
    exist_ok=True
)

ALLOWED_NOTICE_IMAGES = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def save_notice_image(file):

    if not file or not file.filename:
        return None

    if "." not in file.filename:
        return None

    extension = (
        file.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in ALLOWED_NOTICE_IMAGES:
        return None

    filename = (
        uuid.uuid4().hex
        + "."
        + extension
    )

    file.save(
        os.path.join(
            NOTICE_UPLOAD_FOLDER,
            filename
        )
    )

    return filename


# ============================================================
# CHECK IMAGE TYPE
# ============================================================

def allowed_message_image(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return (
        extension
        in ALLOWED_MESSAGE_IMAGES
    )


# ============================================================
# SAVE MESSAGE IMAGE
# ============================================================

def save_message_image(file):

    if file is None:
        return None

    if not file.filename:
        return None


    original_filename = secure_filename(
        file.filename
    )


    if not allowed_message_image(
        original_filename
    ):
        return None


    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()


    # Generate a unique filename

    new_filename = (
        uuid.uuid4().hex
        + "."
        + extension
    )


    save_path = os.path.join(
        MESSAGE_UPLOAD_FOLDER,
        new_filename
    )


    file.save(
        save_path
    )


    return new_filename


# ============================================================
# CHAT TIME FORMAT
# ============================================================

@app.template_filter("chat_time")
def chat_time(value):

    if not value:
        return ""

    try:

        message_time = datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S"
        )

        return message_time.strftime(
            "%d %b • %I:%M %p"
        )

    except (
        ValueError,
        TypeError
    ):

        return value


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()

initialize_messaging_tables()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    general_notices = (
        get_public_general_notices()
    )

    college = get_college_info()

    return render_template(
        "index.html",

        general_notices=general_notices,

        college=college
    )

# ============================================================
# COLLEGE DETAILS
# ============================================================

@app.route("/college-details")
def college_details():

    return render_template(
        "college_details.html"
    )

# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    error = None


    if request.method == "POST":

        user_type = request.form.get(
            "user_type"
        )


        user_id = request.form.get(
            "user_id",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        )


        # ====================================================
        # STUDENT LOGIN
        # ====================================================

        if user_type == "student":

            student = login_student(
                user_id,
                password
            )


            if student:

                session.clear()

                session["user_type"] = (
                    "student"
                )

                session["student_id"] = (
                    student[
                        "student_id"
                    ]
                )

                session["name"] = (
                    student["name"]
                )

                session["year"] = (
                    student["year"]
                )

                session["combination"] = (
                    student[
                        "combination_name"
                    ]
                )


                return redirect(
                    url_for(
                        "student_dashboard"
                    )
                )


            error = (
                "Invalid Student ID "
                "or password."
            )


        # ====================================================
        # ADMIN LOGIN
        # ====================================================

        elif user_type == "admin":

            admin = login_admin(
                user_id,
                password
            )


            if admin:

                session.clear()

                session["user_type"] = (
                    "admin"
                )

                session["admin_id"] = (
                    admin["admin_id"]
                )

                session["name"] = (
                    admin["name"]
                )

                session["role"] = (
                    admin["role"]
                )

                session["department_id"] = (
                    admin[
                        "department_id"
                    ]
                )

                session["department_name"] = (
                    admin[
                        "department_name"
                    ]
                )


                return redirect(
                    url_for(
                        "admin_dashboard"
                    )
                )


            error = (
                "Invalid Admin ID "
                "or password."
            )


        else:

            error = (
                "Please choose Student "
                "or Admin login."
            )


    return render_template(
        "login.html",
        error=error
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/student/dashboard")
def student_dashboard():

    if session.get("user_type") != "student":

        return redirect(
            url_for("login")
        )


    student_id = session.get(
        "student_id"
    )


    if not student_id:

        session.clear()

        return redirect(
            url_for("login")
        )


    # ========================================================
    # LOAD STUDENT
    # ========================================================

    student = get_student(
        student_id
    )


    if student is None:

        session.clear()

        return redirect(
            url_for("login")
        )


    # ========================================================
    # NOTICES
    # ========================================================

    notices = get_filtered_notices_for_student(
        student_id
    )


    # ========================================================
    # UNREAD DEPARTMENT MESSAGES
    # ========================================================

    unread_messages = 0


    conversations = (
        get_student_conversations(
            student_id
        )
    )


    for conversation in conversations:

        unread_messages += (
            conversation["unread_count"]
            or 0
        )


    # ========================================================
    # TODAY'S TIMETABLE
    # ========================================================

    today_name = datetime.now().strftime(
        "%A"
    )


    today_timetable = (
        get_student_timetable_for_day(
            student_id,
            today_name
        )
    )


    # ========================================================
    # LOAD DASHBOARD
    # ========================================================

    return render_template(
        "student_dashboard.html",

        student=student,

        notices=notices,

        unread_messages=unread_messages,

        today_name=today_name,

        today_timetable=today_timetable
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    if (
        session.get("role") == "department_admin"
        and session.get("department_name") == "Library"
    ):

        return redirect(
            url_for("library_dashboard")
        )


    # ========================================================
    # UNREAD DEPARTMENT MESSAGES
    # ========================================================

    unread_messages = 0

    role = session.get(
        "role"
    )

    department_id = session.get(
        "department_id"
    )


    if (
        role == "department_admin"
        and department_id
    ):

        conversations = (
            get_department_conversations(
                department_id
            )
        )


        unread_messages = sum(

            conversation["unread_count"] or 0

            for conversation
            in conversations

        )


    # ========================================================
    # LOAD DASHBOARD
    # ========================================================

    return render_template(
        "admin_dashboard.html",

        name=session.get(
            "name"
        ),

        admin_id=session.get(
            "admin_id"
        ),

        role=role,

        department_name=session.get(
            "department_name"
        ),

        unread_messages=(
            unread_messages
        )
    )


# ============================================================
# LIBRARY ADMIN DASHBOARD
# ============================================================

@app.route("/library/dashboard")
def library_dashboard():

    if (
        session.get("user_type") != "admin"
        or session.get("role") != "department_admin"
        or session.get("department_name") != "Library"
    ):

        return redirect(
            url_for("admin_dashboard")
        )


    return render_template(
        "library_dashboard.html",
        name=session.get("name"),
        admin_id=session.get("admin_id")
    )

# ============================================================
# PUBLIC DEPARTMENTS
# ============================================================

@app.route(
    "/departments"
)
def departments():

    department_list = (
        get_all_departments()
    )


    return render_template(
        "departments.html",
        departments=department_list
    )


# ============================================================
# PUBLIC DEPARTMENT DETAILS
# ============================================================

@app.route(
    "/departments/<int:department_id>"
)
def department_details(
    department_id
):

    department = get_department(
        department_id
    )


    if department is None:

        return (
            "Department not found",
            404
        )


    faculty = (
        get_faculty_by_department(
            department_id
        )
    )


    subjects = (
        get_subjects_by_department(
            department_id
        )
    )


    return render_template(
        "department_details.html",
        department=department,
        faculty=faculty,
        subjects=subjects
    )


# ============================================================
# ADMIN - ATTENDANCE
# ============================================================

@app.route(
    "/admin/attendance",
    methods=[
        "GET",
        "POST"
    ]
)
def manage_attendance():

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    students = get_all_students()


    selected_student_id = (
        request.args.get(
            "student_id",
            ""
        )
    )


    selected_month = (
        request.args.get(
            "month",
            ""
        )
    )


    subjects = []

    existing_attendance = {}


    # ========================================================
    # SAVE
    # ========================================================

    if request.method == "POST":

        student_id = (
            request.form.get(
                "student_id",
                ""
            ).strip()
        )


        month = (
            request.form.get(
                "month",
                ""
            ).strip()
        )


        if (
            not student_id
            or not month
        ):

            return redirect(
                url_for(
                    "manage_attendance"
                )
            )


        subjects = (
            get_subjects_for_student(
                student_id
            )
        )


        for subject in subjects:

            subject_id = (
                subject[
                    "subject_id"
                ]
            )


            present = (
                request.form.get(
                    f"present_{subject_id}"
                )
            )


            total = (
                request.form.get(
                    f"total_{subject_id}"
                )
            )


            if (
                present is not None
                and present != ""
                and total is not None
                and total != ""
            ):

                try:

                    present = int(
                        present
                    )

                    total = int(
                        total
                    )

                except ValueError:

                    continue


                if (
                    present >= 0
                    and total >= 0
                    and present <= total
                ):

                    save_attendance(
                        student_id,
                        subject_id,
                        month,
                        present,
                        total
                    )


        return redirect(
            url_for(
                "manage_attendance",
                student_id=student_id,
                month=month
            )
        )


    # ========================================================
    # LOAD SUBJECTS
    # ========================================================

    if selected_student_id:

        subjects = (
            get_subjects_for_student(
                selected_student_id
            )
        )


    # ========================================================
    # LOAD ATTENDANCE
    # ========================================================

    if (
        selected_student_id
        and selected_month
    ):

        records = (
            get_attendance_for_month(
                selected_student_id,
                selected_month
            )
        )


        for record in records:

            existing_attendance[
                record[
                    "subject_id"
                ]
            ] = record


    return render_template(
        "manage_attendance.html",

        students=students,

        subjects=subjects,

        selected_student_id=(
            selected_student_id
        ),

        selected_month=(
            selected_month
        ),

        existing_attendance=(
            existing_attendance
        )
    )


# ============================================================
# STUDENT ATTENDANCE
# ============================================================

@app.route(
    "/student/attendance"
)
def student_attendance():

    if (
        session.get("user_type")
        != "student"
    ):

        return redirect(
            url_for("login")
        )


    student_id = (
        session.get(
            "student_id"
        )
    )


    records = (
        get_student_attendance(
            student_id
        )
    )


    # ========================================================
    # MONTHLY DATA
    # ========================================================

    monthly_data = {}


    for record in records:

        month = record[
            "attendance_month"
        ]


        if not month:
            continue


        if month not in monthly_data:

            monthly_data[
                month
            ] = {
                "present": 0,
                "total": 0
            }


        monthly_data[
            month
        ]["present"] += (
            record[
                "present_classes"
            ]
        )


        monthly_data[
            month
        ]["total"] += (
            record[
                "total_classes"
            ]
        )


    graph_months = []

    graph_percentages = []


    for month in sorted(
        monthly_data.keys()
    ):

        data = monthly_data[
            month
        ]


        graph_months.append(
            month
        )


        if data["total"] > 0:

            percentage = (
                data["present"]
                /
                data["total"]
            ) * 100

        else:

            percentage = 0


        graph_percentages.append(
            round(
                percentage,
                1
            )
        )


    # ========================================================
    # LATEST MONTH
    # ========================================================

    valid_months = [

        record[
            "attendance_month"
        ]

        for record in records

        if record[
            "attendance_month"
        ]

    ]


    latest_month = None

    latest_records = []


    if valid_months:

        latest_month = max(
            valid_months
        )


        latest_records = [

            record

            for record in records

            if (
                record[
                    "attendance_month"
                ]
                == latest_month
            )

        ]


    # ========================================================
    # OVERALL
    # ========================================================

    total_present = sum(

        record[
            "present_classes"
        ]

        for record in records

    )


    total_classes = sum(

        record[
            "total_classes"
        ]

        for record in records

    )


    if total_classes > 0:

        overall_percentage = round(
            (
                total_present
                /
                total_classes
            )
            * 100,
            1
        )

    else:

        overall_percentage = 0


    return render_template(
        "student_attendance.html",

        records=records,

        latest_month=latest_month,

        latest_records=latest_records,

        overall_percentage=(
            overall_percentage
        ),

        graph_months=(
            graph_months
        ),

        graph_percentages=(
            graph_percentages
        )
    )


# ============================================================
# ADMIN - RESULTS
# ============================================================

@app.route(
    "/admin/results",
    methods=[
        "GET",
        "POST"
    ]
)
def manage_results():

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    students = get_all_students()


    selected_student_id = (
        request.args.get(
            "student_id",
            ""
        )
    )


    selected_semester = (
        request.args.get(
            "semester",
            ""
        )
    )


    academic_year = (
        request.args.get(
            "academic_year",
            ""
        )
    )


    subjects = []

    existing_results = {}


    # ========================================================
    # SAVE RESULTS
    # ========================================================

    if request.method == "POST":

        student_id = (
            request.form.get(
                "student_id",
                ""
            ).strip()
        )


        semester_value = (
            request.form.get(
                "semester",
                ""
            )
        )


        academic_year = (
            request.form.get(
                "academic_year",
                ""
            ).strip()
        )


        if (
            not student_id
            or not semester_value
            or not academic_year
        ):

            return redirect(
                url_for(
                    "manage_results"
                )
            )


        try:

            semester = int(
                semester_value
            )

        except ValueError:

            return redirect(
                url_for(
                    "manage_results"
                )
            )


        subjects = (
            get_subjects_for_student(
                student_id
            )
        )


        for subject in subjects:

            subject_id = (
                subject[
                    "subject_id"
                ]
            )


            marks = (
                request.form.get(
                    f"marks_{subject_id}"
                )
            )


            max_marks = (
                request.form.get(
                    f"max_{subject_id}"
                )
            )


            grade = (
                request.form.get(
                    f"grade_{subject_id}",
                    ""
                ).strip()
            )


            status = (
                request.form.get(
                    f"status_{subject_id}",
                    ""
                ).strip()
            )


            if (
                marks is not None
                and marks != ""
                and max_marks is not None
                and max_marks != ""
            ):

                try:

                    marks = float(
                        marks
                    )

                    max_marks = float(
                        max_marks
                    )

                except ValueError:

                    continue


                if (
                    marks >= 0
                    and max_marks > 0
                    and marks <= max_marks
                ):

                    save_result(
                        student_id,
                        subject_id,
                        semester,
                        academic_year,
                        marks,
                        max_marks,
                        grade,
                        status
                    )


        return redirect(
            url_for(
                "manage_results",
                student_id=student_id,
                semester=semester,
                academic_year=academic_year
            )
        )


    if selected_student_id:

        subjects = (
            get_subjects_for_student(
                selected_student_id
            )
        )


    if (
        selected_student_id
        and selected_semester
        and academic_year
    ):

        try:

            semester_number = int(
                selected_semester
            )


            records = (
                get_results_for_semester(
                    selected_student_id,
                    semester_number,
                    academic_year
                )
            )


            for record in records:

                existing_results[
                    record[
                        "subject_id"
                    ]
                ] = record


        except ValueError:

            pass


    return render_template(
        "manage_results.html",

        students=students,

        subjects=subjects,

        selected_student_id=(
            selected_student_id
        ),

        selected_semester=(
            selected_semester
        ),

        academic_year=(
            academic_year
        ),

        existing_results=(
            existing_results
        )
    )


# ============================================================
# STUDENT RESULTS
# ============================================================

@app.route(
    "/student/results"
)
def student_results():

    if (
        session.get("user_type")
        != "student"
    ):

        return redirect(
            url_for("login")
        )


    student_id = (
        session.get(
            "student_id"
        )
    )


    records = (
        get_student_results(
            student_id
        )
    )


    grouped_results = {}


    for record in records:

        key = (
            record[
                "academic_year"
            ],
            record[
                "semester"
            ]
        )


        if key not in grouped_results:

            grouped_results[key] = {
                "records": [],
                "marks": 0,
                "maximum": 0,
                "percentage": 0
            }


        grouped_results[
            key
        ]["records"].append(
            record
        )


        grouped_results[
            key
        ]["marks"] += (
            record["marks"]
            or 0
        )


        grouped_results[
            key
        ]["maximum"] += (
            record["max_marks"]
            or 0
        )


    for data in (
        grouped_results.values()
    ):

        if data["maximum"] > 0:

            data["percentage"] = round(
                (
                    data["marks"]
                    /
                    data["maximum"]
                )
                * 100,
                2
            )


    return render_template(
        "student_results.html",
        grouped_results=(
            grouped_results
        )
    )


# ============================================================
# DEPARTMENT ADMIN - MANAGE DEPARTMENT
# ============================================================

@app.route(
    "/admin/department",
    methods=[
        "GET",
        "POST"
    ]
)
def manage_department():

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    if (
        session.get("role")
        != "department_admin"
    ):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    department_id = (
        session.get(
            "department_id"
        )
    )


    if not department_id:

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    if request.method == "POST":

        action = request.form.get(
            "action"
        )


        # ====================================================
        # UPDATE DEPARTMENT
        # ====================================================

        if action == "update_department":

            description = (
                request.form.get(
                    "description",
                    ""
                ).strip()
            )


            hod_name = (
                request.form.get(
                    "hod_name",
                    ""
                ).strip()
            )


            hod_email = (
                request.form.get(
                    "hod_email",
                    ""
                ).strip()
            )


            hod_phone = (
                request.form.get(
                    "hod_phone",
                    ""
                ).strip()
            )


            department_location = (
                request.form.get(
                    "department_location",
                    ""
                ).strip()
            )


            update_department_details(
                department_id,
                description,
                hod_name,
                hod_email,
                hod_phone,
                department_location
            )


        # ====================================================
        # ADD FACULTY
        # ====================================================

        elif action == "add_faculty":

            name = (
                request.form.get(
                    "name",
                    ""
                ).strip()
            )


            designation = (
                request.form.get(
                    "designation",
                    ""
                ).strip()
            )


            qualification = (
                request.form.get(
                    "qualification",
                    ""
                ).strip()
            )


            email = (
                request.form.get(
                    "email",
                    ""
                ).strip()
            )


            phone = (
                request.form.get(
                    "phone",
                    ""
                ).strip()
            )


            office_location = (
                request.form.get(
                    "office_location",
                    ""
                ).strip()
            )


            if name:

                add_faculty(
                    name,
                    designation,
                    qualification,
                    email,
                    phone,
                    office_location,
                    department_id
                )


        # ====================================================
        # DELETE FACULTY
        # ====================================================

        elif action == "delete_faculty":

            faculty_id = (
                request.form.get(
                    "faculty_id"
                )
            )


            if faculty_id:

                try:

                    delete_faculty(
                        int(faculty_id)
                    )

                except ValueError:

                    pass


        return redirect(
            url_for(
                "manage_department"
            )
        )


    department = get_department(
        department_id
    )


    faculty = (
        get_faculty_by_department(
            department_id
        )
    )


    subjects = (
        get_subjects_by_department(
            department_id
        )
    )


    return render_template(
        "manage_department.html",
        department=department,
        faculty=faculty,
        subjects=subjects
    )


# ============================================================
# DEPARTMENT ADMIN - FAQS
# ============================================================

@app.route(
    "/admin/faqs",
    methods=[
        "GET",
        "POST"
    ]
)
def manage_faqs():

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    if (
        session.get("role")
        != "department_admin"
    ):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    department_id = (
        session.get(
            "department_id"
        )
    )


    admin_id = session.get(
        "admin_id"
    )


    if not department_id:

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    if request.method == "POST":

        action = request.form.get(
            "action"
        )


        # ====================================================
        # ADD FAQ
        # ====================================================

        if action == "add_faq":

            question = (
                request.form.get(
                    "question",
                    ""
                ).strip()
            )


            answer = (
                request.form.get(
                    "answer",
                    ""
                ).strip()
            )


            subject_value = (
                request.form.get(
                    "subject_id",
                    ""
                )
            )


            subject_id = None


            if subject_value:

                try:

                    requested_subject_id = int(
                        subject_value
                    )


                    department_subjects = (
                        get_subjects_by_department(
                            department_id
                        )
                    )


                    valid_subject_ids = {

                        subject[
                            "subject_id"
                        ]

                        for subject
                        in department_subjects

                    }


                    if (
                        requested_subject_id
                        in valid_subject_ids
                    ):

                        subject_id = (
                            requested_subject_id
                        )


                except ValueError:

                    subject_id = None


            if question and answer:

                add_faq(
                    question,
                    answer,
                    department_id,
                    subject_id,
                    admin_id
                )


        # ====================================================
        # DELETE FAQ
        # ====================================================

        elif action == "delete_faq":

            faq_id = (
                request.form.get(
                    "faq_id"
                )
            )


            if faq_id:

                try:

                    delete_faq(
                        int(faq_id),
                        department_id
                    )

                except ValueError:

                    pass


        return redirect(
            url_for(
                "manage_faqs"
            )
        )


    department = get_department(
        department_id
    )


    subjects = (
        get_subjects_by_department(
            department_id
        )
    )


    faqs = (
        get_faqs_by_department(
            department_id
        )
    )


    return render_template(
        "manage_faqs.html",
        department=department,
        subjects=subjects,
        faqs=faqs
    )


# ============================================================
# MANAGE NOTICES
# ============================================================

@app.route(
    "/admin/notices",
    methods=["GET", "POST"]
)
def manage_notices():

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    role = session.get("role")

    department_id = session.get(
        "department_id"
    )

    department_name = session.get(
        "department_name"
    )

    admin_id = session.get(
        "admin_id"
    )


    categories = [
        "General",
        "Academic",
        "Exam",
        "Event",
        "Urgent",
        "Scholarship",
        "Library"
    ]


    # ========================================================
    # CREATE NOTICE
    # ========================================================

    if request.method == "POST":

        title = (
            request.form
            .get("title", "")
            .strip()
        )

        message = (
            request.form
            .get("message", "")
            .strip()
        )

        category = (
            request.form
            .get("category", "General")
            .strip()
        )


        if category not in categories:
            category = "General"


        # ----------------------------------------------------
        # TARGET YEAR
        # ----------------------------------------------------

        target_year_value = (
            request.form
            .get("target_year", "")
            .strip()
        )


        if target_year_value in {
            "1",
            "2",
            "3"
        }:

            target_year = int(
                target_year_value
            )

        else:

            target_year = None


        # ----------------------------------------------------
        # DEPARTMENT RULES
        # ----------------------------------------------------

        if role == "department_admin":

            # Notice automatically comes from
            # the logged-in department.

            issued_department_id = (
                department_id
            )

            # Library announcements are useful to every
            # student, so they target all departments.

            if department_name == "Library":

                target_department_id = None

            else:

                target_department_id = (
                    department_id
                )


        else:

            # Super admin = College Administration

            issued_department_id = None


            target_department_value = (
                request.form
                .get(
                    "target_department_id",
                    ""
                )
                .strip()
            )


            if target_department_value.isdigit():

                target_department_id = int(
                    target_department_value
                )

            else:

                # NULL means all departments

                target_department_id = None


        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_file = request.files.get(
            "image"
        )


        image_filename = (
            save_notice_image(
                image_file
            )
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not title or not message:

            flash(
                "Title and message are required."
            )

            return redirect(
                url_for(
                    "manage_notices"
                )
            )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        create_notice(
            title=title,
            message=message,
            category=category,
            image=image_filename,
            issued_department_id=issued_department_id,
            target_department_id=target_department_id,
            target_year=target_year,
            created_by=admin_id
        )


        flash(
            "Notice published successfully."
        )


        return redirect(
            url_for(
                "manage_notices"
            )
        )


    # ========================================================
    # GET EXISTING NOTICES
    # ========================================================

    departments = get_all_departments()


    notices = get_notices_for_admin(
        role,
        department_id
    )


    return render_template(
        "manage_notices.html",

        notices=notices,

        departments=departments,

        categories=categories,

        role=role,

        department_id=department_id,

        department_name=department_name
    )

# ============================================================
# DELETE NOTICE
# ============================================================

@app.route(
    "/admin/notices/delete/<int:notice_id>",
    methods=["POST"]
)
def delete_admin_notice(
    notice_id
):

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    role = session.get("role")

    department_id = session.get(
        "department_id"
    )


    notice = get_notice(
        notice_id
    )


    if notice is None:

        return redirect(
            url_for(
                "manage_notices"
            )
        )


    # ========================================================
    # SECURITY CHECK
    # ========================================================

    if role == "department_admin":

        if (
            notice["issued_department_id"]
            != department_id
        ):

            return redirect(
                url_for(
                    "manage_notices"
                )
            )


    # ========================================================
    # DELETE IMAGE
    # ========================================================

    image_filename = notice["image"]


    delete_notice(
        notice_id,
        role,
        department_id
    )


    if image_filename:

        image_path = os.path.join(
            NOTICE_UPLOAD_FOLDER,
            image_filename
        )


        if os.path.exists(
            image_path
        ):

            os.remove(
                image_path
            )


    flash(
        "Notice deleted."
    )


    return redirect(
        url_for(
            "manage_notices"
        )
    )


# ============================================================
# EDIT NOTICE
# ============================================================

@app.route(
    "/admin/notices/edit/<int:notice_id>",
    methods=["GET", "POST"]
)
def edit_notice(
    notice_id
):

    if session.get("user_type") != "admin":
        return redirect(url_for("login"))


    role = session.get("role")
    department_id = session.get("department_id")
    department_name = session.get("department_name")

    notice = get_notice(notice_id)


    # Notice does not exist
    if notice is None:
        return redirect(url_for("manage_notices"))


    # ========================================================
    # SECURITY
    # ========================================================

    if role == "department_admin":

        if notice["issued_department_id"] != department_id:

            return redirect(
                url_for("manage_notices")
            )


    categories = [
        "General",
        "Academic",
        "Exam",
        "Event",
        "Urgent",
        "Scholarship",
        "Library"
    ]


    departments = get_all_departments()


    # ========================================================
    # SAVE CHANGES
    # ========================================================

    if request.method == "POST":

        title = (
            request.form
            .get("title", "")
            .strip()
        )

        message = (
            request.form
            .get("message", "")
            .strip()
        )

        category = (
            request.form
            .get("category", "General")
            .strip()
        )


        if category not in categories:
            category = "General"


        # ----------------------------------------------------
        # TARGET YEAR
        # ----------------------------------------------------

        target_year_value = (
            request.form
            .get("target_year", "")
            .strip()
        )


        if target_year_value in {
            "1",
            "2",
            "3"
        }:

            target_year = int(
                target_year_value
            )

        else:

            target_year = None


        # ----------------------------------------------------
        # TARGET DEPARTMENT
        # ----------------------------------------------------

        if role == "department_admin":

            if department_name == "Library":

                target_department_id = None

            else:

                target_department_id = department_id

        else:

            target_department_value = (
                request.form
                .get("target_department_id", "")
                .strip()
            )

            if target_department_value.isdigit():

                target_department_id = int(
                    target_department_value
                )

            else:

                target_department_id = None


        # ----------------------------------------------------
        # PIN NOTICE
        # ----------------------------------------------------

        is_pinned = 1 if request.form.get("is_pinned") else 0


        # ----------------------------------------------------
        # NEW IMAGE
        # ----------------------------------------------------

        image_file = request.files.get("image")

        new_image = None


        if image_file and image_file.filename:

            new_image = save_notice_image(
                image_file
            )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not title or not message:

            flash(
                "Title and message are required."
            )

            return redirect(
                url_for(
                    "edit_notice",
                    notice_id=notice_id
                )
            )


        old_image = notice["image"]


        # ----------------------------------------------------
        # UPDATE DATABASE
        # ----------------------------------------------------

        update_notice(
            notice_id=notice_id,
            title=title,
            message=message,
            category=category,
            target_department_id=target_department_id,
            target_year=target_year,
            image=new_image,
            is_pinned=is_pinned,
            role=role,
            department_id=department_id
        )


        # ----------------------------------------------------
        # DELETE OLD IMAGE IF REPLACED
        # ----------------------------------------------------

        if new_image and old_image:

            old_image_path = os.path.join(
                NOTICE_UPLOAD_FOLDER,
                old_image
            )

            if os.path.exists(old_image_path):

                os.remove(old_image_path)


        flash(
            "Notice updated successfully."
        )


        return redirect(
            url_for("manage_notices")
        )


    # ========================================================
    # SHOW EDIT PAGE
    # ========================================================

    return render_template(
        "edit_notice.html",

        notice=notice,

        categories=categories,

        departments=departments,

        role=role,

        department_id=department_id,

        department_name=session.get(
            "department_name"
        )
    )


# ============================================================
# FREE OPENROUTER AI
# ============================================================

def ask_ai(question, chat_history=None):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful college student assistant. "
                    "Answer clearly and simply. Do not invent "
                    "college-specific facts."
                )
            }
        ]

        if chat_history:
            for message in chat_history[-6:]:
                role = message.get("role")
                content = message.get("text", "")
                if role in ("user", "assistant") and content:
                    messages.append({
                        "role": role,
                        "content": content
                    })

        messages.append({
            "role": "user",
            "content": question
        })

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI Error:", e)
        return None


@app.route(
    "/student/assistant",
    methods=[
        "GET",
        "POST"
    ]
)
def student_assistant():

    if (
        session.get("user_type")
        != "student"
    ):

        return redirect(
            url_for("login")
        )

    chat_history = session.get(
        "assistant_chat",
        []
    )

    if request.method == "POST":

        action = request.form.get(
            "action",
            "ask"
        )

        if action == "clear_chat":

            session[
                "assistant_chat"
            ] = []

            session.modified = True

            return redirect(
                url_for(
                    "student_assistant"
                )
            )

        question = (
            request.form.get(
                "question",
                ""
            )
            .strip()
        )

        if question:

            chat_history.append({
                "role": "user",
                "text": question
            })

            answers = search_faqs(
                question
            )

            if answers:

                best_answer = (
                    answers[0]
                )

                department_name = (
                    best_answer[
                        "department_name"
                    ]
                    or ""
                )

                subject_name = (
                    best_answer[
                        "subject_name"
                    ]
                    or ""
                )

                source = (
                    department_name
                )

                if subject_name:

                    if source:
                        source += " • "

                    source += subject_name

                chat_history.append({
                    "role": "assistant",
                    "text": (
                        best_answer[
                            "answer"
                        ]
                    ),
                    "source": source
                })

            else:

                ai_answer = ask_ai(
                    question,
                    chat_history
                )

                chat_history.append({
                    "role": "assistant",
                    "text": (
                        ai_answer
                        or
                        "I couldn't find a verified answer "
                        "for that question in the college "
                        "knowledge base. Try asking it in "
                        "another way, or contact the relevant "
                        "department through Department Chat."
                    ),
                    "source": (
                        "OpenRouter AI"
                        if ai_answer
                        else
                        "Student Assistant"
                    )
                })

            chat_history = (
                chat_history[-12:]
            )

            session[
                "assistant_chat"
            ] = chat_history

            session.modified = True

            return redirect(
                url_for(
                    "student_assistant"
                )
            )

    return render_template(
        "student_assistant.html",
        chat_history=chat_history
    )


# ============================================================
# STUDENT - DEPARTMENT MESSAGES
# ============================================================

@app.route(
    "/student/messages",
    methods=[
        "GET",
        "POST"
    ]
)
def student_messages():

    if (
        session.get("user_type")
        != "student"
    ):

        return redirect(
            url_for("login")
        )


    student_id = (
        session.get(
            "student_id"
        )
    )


    department_list = (
        get_all_departments()
    )


    # ========================================================
    # START CHAT
    # ========================================================

    if request.method == "POST":

        department_value = (
            request.form.get(
                "department_id",
                ""
            )
        )


        try:

            department_id = int(
                department_value
            )

        except (
            ValueError,
            TypeError
        ):

            return redirect(
                url_for(
                    "student_messages"
                )
            )


        department = (
            get_department(
                department_id
            )
        )


        if department is None:

            return redirect(
                url_for(
                    "student_messages"
                )
            )


        conversation = (
            get_or_create_conversation(
                student_id,
                department_id
            )
        )


        return redirect(
            url_for(
                "student_chat",

                conversation_id=(
                    conversation[
                        "conversation_id"
                    ]
                )
            )
        )


    conversations = (
        get_student_conversations(
            student_id
        )
    )


    return render_template(
        "student_messages.html",

        departments=(
            department_list
        ),

        conversations=(
            conversations
        )
    )


# ============================================================
# STUDENT - OPEN DEPARTMENT CHAT
# ============================================================

@app.route(
    "/student/messages/<int:conversation_id>",
    methods=[
        "GET",
        "POST"
    ]
)
def student_chat(
    conversation_id
):

    if (
        session.get("user_type")
        != "student"
    ):

        return redirect(
            url_for("login")
        )


    student_id = (
        session.get(
            "student_id"
        )
    )


    conversation = (
        get_conversation(
            conversation_id
        )
    )


    # ========================================================
    # SECURITY
    # ========================================================

    if (
        conversation is None
        or conversation[
            "student_id"
        ] != student_id
    ):

        return (
            "You do not have permission "
            "to view this conversation.",
            403
        )


    # ========================================================
    # SEND MESSAGE
    # ========================================================

    if request.method == "POST":

        message_text = (
            request.form.get(
                "message",
                ""
            ).strip()
        )


        # IMPORTANT:
        # Uploaded files are inside request.files

        image_file = (
            request.files.get(
                "image"
            )
        )


        image_name = None


        if (
            image_file is not None
            and image_file.filename
        ):

            image_name = (
                save_message_image(
                    image_file
                )
            )


        # Text, image, or both can be sent

        if (
            message_text
            or image_name
        ):

            add_message(
                conversation_id,
                "student",
                student_id,
                message_text,
                image_name
            )


        return redirect(
            url_for(
                "student_chat",
                conversation_id=(
                    conversation_id
                )
            )
        )


    # ========================================================
    # MARK DEPARTMENT MESSAGES READ
    # ========================================================

    mark_messages_read(
        conversation_id,
        "student"
    )


    messages = (
        get_conversation_messages(
            conversation_id
        )
    )


    return render_template(
        "student_chat.html",

        conversation=(
            conversation
        ),

        messages=messages
    )


# ============================================================
# DEPARTMENT ADMIN - INBOX
# ============================================================

@app.route(
    "/admin/messages",
    methods=[
        "GET",
        "POST"
    ]
)
def department_messages():

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    if (
        session.get("role")
        != "department_admin"
    ):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    department_id = (
        session.get(
            "department_id"
        )
    )


    if not department_id:

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    # ========================================================
    # DEPARTMENT STARTS CHAT
    # ========================================================

    if request.method == "POST":

        student_id = (
            request.form.get(
                "student_id",
                ""
            ).strip()
        )


        allowed_students = (
            get_students_for_department(
                department_id
            )
        )


        allowed_ids = {

            student[
                "student_id"
            ]

            for student
            in allowed_students

        }


        if (
            student_id
            not in allowed_ids
        ):

            return (
                "This student is not "
                "connected to your "
                "department.",
                403
            )


        conversation = (
            get_or_create_conversation(
                student_id,
                department_id
            )
        )


        return redirect(
            url_for(
                "department_chat",

                conversation_id=(
                    conversation[
                        "conversation_id"
                    ]
                )
            )
        )


    conversations = (
        get_department_conversations(
            department_id
        )
    )


    students = (
        get_students_for_department(
            department_id
        )
    )


    department = get_department(
        department_id
    )


    return render_template(
        "department_messages.html",

        conversations=(
            conversations
        ),

        students=students,

        department=department
    )


# ============================================================
# DEPARTMENT ADMIN - OPEN STUDENT CHAT
# ============================================================

@app.route(
    "/admin/messages/<int:conversation_id>",
    methods=[
        "GET",
        "POST"
    ]
)
def department_chat(
    conversation_id
):

    if (
        session.get("user_type")
        != "admin"
    ):

        return redirect(
            url_for("login")
        )


    if (
        session.get("role")
        != "department_admin"
    ):

        return redirect(
            url_for(
                "admin_dashboard"
            )
        )


    department_id = (
        session.get(
            "department_id"
        )
    )


    admin_id = (
        session.get(
            "admin_id"
        )
    )


    conversation = (
        get_conversation(
            conversation_id
        )
    )


    # ========================================================
    # SECURITY
    # ========================================================

    if (
        conversation is None
        or conversation[
            "department_id"
        ] != department_id
    ):

        return (
            "You do not have permission "
            "to view this conversation.",
            403
        )


    # ========================================================
    # SEND MESSAGE
    # ========================================================

    if request.method == "POST":

        message_text = (
            request.form.get(
                "message",
                ""
            ).strip()
        )


        image_file = (
            request.files.get(
                "image"
            )
        )


        image_name = None


        if (
            image_file is not None
            and image_file.filename
        ):

            image_name = (
                save_message_image(
                    image_file
                )
            )


        if (
            message_text
            or image_name
        ):

            add_message(
                conversation_id,
                "department_admin",
                admin_id,
                message_text,
                image_name
            )


        return redirect(
            url_for(
                "department_chat",
                conversation_id=(
                    conversation_id
                )
            )
        )


    # ========================================================
    # MARK STUDENT MESSAGES READ
    # ========================================================

    mark_messages_read(
        conversation_id,
        "department"
    )


    messages = (
        get_conversation_messages(
            conversation_id
        )
    )


    return render_template(
        "department_chat.html",

        conversation=(
            conversation
        ),

        messages=messages
    )

# ============================================================
# SUPER ADMIN - MANAGE STUDENTS
# ============================================================

@app.route("/admin/students")
def manage_students():

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    # Only Super Admin can manage student accounts
    if session.get("role") != "super_admin":

        return redirect(
            url_for("admin_dashboard")
        )


    search_text = request.args.get(
        "search",
        ""
    ).strip()


    students = search_students(
        search_text
    )


    return render_template(
        "manage_students.html",
        students=students,
        search_text=search_text
    )


# ============================================================
# SUPER ADMIN - ADD STUDENT
# ============================================================

@app.route(
    "/admin/students/add",
    methods=["GET", "POST"]
)
def add_student_page():

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    if session.get("role") != "super_admin":

        return redirect(
            url_for("admin_dashboard")
        )


    combinations = get_all_combinations()

    error = None


    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip().upper()


        name = request.form.get(
            "name",
            ""
        ).strip()


        email = request.form.get(
            "email",
            ""
        ).strip()


        phone = request.form.get(
            "phone",
            ""
        ).strip()


        date_of_birth = request.form.get(
            "date_of_birth",
            ""
        ).strip()


        address = request.form.get(
            "address",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        )


        year_value = request.form.get(
            "year",
            ""
        )


        combination_value = request.form.get(
            "combination_id",
            ""
        )


        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if (
            not student_id
            or not name
            or not password
            or not year_value
            or not combination_value
        ):

            error = (
                "Student ID, name, password, "
                "year and combination are required."
            )

        else:

            try:

                year = int(
                    year_value
                )

                combination_id = int(
                    combination_value
                )

            except ValueError:

                error = (
                    "Invalid year or combination."
                )

            else:

                if year not in (
                    1,
                    2,
                    3
                ):

                    error = (
                        "Year must be 1, 2 or 3."
                    )

                else:

                    success, message = (
                        create_student(
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
                    )


                    if success:

                        return redirect(
                            url_for(
                                "manage_students"
                            )
                        )


                    error = message


    return render_template(
        "add_student.html",
        combinations=combinations,
        error=error
    )


# ============================================================
# SUPER ADMIN - EDIT STUDENT
# ============================================================

@app.route(
    "/admin/students/<student_id>/edit",
    methods=["GET", "POST"]
)
def edit_student_page(
    student_id
):

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    if session.get("role") != "super_admin":

        return redirect(
            url_for("admin_dashboard")
        )


    student = get_student(
        student_id
    )


    if student is None:

        return (
            "Student not found",
            404
        )


    combinations = (
        get_all_combinations()
    )


    error = None

    success_message = None


    if request.method == "POST":

        action = request.form.get(
            "action"
        )


        # ====================================================
        # UPDATE STUDENT DETAILS
        # ====================================================

        if action == "update_student":

            name = request.form.get(
                "name",
                ""
            ).strip()


            email = request.form.get(
                "email",
                ""
            ).strip()


            phone = request.form.get(
                "phone",
                ""
            ).strip()


            date_of_birth = request.form.get(
                "date_of_birth",
                ""
            ).strip()


            address = request.form.get(
                "address",
                ""
            ).strip()


            year_value = request.form.get(
                "year",
                ""
            )


            combination_value = (
                request.form.get(
                    "combination_id",
                    ""
                )
            )


            if (
                not name
                or not year_value
                or not combination_value
            ):

                error = (
                    "Name, year and combination "
                    "are required."
                )

            else:

                try:

                    year = int(
                        year_value
                    )

                    combination_id = int(
                        combination_value
                    )

                except ValueError:

                    error = (
                        "Invalid year or combination."
                    )

                else:

                    if year not in (
                        1,
                        2,
                        3
                    ):

                        error = (
                            "Year must be 1, 2 or 3."
                        )

                    else:

                        success, message = (
                            update_student(
                                student_id,
                                name,
                                email,
                                phone,
                                date_of_birth,
                                address,
                                year,
                                combination_id
                            )
                        )


                        if success:

                            success_message = (
                                message
                            )

                            student = get_student(
                                student_id
                            )

                        else:

                            error = message


        # ====================================================
        # RESET PASSWORD
        # ====================================================

        elif action == "reset_password":

            new_password = (
                request.form.get(
                    "new_password",
                    ""
                )
            )


            if not new_password:

                error = (
                    "Enter a new password."
                )

            else:

                reset_student_password(
                    student_id,
                    new_password
                )

                success_message = (
                    "Student password was reset."
                )


    return render_template(
        "edit_student.html",
        student=student,
        combinations=combinations,
        error=error,
        success_message=success_message
    )


# ============================================================
# SUPER ADMIN - DELETE STUDENT
# ============================================================

@app.route(
    "/admin/students/<student_id>/delete",
    methods=["POST"]
)
def delete_student_route(
    student_id
):

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    if session.get("role") != "super_admin":

        return redirect(
            url_for("admin_dashboard")
        )


    delete_student(
        student_id
    )


    return redirect(
        url_for(
            "manage_students"
        )
    )


# ============================================================
# SUPER ADMIN - MANAGE TIMETABLE
# ============================================================

@app.route(
    "/admin/timetable",
    methods=["GET", "POST"]
)
def manage_timetable():

    # Only logged-in admins
    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    # Only Super Admin manages full timetable
    if session.get("role") != "super_admin":

        return redirect(
            url_for("admin_dashboard")
        )


    combinations = get_all_combinations()


    selected_combination = request.args.get(
        "combination_id",
        ""
    )


    selected_year = request.args.get(
        "year",
        ""
    )


    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]


    timetable_data = {}


    # ========================================================
    # SAVE TIMETABLE
    # ========================================================

    if request.method == "POST":

        combination_value = request.form.get(
            "combination_id",
            ""
        )


        year_value = request.form.get(
            "year",
            ""
        )


        try:

            combination_id = int(
                combination_value
            )

            year = int(
                year_value
            )

        except (
            ValueError,
            TypeError
        ):

            return redirect(
                url_for(
                    "manage_timetable"
                )
            )


        if year not in [
            1,
            2,
            3
        ]:

            return redirect(
                url_for(
                    "manage_timetable"
                )
            )


        # Save Monday - Saturday

        for day in days:

            period1 = request.form.get(
                f"{day}_period1",
                ""
            ).strip()


            period2 = request.form.get(
                f"{day}_period2",
                ""
            ).strip()


            period3 = request.form.get(
                f"{day}_period3",
                ""
            ).strip()


            period4 = request.form.get(
                f"{day}_period4",
                ""
            ).strip()


            period5 = request.form.get(
                f"{day}_period5",
                ""
            ).strip()


            save_timetable(
                combination_id,
                year,
                day,
                period1,
                period2,
                period3,
                period4,
                period5
            )


        return redirect(
            url_for(
                "manage_timetable",
                combination_id=combination_id,
                year=year
            )
        )


    # ========================================================
    # LOAD EXISTING TIMETABLE
    # ========================================================

    if (
        selected_combination
        and selected_year
    ):

        try:

            combination_id = int(
                selected_combination
            )

            year = int(
                selected_year
            )


            records = get_timetable(
                combination_id,
                year
            )


            for record in records:

                timetable_data[
                    record["day"]
                ] = record


        except (
            ValueError,
            TypeError
        ):

            pass


    # ========================================================
    # SHOW PAGE
    # ========================================================

    return render_template(
        "manage_timetable.html",

        combinations=combinations,

        selected_combination=(
            selected_combination
        ),

        selected_year=(
            selected_year
        ),

        days=days,

        timetable_data=(
            timetable_data
        )
    )


# ============================================================
# LIBRARY CATALOGUE
# ============================================================

@app.route("/library")
def student_library():

    search_text = request.args.get(
        "search",
        ""
    ).strip()

    books = get_library_books(
        search_text
    )

    return render_template(
        "student_library.html",
        books=books,
        search_text=search_text,
        user_type=session.get("user_type")
    )


# ============================================================
# ADMIN LIBRARY MANAGEMENT
# ============================================================

@app.route(
    "/admin/library",
    methods=["GET", "POST"]
)
def manage_library():

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    role = session.get("role")
    department_id = session.get("department_id")
    department_name = session.get("department_name")
    admin_id = session.get("admin_id")

    is_library_admin = (
        role == "department_admin"
        and department_name == "Library"
    )

    can_manage_books = (
        role == "super_admin"
        or is_library_admin
    )


    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )


        # ----------------------------------------------------
        # LIBRARY ADMIN / SUPER ADMIN ADDS A BOOK
        # ----------------------------------------------------

        if action == "add_book":

            if not can_manage_books:

                flash(
                    "Only the Library admin or Super Admin can add books."
                )

                return redirect(
                    url_for("manage_library")
                )


            title = request.form.get(
                "title",
                ""
            ).strip()

            author = request.form.get(
                "author",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            availability = request.form.get(
                "availability",
                "Available"
            ).strip()

            allowed_availability = {
                "Available",
                "Reference Only",
                "Unavailable"
            }

            if availability not in allowed_availability:
                availability = "Available"


            recommendation_value = request.form.get(
                "recommended_department_id",
                ""
            ).strip()

            recommended_department_id = None

            if recommendation_value.isdigit():

                recommended_department_id = int(
                    recommendation_value
                )


            if not title or not author:

                flash(
                    "Book name and author are required."
                )

            else:

                success, message = add_library_book(
                    title=title,
                    author=author,
                    description=description,
                    availability=availability,
                    added_by=admin_id,
                    recommended_department_id=(
                        recommended_department_id
                    )
                )

                flash(message)


        # ----------------------------------------------------
        # DEPARTMENT ADMIN RECOMMENDS AN EXISTING BOOK
        # ----------------------------------------------------

        elif action == "recommend_book":

            book_value = request.form.get(
                "book_id",
                ""
            ).strip()

            recommendation_department_id = None


            if role == "department_admin":

                recommendation_department_id = department_id


            elif role == "super_admin":

                selected_department = request.form.get(
                    "department_id",
                    ""
                ).strip()

                if selected_department.isdigit():

                    recommendation_department_id = int(
                        selected_department
                    )


            if (
                book_value.isdigit()
                and recommendation_department_id
            ):

                success, message = recommend_library_book(
                    book_id=int(book_value),
                    department_id=(
                        recommendation_department_id
                    ),
                    recommended_by=admin_id
                )

                flash(message)

            else:

                flash(
                    "Choose a valid book and department."
                )


        # ----------------------------------------------------
        # DEPARTMENT ADMIN REMOVES ITS RECOMMENDATION
        # ----------------------------------------------------

        elif action == "remove_recommendation":

            book_value = request.form.get(
                "book_id",
                ""
            ).strip()

            if (
                role == "department_admin"
                and department_id
                and book_value.isdigit()
            ):

                removed = remove_library_recommendation(
                    int(book_value),
                    department_id
                )

                if removed:
                    flash("Recommendation removed.")
                else:
                    flash("No recommendation was found.")


        return redirect(
            url_for("manage_library")
        )


    search_text = request.args.get(
        "search",
        ""
    ).strip()

    books = get_library_books(
        search_text
    )

    departments = get_all_departments()

    return render_template(
        "manage_library.html",
        books=books,
        departments=departments,
        search_text=search_text,
        role=role,
        department_id=department_id,
        department_name=department_name,
        is_library_admin=is_library_admin,
        can_manage_books=can_manage_books
    )


@app.route(
    "/admin/library/books/<int:book_id>/delete",
    methods=["POST"]
)
def delete_library_book_route(book_id):

    if session.get("user_type") != "admin":

        return redirect(
            url_for("login")
        )


    can_manage_books = (
        session.get("role") == "super_admin"
        or session.get("department_name") == "Library"
    )


    if not can_manage_books:

        return redirect(
            url_for("admin_dashboard")
        )


    if delete_library_book(book_id):
        flash("Book removed from the Library catalogue.")
    else:
        flash("Book not found.")


    return redirect(
        url_for("manage_library")
    )


# ============================================================
# ANONYMOUS STUDENT COMPLAINT BOX
# ============================================================

@app.route(
    "/student/complaint",
    methods=["GET", "POST"]
)
def student_complaint():

    if session.get("user_type") != "student":

        return redirect(
            url_for("login")
        )


    categories = [
        "Academic",
        "Administration",
        "Facilities",
        "Library",
        "Safety",
        "Other"
    ]


    if request.method == "POST":

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        category = request.form.get(
            "category",
            "Other"
        ).strip()

        complaint_text = request.form.get(
            "complaint_text",
            ""
        ).strip()


        if category not in categories:
            category = "Other"


        if not subject or not complaint_text:

            flash(
                "Subject and complaint details are required."
            )

        elif len(subject) > 120:

            flash(
                "The subject must be 120 characters or fewer."
            )

        elif len(complaint_text) < 10:

            flash(
                "Please provide at least 10 characters of detail."
            )

        elif len(complaint_text) > 3000:

            flash(
                "The complaint must be 3000 characters or fewer."
            )

        else:

            create_anonymous_complaint(
                subject=subject,
                category=category,
                complaint_text=complaint_text
            )

            flash(
                "Your anonymous complaint was submitted to the Super Admin."
            )

            return redirect(
                url_for("student_complaint")
            )


    return render_template(
        "student_complaint.html",
        categories=categories
    )


# ============================================================
# SUPER ADMIN COMPLAINT MANAGEMENT
# ============================================================

@app.route("/admin/complaints")
def manage_complaints():

    if (
        session.get("user_type") != "admin"
        or session.get("role") != "super_admin"
    ):

        return redirect(
            url_for("admin_dashboard")
        )


    allowed_statuses = [
        "New",
        "Reviewing",
        "Resolved",
        "Dismissed"
    ]

    status_filter = request.args.get(
        "status",
        ""
    ).strip()

    if status_filter not in allowed_statuses:
        status_filter = ""


    complaints = get_anonymous_complaints(
        status_filter
    )


    return render_template(
        "manage_complaints.html",
        complaints=complaints,
        statuses=allowed_statuses,
        status_filter=status_filter
    )


@app.route(
    "/admin/complaints/<int:complaint_id>/update",
    methods=["POST"]
)
def update_complaint_route(complaint_id):

    if (
        session.get("user_type") != "admin"
        or session.get("role") != "super_admin"
    ):

        return redirect(
            url_for("admin_dashboard")
        )


    allowed_statuses = {
        "New",
        "Reviewing",
        "Resolved",
        "Dismissed"
    }

    status = request.form.get(
        "status",
        "New"
    ).strip()

    admin_note = request.form.get(
        "admin_note",
        ""
    ).strip()


    if status not in allowed_statuses:
        status = "New"

    admin_note = admin_note[:2000]


    if update_anonymous_complaint(
        complaint_id,
        status,
        admin_note
    ):

        flash("Complaint updated.")

    else:

        flash("Complaint not found.")


    return redirect(
        url_for("manage_complaints")
    )


@app.route(
    "/admin/complaints/<int:complaint_id>/delete",
    methods=["POST"]
)
def delete_complaint_route(complaint_id):

    if (
        session.get("user_type") != "admin"
        or session.get("role") != "super_admin"
    ):

        return redirect(
            url_for("admin_dashboard")
        )


    if delete_anonymous_complaint(complaint_id):
        flash("Complaint deleted.")
    else:
        flash("Complaint not found.")


    return redirect(
        url_for("manage_complaints")
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )



# ============================================================
# STUDENT TIMETABLE
# ============================================================

@app.route(
    "/student/timetable"
)
def student_timetable():

    if session.get("user_type") != "student":

        return redirect(
            url_for("login")
        )


    student_id = session.get(
        "student_id"
    )


    student = get_student(
        student_id
    )


    if student is None:

        session.clear()

        return redirect(
            url_for("login")
        )


    timetable = get_timetable(
        student["combination_id"],
        student["year"]
    )


    return render_template(
        "student_timetable.html",

        student=student,

        timetable=timetable
    )


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
