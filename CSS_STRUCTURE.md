# CSS structure

Every HTML template now has a CSS file with the same name.

Examples:

- `templates/index.html` uses `static/css/index.css`
- `templates/student_dashboard.html` uses `static/css/student_dashboard.css`
- `templates/manage_notices.html` uses `static/css/manage_notices.css`
- `templates/department_chat.html` uses `static/css/department_chat.css`
- `templates/student_library.html` uses `static/css/student_library.css`
- `templates/manage_library.html` uses `static/css/manage_library.css`
- `templates/library_dashboard.html` uses `static/css/library_dashboard.css`
- `templates/student_complaint.html` uses `static/css/student_complaint.css`
- `templates/manage_complaints.html` uses `static/css/manage_complaints.css`

Each page file imports:

1. `base.css` for colours, navigation, buttons, inputs, tables and mobile basics.
2. One small file from `css/modules/` containing only that page type's layout.

This keeps one simple CSS link inside every HTML page while avoiding duplicated code.

The old `style.css` is not included in the rebuilt ZIP because none of the templates use it anymore.
