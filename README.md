# pfSense Details Fetcher

This Python script fetches details from pfSense devices and updates a CSV file with the retrieved information. It logs into the pfSense devices using the provided credentials, retrieves version information, system type, and uptime, and then writes this data to the specified CSV file.

## Features

- Prompts user for credentials and choice of input method (manual IP entry or CSV file).
- Logs into pfSense devices to retrieve version information, system type, and uptime.
- Updates the provided CSV file with the fetched details.
- Displays log messages to keep track of the process.

## Prerequisites

- Python 3.6 or higher
- `requests` library
- `BeautifulSoup4` library

You can install the required libraries using pip:

```sh
pip install requests beautifulsoup4
```

**## Usage**

1. Clone this repository to your local machine.

2. Navigate to the directory containing the script.

3. Prepare a CSV file with the following structure:

   ```csv
   Store Name,pfSense IP,pfSense Version,pfSense System Type,pfSense Uptime
   Store1,192.168.1.1,,,
   Store2,192.168.2.1,,,
   Store3,192.168.3.1,,,
   ```

4. Run the script:

   ```sh
   python pfsense_details_fetcher.py
   ```

5. Follow the on-screen prompts to enter your username and password.

6. Choose whether to enter the pfSense IP manually or use the CSV file.


## Example Output if a user selects to provide IP manually

```sh
Enter your username: admin
Enter your password: 
Do you want to provide pfSense IP manually? (yes/no): yes
Enter pfSense IP: 192.168.1.1
('Logging in to the pfSense at IP:', '192.168.1.1', 'for store:', 'manual entry')
('Logged in to the pfSense at IP:', '192.168.1.1')
('Fetching details for pfSense IP:', '192.168.1.1', 'for store:', 'manual entry')
pfSense Version: 2.5.2-RELEASE
pfSense System Type: APU2
pfSense Uptime: 15 days, 3 hours, 22 minutes
```

## Example Output if a user selects to provide IPs through CSV file

```sh
Enter your username: admin
Enter your password:
Do you want to provide pfSense IP manually? (yes/no): no
Enter the path to the CSV file: /home/adm/scripts/pfsense-script/sample.csv
('Logging in to the pfSense at IP:', '192.168.1.1', 'for store:', 'Store1')
('Logged in to the pfSense at IP:', '192.168.1.1')
('Fetching details for pfSense IP:', '192.168.1.1', 'for store:', 'Store1')
('Logging in to the pfSense at IP:', '192.168.2.1', 'for store:', 'Store2')
('Logged in to the pfSense at IP:', '192.168.2.1')
('Fetching details for pfSense IP:', '192.168.2.1', 'for store:', 'Store2')
('Logging in to the pfSense at IP:', '192.168.3.1', 'for store:', 'Store3')
('Logged in to the pfSense at IP:', '192.168.3.1')
('Fetching details for pfSense IP:', '192.168.3.1', 'for store:', 'Store3')
('Details saved to the CSV file:', '/home/adm/scripts/pfsense-script/sample.csv')
Saved!
```
