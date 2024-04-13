import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from world_sql_setup import setup_database, insert_scan_result
import requests

def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"Port {port} on {ip} is open.")
                return ip, port, True
            else:
                print(f"Port {port} on {ip} is closed.")
    except Exception as e:
        print(f"Error scanning port {port} on {ip}: {e}")
    return ip, port, False

def scan_ports_on_ip_range(ip_range, port_range, num_threads):
    open_ports = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_port = {executor.submit(scan_port, str(ip), port): (str(ip), port) for ip in ip_range for port in port_range}
        for future in as_completed(future_to_port):
            ip, port = future_to_port[future]
            try:
                _, _, is_open = future.result()
                if is_open:
                    open_ports.append((ip, port))
            except Exception as e:
                print(f"Error scanning port {port} on {ip}: {e}")
    return open_ports


def get_ip_info(ip_address):
    token = "1d55ae03741de7"
    url = f"https://ipinfo.io/{ip_address}?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        ip_info = response.json()
        location_info = f"{ip_info['city']}, {ip_info['region']}, {ip_info['country']}"
        return location_info
    else:
        print(f"Get diffrent token")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python world.py <scan_type> <num_threads> <length> <ip_list_file>")
        sys.exit(1)

    setup_database()  # Initialize the database

    scan_type = sys.argv[1]
    num_threads = int(sys.argv[2])
    length = int(sys.argv[3])
    ip_list_file = sys.argv[4]

    port_list = [int(sys.argv[i + 5]) for i in range(length)]

    with open(ip_list_file, 'r') as file:
        ip_range = file.read().splitlines()

    print("Scanning ports...")
    open_ports = scan_ports_on_ip_range(ip_range, port_list, num_threads)

    for ip, port in open_ports:

        location = get_ip_info(ip)
        ip_lookup = f"https://www.infobyip.com/ip-{ip}.html"
        insert_scan_result(ip, location, port, ip_lookup)


    print("Scan results stored in the database.")
