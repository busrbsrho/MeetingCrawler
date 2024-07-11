import requests
from bs4 import BeautifulSoup

# Base URL to scrape
base_url = "https://catalog.data.gov/dataset?q=&sort=views_recent+desc&page="

# Function to extract download links from a given dataset page URL
def extract_download_links(dataset_url):
    download_links = []
    dataset_response = requests.get(dataset_url)
    if dataset_response.status_code == 200:
        dataset_soup = BeautifulSoup(dataset_response.content, "html.parser")
        # Look for the section that contains download resources
        resource_section = dataset_soup.find("section", {"id": "dataset-resources"})
        if resource_section:
            download_buttons = resource_section.find_all("a", class_="resource-url-analytics")
            for button in download_buttons:
                link = button.get("href")
                if link and link.startswith("http"):
                    download_links.append(link)
                    print(f"Found download link: {link}")
    return download_links

# Initialize a list to store all download links
all_download_links = []

# Loop through the first few pages (adjust the range to cover more pages)
for page_num in range(1, 3):  # Adjust the range as needed to cover more pages
    page_url = base_url + str(page_num)
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        dataset_links = soup.find_all("h3", class_="dataset-heading")
        for dataset in dataset_links:
            dataset_url = "https://catalog.data.gov" + dataset.find("a")["href"]
            print(f"Processing dataset: {dataset_url}")
            links = extract_download_links(dataset_url)
            all_download_links.extend(links)
    else:
        print(f"Failed to retrieve the page: {page_url}")

# Save the download links to a file
if all_download_links:
    with open("download_links.txt", "w") as file:
        for link in all_download_links:
            file.write(link + "\n")
    print("Download links have been saved to download_links.txt")
else:
    print("No download links found.")
