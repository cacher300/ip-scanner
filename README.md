# NetProbe IP Scanner

An IP Scanner tool that scans both local and public IP addresses, storing all the data in a SQL database. The scanner provides useful information such as:

- IP Address
- Ports Open
- Name
- Type
- Helpful Info
- MAC Address
- Status

## Features

- Scans local and public IP addresses.
- Provides detailed information for each IP.
- Stores data in a SQL database.
- Contains a built-in database of public IPs sorted by country.
- Web GUI

![image](https://github.com/cacher300/ip-scanner/assets/77995433/92c40bd1-3a7b-44d6-88f6-f5c93f25edf7)

![image](https://github.com/cacher300/ip-scanner/assets/77995433/68c7c1ef-d621-4f1a-af83-b14ad4efca19)

![image](https://github.com/cacher300/ip-scanner/assets/77995433/f7eaea65-e7ea-4ac4-8daa-f68b01ecd8c1)

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Database Schema](#database-schema)
4. [Versions](#versions)
5. [License](#license)

## Installation

### Requirements

- Python
- Windows

### Installing
You can download the official latest release [here](https://github.com/cacher300/ip-scanner/releases/tag/stable) or compile it yourlsef.

Clone the repository:

```bash
git clone https://github.com/username/ip-scanner.git
```

Navigate to the project directory:

```bash
cd ip-scanner
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To start the IP scanner, run:

```bash
python main.py
```

## Database Schema

The scanner stores its results in a SQL database with the following schema:

| Column Name    | Data Type | Description                  |
|----------------|-----------|------------------------------|
| id             | INT       | Primary key                  |
| ip_address     | VARCHAR   | The IP address               |
| ports_open     | TEXT      | List of open ports           |
| name           | VARCHAR   | Name associated with the IP  |
| type           | VARCHAR   | Type of the IP (local/public)|
| info           | TEXT      | Additional information       |
| mac_address    | VARCHAR   | The MAC address              |
| status         | VARCHAR   | Status of the IP             |

## Versions

1.6 Major bugfixes and efficiency increases (First stable release I will be providing)
1.5 Added world ip database
1.4 Transferd all databases to SQL
1.3 Added world scan feature
1.2 Added basic Flask GUI
1.1 Added local scan script

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
