from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import mysql.connector
import csv
import io
import os
import time
from datetime import timedelta

app = Flask(__name__)


# CONFIG: MySQL credentials (for limited-access user)
DB_HOST = 'localhost'
DB_USER = 'webapp_user'
DB_PASSWORD = 'strong_password'  # Update securely
DB_RESTRICTED_PREFIX = 'ems_'
RESERVED_DATABASES = {'ems_employees', 'ems_temp_demo'}


def get_connection(database=None):
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database if database else None
    )


@app.before_request
def manage_session():
    session.permanent = True
    if 'start_time' not in session:
        session['start_time'] = int(time.time())
        session['user_dbs'] = []

    elapsed = int(time.time()) - session['start_time']
    if elapsed > 300:
        delete_user_databases()
        session.clear()


def delete_user_databases():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for db in session.get('user_dbs', []):
            if db not in RESERVED_DATABASES:
                cursor.execute(f"DROP DATABASE IF EXISTS `{db}`")
        conn.commit()
    except:
        pass
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    all_dbs = [db[0] for db in cursor.fetchall() if db[0].startswith(DB_RESTRICTED_PREFIX)]
    return render_template('dashboard.html', databases=all_dbs, timer=get_remaining_time())


@app.route('/create_database', methods=['POST'])
def create_database():
    dbname = request.form['dbname'].strip()
    full_name = DB_RESTRICTED_PREFIX + dbname
    if full_name in RESERVED_DATABASES:
        flash(f"The database name '{full_name}' is reserved.", 'error')
        return redirect('/dashboard')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    all_dbs = [db[0] for db in cursor.fetchall()]
    if full_name in all_dbs:
        flash("Database already exists!", 'error')
    else:
        cursor.execute(f"CREATE DATABASE `{full_name}`")
        conn.commit()
        session['user_dbs'].append(full_name)
        flash(f"Database '{full_name}' created successfully!", 'success')
    return redirect('/dashboard')


@app.route('/delete_database/<dbname>', methods=['POST'])
def delete_database(dbname):
    if dbname in RESERVED_DATABASES:
        flash("You are not allowed to delete this database.", 'error')
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS `{dbname}`")
        conn.commit()
        flash(f"Database '{dbname}' deleted.", 'success')
    return redirect('/dashboard')


@app.route('/select/<database>')
def select_table(database):
    try:
        conn = get_connection(database)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        flash(f"Error fetching tables: {e}", 'error')
        tables = []

    timer = get_remaining_time()
    return render_template('select.html', database=database, tables=tables, timer=timer)


@app.route('/create_table/<database>', methods=['POST'])
def create_table(database):
    table_name = request.form['table_name']
    column_names = request.form.getlist('column_name[]')
    data_types = request.form.getlist('data_type[]')
    primary_keys = request.form.getlist('primary_key[]')
    not_nulls = request.form.getlist('not_null[]')

    columns_sql = []
    pk_count = 0
    for i in range(len(column_names)):
        name = column_names[i].strip()
        dtype = data_types[i]
        constraints = []
        if f"col{i}" in primary_keys:
            constraints.append("PRIMARY KEY")
            pk_count += 1
        if f"col{i}" in not_nulls:
            constraints.append("NOT NULL")
        column_def = f"`{name}` {dtype} {' '.join(constraints)}"
        columns_sql.append(column_def)

    if pk_count > 1:
        flash("Only one PRIMARY KEY is allowed.", 'error')
        return redirect(f"/select/{database}")

    columns_clause = ", ".join(columns_sql)
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE `{table_name}` ({columns_clause})")
    conn.commit()
    flash(f"Table '{table_name}' created successfully!", 'success')
    return redirect(f"/select/{database}")


@app.route('/delete_table/<database>/<table>', methods=['POST'])
def delete_table(database, table):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
    conn.commit()
    flash(f"Table '{table}' deleted.", 'success')
    return redirect(f"/select/{database}")


@app.route('/view/<database>/<table>')
def view_table(database, table):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `{table}`")
    rows = cursor.fetchall()
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    columns = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('view.html', database=database, table=table, rows=rows, columns=columns, timer=get_remaining_time())



@app.route('/insert/<database>/<table>', methods=['POST'])
def insert_row(database, table):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    columns = [row[0] for row in cursor.fetchall()]
    values = [request.form.get(col) for col in columns]

    if None in values or "" in values:
        flash("All fields must be filled.", 'error')
        return redirect(f"/view/{database}/{table}")

    placeholders = ', '.join(['%s'] * len(values))
    sql = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.execute(sql, values)
    conn.commit()
    flash("Row inserted successfully!", 'success')
    return redirect(f"/view/{database}/{table}")


@app.route('/delete_row/<database>/<table>/<int:row_id>', methods=['POST'])
def delete_row_route(database, table, row_id):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM `{table}` WHERE id = %s", (row_id,))
    conn.commit()
    flash("Row deleted.", 'success')
    return redirect(f"/view/{database}/{table}")


@app.route('/import_csv/<database>/<table>', methods=['POST'])
def import_csv(database, table):
    if 'file' not in request.files or request.files['file'].filename == '':
        flash("Please select a CSV file to upload.", 'error')
        return redirect(f"/view/{database}/{table}")

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        flash("Only CSV files are allowed.", 'error')
        return redirect(f"/view/{database}/{table}")

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    rows = list(csv_input)

    if not rows:
        flash("CSV file is empty.", 'error')
        return redirect(f"/view/{database}/{table}")

    headers = rows[0]
    data = rows[1:]

    try:
        conn = get_connection(database)
        cursor = conn.cursor()

        for row in data:
            if len(row) != len(headers):
                flash("Mismatch between CSV headers and row data.", 'error')
                return redirect(f"/view/{database}/{table}")
            try:
                cursor.execute(
                    f"INSERT INTO `{table}` VALUES ({', '.join(['%s'] * len(row))})", row
                )
            except mysql.connector.errors.IntegrityError as e:
                if "1062" in str(e):
                    flash("Duplicate primary key detected. Please ensure unique values for primary key columns.", 'error')
                    conn.rollback()
                    return redirect(f"/view/{database}/{table}")
                else:
                    raise e

        conn.commit()
        flash("CSV data imported successfully.", 'success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(f"/view/{database}/{table}")





@app.route('/export_csv/<database>/<table>')
def export_csv(database, table):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `{table}`")
    rows = cursor.fetchall()
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    columns = [row[0] for row in cursor.fetchall()]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)
    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name=f"{table}.csv", as_attachment=True, mimetype='text/csv')


@app.route('/download_sample/<database>/<table>')
def download_sample_csv(database, table):
    conn = get_connection(database)
    cursor = conn.cursor()
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    columns = [row[0] for row in cursor.fetchall()]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerow(['sample'] * len(columns))
    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name=f"{table}_sample.csv", as_attachment=True, mimetype='text/csv')


def get_remaining_time():
    start = session.get('start_time', int(time.time()))
    return max(0, 300 - (int(time.time()) - start))


if __name__ == "__main__":
    app.run()

