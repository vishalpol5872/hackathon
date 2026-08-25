# Library Department

The project now includes a searchable book catalogue and a separate Library department.

## Student catalogue

- Open `/library` from the home page or student dashboard.
- Search using a book name or author.
- Browse book cards with availability and department recommendations.

## Administration

- Library admins are redirected to the separate `/library/dashboard` page.
- The Library Dashboard contains only **Manage Library** and **Manage Notices**.
- Open `/admin/library` from the admin dashboard.
- Library and Super Admin accounts can add or remove books.
- Department admins can recommend books for their own department.
- Library notices are labelled **Library** and are visible to all departments.

## Demo Library administrator

- Admin ID: `LIB001`
- Password: `library123`

## Database additions

- `books` stores the catalogue.
- `book_recommendations` connects books to recommending departments.
