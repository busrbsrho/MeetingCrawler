from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def scrape_arxiv_pdf_links(url):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Setup the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Open the URL
        driver.get(url)

        # Find all the paper entries
        entries = driver.find_elements(By.XPATH, '//dl/dd/span[@class="list-identifier"]/a[@title="Download PDF"]')

        # Extract the href attributes of these links
        pdf_links = [entry.get_attribute('href') for entry in entries]

        return pdf_links

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        # Close the browser
        driver.quit()


# Replace with the actual URL of the arXiv page you want to scrape
arxiv_url = 'https://arxiv.org/list/astro-ph/recent?skip=0&show=25'
pdf_links = scrape_arxiv_pdf_links(arxiv_url)

# Print the PDF links
print("PDF Download Links:")
for pdf_link in pdf_links:
    print(pdf_link)

# Optionally, save the links to a file
with open('arxiv_pdf_links.txt', 'w') as f:
    for pdf_link in pdf_links:
        f.write(pdf_link + '\n')
