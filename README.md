Smart Employee Database Manager

This is a Flask + MySQL-based web application that allows users to create, manage, and interact with employee databases without needing to know SQL. It is designed for non-technical users with a clean and simple interface.

Features

- Create and delete MySQL databases dynamically
- Create tables with custom names, columns, and constraints like PRIMARY KEY and NOT NULL
- Insert, view, edit, and delete table records
- Import data into tables from CSV files
- Export table data as CSV
- View downloadable sample CSV with correct headers
- Alter table structure by adding or removing columns
- Show user-friendly error messages
- Layman terms for SQL data types in the interface
- Disallows creation of reserved database names like ems_employees and ems_temp_demo

Getting Started

Requirements:

- Python 3.8 or higher
- MySQL Server running locally
- A MySQL user with permission to manage databases starting with "ems_"


Steps:

- Clone the repository
git clone https://github.com/yourusername/employee-database-manager.git
cd employee-database-manager

- Install dependencies
pip install -r requirements.txt

- Update MySQL credentials
Open app.py and set your MySQL username and password

- Run the app
python app.py
Then open http://localhost:5000 in your browser

Project Structure

employee-management-system/
app.py
templates/
index.html
dashboard.html
view.html
static/
style.css
assets/
sample.csv
requirements.txt

Security

- Only allows database names starting with ems_
- Reserved names like ems_employees or ems_temp_demo are blocked
- SQL input is sanitized


Suggestions for Future Features

- User authentication for login
- Admin and viewer roles
- Graphical dashboards with charts
- Export full database as SQL

License
This project is licensed under the MIT License.

Author

Samarth Mishra
Website: samarthmishra.link
