import socket
import ipaddress
import threading
from queue import Queue
import sys
import sqlite3

def setup_database():
    conn = sqlite3.connect('scan_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scan_results
                 (ip_address TEXT, port INTEGER, status TEXT)''')
    conn.commit()
    conn.close()


# Function to insert scan results into the database
def insert_scan_result(ip, port, status):
    conn = sqlite3.connect('scan_results.db')
    c = conn.cursor()
    c.execute("INSERT INTO scan_results (ip_address, port, status) VALUES (?, ?, ?)",
              (ip, port, status))
    conn.commit()
    conn.close()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))
    IP = s.getsockname()[0]
    s.close()
    return IP


def get_ip_range():
    local_ip = get_local_ip()
    ip_with_mask = str(local_ip) + "/24"
    network = ipaddress.ip_network(ip_with_mask, strict=False)
    return [str(ip) for ip in network.hosts()]


def scan_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((ip, port))
        s.close()
        return ip, port, "Open"
    except (socket.timeout, socket.error):
        return None


def threader(port_list):
    while True:
        for item in port_list:
            port = port_list[i]
            worker = q.get()
            result = scan_port(worker, port)
            if result:
                results_queue.put(result)
            q.task_done()


def start_local_scan(threads_num, port_list):
    setup_database()  # Set up the database and table

    for _ in range(threads_num):
        t = threading.Thread(target=threader, args=port_list)
        t.daemon = True
        t.start()
        threads.append(t)

    ip_list = get_ip_range()

    for ip in ip_list:
        q.put(ip)

    q.join()

    while not results_queue.empty():
        ip, port, status = results_queue.get()
        insert_scan_result(ip, port, status)

    for t in threads:
        t.join()


scan_type = sys.argv[1]
num_threads = sys.argv[2]
ip_range = sys.argv[3]
length = sys.argv[4]

port_list = []
i = 0
while i < int(length):
    port_list.append(sys.argv[i+4])

q = Queue()
results_queue = Queue()
threads = []

start_local_scan(int(num_threads))