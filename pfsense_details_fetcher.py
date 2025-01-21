import csv
import requests
from bs4 import BeautifulSoup
import getpass

# Suppress insecure request warnings
requests.packages.urllib3.disable_warnings()

def prompt_user_credentials():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    return username, password

def prompt_user_choice():
    choice = input("Do you want to provide pfSense IP manually? (yes/no): ").lower()
    return choice

def get_csrf_token(BASE_URL):
    try:
        response = requests.get(BASE_URL, verify=False, timeout=10)
        response.raise_for_status()
        html_content = response.text
        csrf_token = html_content.split('var csrfMagicToken = "')[1].split('"')[0]
        return csrf_token
    except (requests.RequestException, IndexError) as e:
        print(f"Failed to get CSRF token from {BASE_URL}: {e}")
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
        print(f"Failed to login to pfSense at {BASE_URL}: {e}")
        return None

def fetch_pfSense_details(pfSense_ip, username, password, store_name):
    BASE_URL = f"https://{pfSense_ip}"
    print(f"Logging in to the pfSense at IP: {pfSense_ip} for store: {store_name}")
    login_response = login_to_pfSense(BASE_URL, username, password)
    if login_response and "Dashboard" in login_response.text:
        print(f"Logged in to the pfSense at IP: {pfSense_ip}")
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
        print(f"Fetching details for pfSense IP: {pfSense_ip} for store: {store_name}")
        return version_info, system_type, uptime
    else:
        if login_response and "pfSense" not in login_response.text:
            print(f"Not a pfSense device at IP: {pfSense_ip} for store: {store_name}")
        else:
            print(f"Failed to fetch details for pfSense IP: {pfSense_ip} for store: {store_name}")
        return "not a pfSense", "not a pfSense", "not a pfSense"

def update_csv_with_pfSense_details(csv_file_path, username, password):
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        # Check if the new columns already exist
        new_columns = ['pfSense Version', 'pfSense System Type', 'pfSense Uptime']
        if not all(column in fieldnames for column in new_columns):
            fieldnames += new_columns

        rows = list(reader)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            store_name = row['Store Name']
            pfSense_ip = row['pfSense IP']
            version_info, system_type, uptime = fetch_pfSense_details(pfSense_ip, username, password, store_name)
            if version_info == "not a pfSense":
                print(f"Skipping {pfSense_ip} as it is not a pfSense device.")
            row['pfSense Version'] = version_info
            row['pfSense System Type'] = system_type
            row['pfSense Uptime'] = uptime
            writer.writerow(row)
        print(f"Details saved to the CSV file: {csv_file_path}")

def main():
    username, password = prompt_user_credentials()
    choice = prompt_user_choice()

    if choice == "yes":
        pfSense_ip = input("Enter pfSense IP: ")
        store_name = "manual entry"  # Placeholder for store name in manual entry
        version_info, system_type, uptime = fetch_pfSense_details(pfSense_ip, username, password, store_name)
        if version_info is not None:
            print(f"pfSense Version: {version_info}")
            print(f"pfSense System Type: {system_type}")
            print(f"pfSense Uptime: {uptime}")
        else:
            print(f"Failed to fetch details for pfSense IP: {pfSense_ip}")
    elif choice == "no":
        csv_file_path = input("Enter the path to the CSV file: ")
        update_csv_with_pfSense_details(csv_file_path, username, password)
    else:
        print("Invalid choice. Exiting.")
        exit(1)

if __name__ == "__main__":
    main()
