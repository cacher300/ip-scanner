from flask import Flask, render_template, request, redirect, url_for, send_file, g, jsonify
import sqlite3
import csv
import tempfile
import pandas as pd
import local
import world
from ipaddress import ip_network, IPv4Address
from local_sql_setup import get_local_db_data
from world_sql_setup import get_world_db_data

app = Flask(__name__)
DATABASE = 'ip_ranges.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        scan_type = request.form.get('scan_type')
        threads = int(request.form.get('threads'))
        ports = request.form.get('ports')
        scan_target = request.form.get('ip_range')

        port_list = []
        for port in ports.split(','):
            if '-' in port:
                start, end = map(int, port.split('-'))
                port_list.extend(range(start, end + 1))
            else:
                port_list.append(int(port))

        if scan_type == 'local_network':
            local.run_local_scan(threads, port_list)
            return redirect(url_for('local_table'))

        elif scan_type == 'ip_range':
            ip_range_list = scan_target.split('-')
            if len(ip_range_list) == 2:
                ip_start = int(IPv4Address(ip_range_list[0].strip()))
                ip_end = int(IPv4Address(ip_range_list[1].strip()))
                ip_range = [str(IPv4Address(ip)) for ip in range(ip_start, ip_end + 1)]
            else:
                ip_range = [str(ip) for ip in ip_network(scan_target).hosts()]

            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write('\n'.join(ip_range))

            world.run_world_scan(threads, temp_file.name, port_list)
            temp_file.close()

            return redirect(url_for('world_table'))

    return render_template('index.html')


@app.route('/get_ip_blocks')
def get_ip_blocks():
    df = pd.read_csv('path_to_your_csv_file.csv')
    result = df.groupby('country')[['start of block', 'end of block']].apply(lambda x: x.to_dict(orient='records')).to_dict()
    return jsonify(result)


@app.route('/world_table')
def world_table():
    data = get_world_db_data()
    return render_template('world_table.html', data=data)


@app.route('/local_table')
def local_table():
    data = get_local_db_data()
    return render_template('local_table.html', data=data)


@app.route('/world_download')
def world_download():
    conn = sqlite3.connect('world_scan_results.db')
    cursor = conn.cursor()

    query = """
    SELECT ip_addresses.id, ip_addresses.ip_address, group_concat(open_ports.port, ', ') as ports,
           ip_addresses.location,  ip_addresses.ip_lookup
    FROM ip_addresses
    LEFT JOIN open_ports ON ip_addresses.id = open_ports.ip_id
    GROUP BY ip_addresses.id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()

    csv_file_path = 'ip_ports_export.csv'
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ID', 'IP Address', 'Ports Open', 'Location', 'IP Lookup'])
        for row in data:
            csv_writer.writerow(row)

    return send_file(csv_file_path, as_attachment=True, download_name='ip_ports_export.csv')


@app.route('/local_download')
def local_download():
    conn = sqlite3.connect('local_scan_results.db')
    cursor = conn.cursor()

    query = """
    SELECT ip_addresses.id, ip_addresses.ip_address, GROUP_CONCAT(open_ports.port, ', ') as ports,
            ip_addresses.name, ip_addresses.type, ip_addresses.os, ip_addresses.mac_address, ip_addresses.status
    FROM ip_addresses
    LEFT JOIN open_ports ON ip_addresses.id = open_ports.ip_id
    GROUP BY ip_addresses.id
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()

    csv_file_path = 'ip_ports_export.csv'
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ID', 'IP Address', 'Ports Open', 'Name', "Type", 'OS', 'Mac Address', 'Status'])
        for row in data:
            csv_writer.writerow(row)

    return send_file(csv_file_path, as_attachment=True, download_name='ip_ports_export.csv')


@app.route('/local_wipe')
def local_wipe_database():
    conn = sqlite3.connect('local_scan_results.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM open_ports")
    cursor.execute("DELETE FROM ip_addresses")
    conn.commit()
    conn.close()
    return redirect(url_for('local_table'))


@app.route('/world_wipe')
def world_wipe_database():
    conn = sqlite3.connect('world_scan_results.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM open_ports")
    cursor.execute("DELETE FROM ip_addresses")
    conn.commit()
    conn.close()
    return redirect(url_for('world_table'))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/directory')
def directory():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return render_template('directory.html', tables=tables)


@app.route('/table/<name>')
def table(name):
    db = get_db()
    cursor = db.cursor()
    query = f"SELECT * FROM {name}"
    cursor.execute(query)
    data = cursor.fetchall()
    return render_template('table.html', name=name, data=data)


if __name__ == '__main__':
    app.run(debug=True)
