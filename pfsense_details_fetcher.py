import csv
import requests
from bs4 import BeautifulSoup
import getpass

# Suppress insecure request warnings
requests.packages.urllib3.disable_warnings()

def prompt_user_credentials():
    username = raw_input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    return username, password

def prompt_user_choice():
    choice = raw_input("Do you want to provide pfSense IP manually? (yes/no): ").lower()
    return choice

def get_csrf_token(BASE_URL):
    try:
        response = requests.get(BASE_URL, verify=False, timeout=10)
        response.raise_for_status()
        html_content = response.text
        csrf_token = html_content.split('var csrfMagicToken = "')[1].split('"')[0]
        return csrf_token
    except (requests.RequestException, IndexError) as e:
        print("Failed to get CSRF token from {}: {}".format(BASE_URL, e))
        return None

def login_to_pfSense(BASE_URL, username, password):
    csrf_token = get_csrf_token(BASE_URL)
    if not csrf_token:
        return None
    login_data = {
        "__csrf_magic": csrf_token,
        "usernamefld": username,
        "passwordfld": password,
        "login": "Login"
    }
    try:
        login_response = requests.post(BASE_URL, data=login_data, verify=False, timeout=10)
        login_response.raise_for_status()
        return login_response
    except requests.RequestException as e:
        print("Failed to login to pfSense at {}: {}".format(BASE_URL, e))
        return None

def fetch_pfSense_details(pfSense_ip, username, password, store_name):
    BASE_URL = "https://" + pfSense_ip
    print("Logging in to the pfSense at IP: {} for store: {}".format(pfSense_ip, store_name))
    login_response = login_to_pfSense(BASE_URL, username, password)
    if login_response and "Dashboard" in login_response.text:
        print("Logged in to the pfSense at IP: {}".format(pfSense_ip))
        soup = BeautifulSoup(login_response.text, 'html.parser')
        version_info = soup.find('th', text='Version').find_next_sibling('td').text.strip().split('\n')[0]
        system_info = soup.find('th', text='System').find_next_sibling('td')
        if system_info:
            system_info_text = system_info.get_text(separator=" ").strip()
            if "PC Engines" in system_info_text:
                system_type = system_info_text.split("PC Engines")[1].split("Netgate Device ID")[0].strip()
            else:
                system_type = system_info_text.split("Netgate Device ID")[0].strip()
        uptime = soup.find('th', text='Uptime').find_next_sibling('td').text.strip()
        print("Fetching details for pfSense IP: {} for store: {}".format(pfSense_ip, store_name))
        return version_info, system_type, uptime
    else:
        if login_response and "pfSense" not in login_response.text:
            print("Not a pfSense device at IP: {} for store: {}".format(pfSense_ip, store_name))
        else:
            print("Failed to fetch details for pfSense IP: {} for store: {}".format(pfSense_ip, store_name))
        return "not a pfSense", "not a pfSense", "not a pfSense"

def update_csv_with_pfSense_details(csv_file_path, username, password):
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        
        # Check if the new columns already exist
        new_columns = ['pfSense Version', 'pfSense System Type', 'pfSense Uptime']
        if not all(column in fieldnames for column in new_columns):
            fieldnames += new_columns
        
        rows = list(reader)
        
    with open(csv_file_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            store_name = row['Store Name']
            pfSense_ip = row['pfSense IP']
            version_info, system_type, uptime = fetch_pfSense_details(pfSense_ip, username, password, store_name)
            if version_info == "not a pfSense":
                print("Skipping {} as it is not a pfSense device.".format(pfSense_ip))
            row['pfSense Version'] = version_info
            row['pfSense System Type'] = system_type
            row['pfSense Uptime'] = uptime
            writer.writerow(row)
        print("Details saved to the CSV file: {}".format(csv_file_path))
        print("Saved!")

def main():
    username, password = prompt_user_credentials()
    choice = prompt_user_choice()

    if choice == "yes":
        pfSense_ip = raw_input("Enter pfSense IP: ")
        store_name = "manual entry"  # Placeholder for store name in manual entry
        version_info, system_type, uptime = fetch_pfSense_details(pfSense_ip, username, password, store_name)
        if version_info is not None:
            print("pfSense Version: " + version_info.encode('utf-8'))
            print("pfSense System Type: " + system_type.encode('utf-8'))
            print("pfSense Uptime: " + uptime.encode('utf-8'))
        else:
            print("Failed to fetch details for pfSense IP: " + pfSense_ip)
    elif choice == "no":
        csv_file_path = raw_input("Enter the path to the CSV file: ")
        update_csv_with_pfSense_details(csv_file_path, username, password)
    else:
        print("Invalid choice. Exiting.")
        exit(1)

if __name__ == "__main__":
    main()
