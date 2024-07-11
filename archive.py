import requests
from bs4 import BeautifulSoup
import json


def fetch_pdf_links(base_url, total_links=500):
    pdf_links = []
    page_number = 1

    while len(pdf_links) < total_links:
        # Construct the URL for each page
        url = f"{base_url}?&page={page_number}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the links on the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                full_link = f"https://archive.org{href}"
                pdf_links.append(full_link)
                if len(pdf_links) >= total_links:
                    break

        print(f"Page {page_number} processed. Total PDF links collected: {len(pdf_links)}")
        page_number += 1

    return pdf_links[:total_links]


def save_links_to_json(links, filename="download_links.json"):
    with open(filename, 'w') as file:
        json.dump(links, file, indent=4)
    print(f"Links saved to {filename}")


# Example usage
base_url = "https://arxiv.org/list/astro-ph.CO/recent?skip=0&show=25"
pdf_links = fetch_pdf_links(base_url)
save_links_to_json(pdf_links)
