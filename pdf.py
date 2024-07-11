import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

# Paths (update these with the correct paths on your system)
download_directory = "downloaded_pdfs"

# Create download directory if it doesn't exist
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Set up Chrome options for downloading files
chrome_options = webdriver.ChromeOptions()
prefs = {
    'download.default_directory': os.path.abspath(download_directory),  # Set the download directory
    'download.prompt_for_download': False,  # Disable download prompt
    'plugins.always_open_pdf_externally': True  # Disable PDF preview in Chrome
}
chrome_options.add_experimental_option('prefs', prefs)

# Enable logging for capturing network traffic
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}

# Initialize WebDriver (Update the path to your ChromeDriver)
driver_service = Service(executable_path='path/to/chromedriver')
driver = webdriver.Chrome(service=driver_service, options=chrome_options, desired_capabilities=caps)


def download_pdfs_with_traffic(json_file, output_directory="downloaded_pdfs"):
    # Open the JSON file containing the PDF links
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Determine the structure of the JSON data
    if isinstance(data, list):
        # JSON is a list of URLs
        links = data
    elif isinstance(data, dict):
        # JSON is a dictionary, expected to contain "pdf_links" key
        links = data.get("pdf_links", [])
    else:
        raise ValueError(
            "Invalid JSON format. The file should be either a list of URLs or a dictionary with a 'pdf_links' key.")

    for link in links:
        link = link.strip()  # Remove any whitespace or newline characters
        if link:
            try:
                # Clear previous logs
                driver.get("chrome://settings/clearBrowserData")
                time.sleep(2)  # Give it a moment to load
                driver.find_element_by_css_selector('* /deep/ #clearBrowsingDataConfirm').click()
                time.sleep(5)  # Wait for the clearing to finish

                # Visit the link to trigger the download
                driver.get(link)

                # Wait for the download to complete (you might need to adjust this time)
                time.sleep(10)

                # Capture network traffic
                logs = driver.get_log('performance')
                network_events = [json.loads(log['message'])['message'] for log in logs]

                # Filter network responses to get only the relevant ones
                download_events = [event for event in network_events if 'Network.responseReceived' in event['method']]

                # Save the traffic data to a JSON file
                traffic_filename = os.path.join(output_directory, f"{os.path.basename(link)}.traffic.json")
                with open(traffic_filename, 'w') as traffic_file:
                    json.dump(download_events, traffic_file, indent=4)

                print(f"Downloaded: {link}")
                print(f"Traffic data saved: {traffic_filename}")

            except Exception as e:
                print(f"An error occurred while downloading {link}: {e}")

    driver.quit()


# Example usage
download_pdfs_with_traffic('download_links.json', download_directory)
