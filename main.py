from flask import Flask, render_template, request, redirect, url_for, send_file
import subprocess
from sql_setup import get_db_data
import sqlite3
import csv
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        scan_type = request.form.get('scan_type')
        threads = int(request.form.get('threads'))
        ports = request.form.get('ports')
        ip_range = request.form.get('ip_range')

        ip_range = '' if ip_range is None else ip_range

        port_list = ports.split(',')
        port_list = [port.strip() for port in port_list]
        length = len(port_list)

        print(f"Scan Type: {scan_type}, Threads: {threads}, IP Range: {ip_range}")
        subprocess.run(['python', 'backend.py', scan_type, str(threads), ip_range, str(length)] + port_list, check=True)

        return redirect(url_for('table'))

    return render_template('index.html')


@app.route('/table')
def table():
    data = get_db_data()
    return render_template('table.html', data=data)


@app.route('/download')
def download():
    conn = sqlite3.connect('scan_results.db')
    cursor = conn.cursor()

    query = """
    SELECT ip_addresses.id, ip_addresses.ip_address, group_concat(open_ports.port, ', ') as ports
    FROM ip_addresses
    LEFT JOIN open_ports ON ip_addresses.id = open_ports.ip_id
    GROUP BY ip_addresses.id
    """
    cursor.execute(query)
    data = cursor.fetchall()

    csv_file_path = 'ip_ports_export.csv'

    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ID', 'IP Address', 'Ports Open'])  # Column headers
        for row in data:
            csv_writer.writerow(row)

    conn.close()

    return send_file(csv_file_path, as_attachment=True, download_name='ip_ports_export.csv')


@app.route('/wipe')
def wipe_database():
    conn = sqlite3.connect('scan_results.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM open_ports")  # Replace 'port_table' with your actual table name for ports

    cursor.execute("DELETE FROM ip_addresses")

    conn.commit()
    conn.close()

    return "Database wiped successfully."


if __name__ == '__main__':
    app.run(debug=True)
