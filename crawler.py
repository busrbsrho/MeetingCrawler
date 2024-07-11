import json
import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from scapy.arch import get_if_addr
from scapy.config import conf
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from queue import Queue  # Change from LifoQueue to Queue
from scapy.all import sniff, AsyncSniffer, wrpcap
from datetime import datetime
import pyshark
import random
import subprocess
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self, urls, operation, max_links, headless=False):
        self.urls = urls  # This is now a list of URLs
        self.max_links = max_links
        self.visited = set()
        self.total_links = 0
        self.queue = Queue()  # Use a FIFO Queue for BFS
        self.download_dir ="downloads_for_project"
        self.crawled_links = set()
        self.network_condition = "normal"
        self.operation = operation

        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--mute-audio")

        # Inside the __init__ method of your WebCrawler class
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        print(f"Chrome is configured to download to: {self.download_dir}")
        chrome_options.add_experimental_option("prefs", prefs)

        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL', 'browser': 'ALL'}
        chrome_options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
        print(f"Download directory set in Chrome options: {self.download_dir}")
        print(f"Chrome preferences: {prefs}")
        assert os.path.exists(self.download_dir), f"Download directory does not exist: {self.download_dir}"
        assert os.access(self.download_dir, os.W_OK), f"No write permission for download directory: {self.download_dir}"

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        os.makedirs(self.download_dir, exist_ok=True)
        self.driver.maximize_window()
    def save_browser_log(self, logfile):
        print("Retrieving performance logs...")
        logs = self.driver.get_log('performance')  # Retrieves performance logs
        if not logs:
            print("No logs to save.")
        else:
            with open(logfile, 'w', encoding='utf-8') as file:
                for entry in logs:
                    file.write(f"{entry['message']}\n")
            print(f"Logs saved to {logfile}.")

    def fetch_content(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)
            #self.play_videos(url)
            return self.driver.page_source
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def play_videos(self, url):
        try:
         #   self.play_cnn_video()
            parsed_url = urlparse(url)
            if "youtube.com" in parsed_url.netloc:
                self.play_youtube_video()
            else:
                self.play_generic_video(url)
        except Exception as e:
            print(f"Failed to play video on {url}: {e}")

    def play_youtube_video(self):
        try:
            play_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.ytp-large-play-button'))
            )
            play_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"Failed to play YouTube video: {e}")

    def play_generic_video(self,url):
        if "cnn.com" in url:
            try:
                # Wait for the element to be present in the DOM for up to 20 seconds
                element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="player-player-cms.cnn.com/_components/video-player/instances/clxotd1cq00053b6kgzxeusch@published-pui-wrapper"]/div/div/button'))
                )
                # Perform the click operation if the element is found
                element.click()
                print("Element found and clicked.")

            except TimeoutException:
                print("The specified element was not found within the given time frame.")
            except Exception as e:
                print(f"An error occurred: {e}")


        if "bbc.com" in url:
            try:
                time.sleep(6)

                # Wait for the element to be present in the DOM
                element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="main-content"]/article/section[1]/div/div/div[1]/div[1]/div/div/button/div[1]'))
                )

                # Create an instance of ActionChains
                actions = ActionChains(self.driver)

                # Perform a double-click on the element
                actions.double_click(element).perform()

                print("Element found and double-clicked.")
            except TimeoutException:
                print("The specified element was not found within the given time frame.")
            except Exception as e:
                print(f"An error occurred: {e}")


        if "techcrunch.com" in url:
            try:

                # Allow the page to load
                time.sleep(5)  # Adjust as necessary for your connection speed

                # Locate the embedded YouTube video iframe
                iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'youtube.com')]")

                # Switch to the iframe context

                self.driver.switch_to.frame(iframe)

                # Locate the play button within the iframe and click it
                play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-large-play-button")
                play_button.click()
                print("video clicked")

            except TimeoutException:
                print("The specified element was not found within the given time frame.")
            except Exception as e:
                print(f"An error occurred: {e}")


        if "israelhayom.co.il" in url :
            try:
                # Open the desired webpage
                self.driver.get(
                    "https://www.israelhayom.co.il/podcasts/article/15800076")

                time.sleep(6)



                element = self.driver.find_element(By.XPATH, "//*[contains(@id, 'video_')]/button")
                element.click()
                print("Element found and clicked.")
            except TimeoutException:
                print("The specified element was not found within the given time frame.")
            except Exception as e:
                print(f"An error occurred: {e}")



    def handle_iframes(self):
        try:
            iframe_elements = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframe_elements:
                self.driver.switch_to.frame(iframe)
                video_elements = self.driver.find_elements(By.XPATH, '//*[@id="movie_player"]/div[4]/button')
                for video in video_elements:
                    self.attempt_to_play_video(video)
                self.driver.switch_to.default_content()
        except Exception as e:
            print(f"Error handling iframes: {e}")

    def click_near_center_of_screen(self):
        try:
            action = ActionChains(self.driver)
            # Get the size of the window
            window_size = self.driver.get_window_size()
            center_x = window_size['width'] / 2
            center_y = window_size['height'] / 2

            # Click slightly to the left of the center of the screen
            offset_x = center_x - 50  # Move 50 pixels left from the center
            offset_y = center_y

            # Perform the click action
            action.move_by_offset(offset_x, offset_y).click().perform()
            print(f"Clicked at ({offset_x}, {offset_y}) relative to the screen center.")
            time.sleep(5)  # Wait to see if the video starts playing
        except Exception as e:
            print(f"Error while trying to click near the center of the screen: {e}")


    def attempt_to_play_video(self, video):
        try:
            if video.get_attribute('paused') == 'true':
                self.driver.execute_script("arguments[0].play();", video)
                print("Playing video via JavaScript execution.")
                time.sleep(5)  # Wait for some video to play
        except Exception as e:
            print(f"Error while trying to play video: {e}")

    def click_play_button(self):
        try:
            # Example play button selectors, may need to adjust for CNN
            play_button_selectors = [
                'button.play-button',
                'playIconTitle',
                '.video-player__play-button',
                'div.vjs-play-control',
                'button[aria-label="Play"]',
                '.overlay-play-button',  # Example for CNN overlay play button
                'div.play-overlay'  # Another possible overlay selector
            ]
            for selector in play_button_selectors:
                try:
                    play_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.scroll_into_view(play_button)
                    play_button.click()
                    print(f"Clicked play button with selector {selector}")
                    time.sleep(5)
                    break
                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    print(f"Failed to click play button with selector {selector}: {e}")

        except Exception as e:
            print(f"Failed to find and click play button: {e}")


    def click_center_of_element(self, element):
        try:
            action = ActionChains(self.driver)
            # Move to the center of the element and click
            action.move_to_element(element).move_by_offset(
                element.size['width'] / 2, element.size['height'] / 2).click().perform()
            time.sleep(5)  # Wait to see if the video starts playing
        except Exception as e:
            print(f"Error while trying to click in the middle of the video: {e}")


    def scroll_into_view(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except Exception as e:
            print(f"Error scrolling element into view: {e}")

    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(base_url, href)
            if self.is_valid_url(full_url):
                links.add(full_url)
        return links

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def categorize_url(self, url):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        print(f"Categorizing URL: {url}")

        if any(video_keyword in netloc for video_keyword in ['youtube', 'vimeo', 'dailymotion', 'netflix', 'hulu']):
            category = "video"
            attribution = "VOD"
        elif 'zoom.us' in netloc or 'zoom.com' in netloc:
            category = "messaging"
            attribution = "real-time"
        elif 'slack.com' in netloc or 'teams.microsoft.com' in netloc or 'skype.com' in netloc or 'whatsapp.com' in netloc or 'telegram.org' in netloc:
            category = "messaging"
            attribution = "chat"
        elif 'webrtc.org' in netloc:
            category = "messaging"
            attribution = "real-time"
        elif any(path.endswith(ext) for ext in
                 ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.zip', '.tar', '.gz', '.rar', '.exe']):
            category = "file"
            attribution = "file download"
        elif self.operation == "download":
            category = "file"
            attribution = "file download"
        else:
            category = "other"
            attribution = "browsing"

        print(f"URL categorized as Category: {category}, Attribution: {attribution}")
        return category, attribution

    def sniff_traffic(self, timeout=30, identifier=""):
        captured_packets = []

        def packet_callback(packet):
            captured_packets.append(packet)

        print(f"Starting sniffing for {timeout} seconds with identifier {identifier}...")
        sniffer = AsyncSniffer(prn=packet_callback, store=0)
        sniffer.start()
        time.sleep(timeout)
        sniffer.stop()
        print(f"Sniffing complete. Captured {len(captured_packets)} packets.")
        return captured_packets

    def download_file(self, url, retries=1):
        filename = urlparse(url).path.split('/')[-1]
        local_filename = os.path.join(self.download_dir, filename)
        logfile = os.path.join(self.download_dir, f'download_log_{filename.replace(".", "_")}.txt')

        print(f"Downloading file from: {url}")
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        for attempt in range(retries):
            try:
                with session.get(url, stream=True, allow_redirects=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('Content-Length', 0))
                    downloaded_size = 0
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)

                    # Log after each attempt, regardless of outcome
                    self.save_browser_log(logfile)

                    if downloaded_size == total_size:
                        print(f"Successfully downloaded file: {local_filename}")
                        break
                    else:
                        print(f"Download incomplete: {downloaded_size}/{total_size} bytes downloaded.")
                        if attempt < retries - 1:
                            print(f"Retrying download... (Attempt {attempt + 1}/{retries})")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")
                if attempt < retries - 1:
                    print(f"Retrying download... (Attempt {attempt + 1}/{retries})")

            # Log after each attempt, including after the last one, regardless of its success
            self.save_browser_log(logfile)


    def apply_random_network_conditions(self):
        conditions = [
            "normal",
            "delay --time 200ms",
            "drop --rate 10%",
            "throttle --rate 1Mbps",
            "duplicate --rate 5%",
            "corrupt --rate 5%"
        ]
        chosen_condition = random.choice(conditions)
        self.network_condition = chosen_condition
        if chosen_condition == "normal":
            print("Applying normal network conditions.")
            subprocess.call([r"clumsy.exe", "-stop"])
        else:
            print(f"Applying network condition: {chosen_condition}")
            subprocess.call([r"clumsy.exe", chosen_condition])

    def close(self):
        if self.driver:
            print("Closing the WebDriver.")
            self.driver.quit()

    def organize_pcap(self, pcap_file, url, timestamp):
        try:
            metadata = self.extract_pcap_metadata(pcap_file)
        except Exception as e:
            print(f"Failed to extract metadata from {pcap_file}: {e}")
            metadata = {"network_conditions": self.network_condition}

        # Extract the application name based on the URL or some other logic
        application_name = self.extract_application_name(url)  # This needs to be implemented

        category, attribution = self.categorize_url(url)
        network_conditions = metadata.get("network_conditions", self.network_condition)
        date = timestamp.split('_')[0]

        # Define new folder structure based on application name
        vod_folder = os.path.join("Data", attribution)
        application_folder = os.path.join(vod_folder, application_name)
        network_conditions_folder = os.path.join(application_folder, network_conditions)
        date_folder = os.path.join(network_conditions_folder, date)

        # Create directories if they don't exist
        for folder in [vod_folder, application_folder, network_conditions_folder, date_folder]:
            os.makedirs(folder, exist_ok=True)

        print(f"Organizing pcap file: {pcap_file} into {date_folder}")

        # Move the pcap file
        destination_pcap_file = os.path.join(date_folder, os.path.basename(pcap_file))
        try:
            shutil.move(pcap_file, destination_pcap_file)
            print(f"Moved {pcap_file ,{date_folder}}")
        except Exception as e:
            print(f"Failed to move pcap file {pcap_file} to {date_folder}: {e}")

        # Save the metadata to a text file with the same name as the pcap file
        metadata_file = destination_pcap_file.replace(".pcap", ".txt")
        try:
            with open(metadata_file, "w") as f:
                f.write(f"URL: {url}\n")
                f.write(f"Application: {application_name}\n")
                f.write(f"Category: {category}\n")
                f.write(f"Attribution: {attribution}\n")
                f.write(f"Date: {date}\n")
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
            print(f"Saved metadata to {metadata_file}")
        except Exception as e:
            print(f"Failed to save metadata file for {pcap_file}: {e}")

    def extract_application_name(self, url):
        # Parse the URL to get components
        parsed_url = urlparse(url)
        # Extract the domain name (netloc) and split it by dots
        domain_parts = parsed_url.netloc.split('.')
        # Check if it's a common SLD+TLD format; adjust indexing based on your needs
        if len(domain_parts) > 2:
            # Exclude subdomains if present (common for sites like 'www')
            return '.'.join(domain_parts[-2:])
        elif len(domain_parts) == 2:
            # Directly use the domain if it's just a second-level and top-level domain
            return '.'.join(domain_parts)
        else:
            # Fallback if the URL is somehow unusual or malformed
            return "Unknown"

    def extract_pcap_metadata(self, pcap_file):
        cap = pyshark.FileCapture(pcap_file, only_summaries=True)
        return {"network_conditions": self.network_condition}

    def download_files(self, content, base_url):
        # Define the pattern for downloadable files
        file_pattern = re.compile(
            r'href=["\'](.*?(\.zip|\.pdf|\.exe|\.tar\.gz|\.rar|\.7z|\.docx|\.xlsx|\.jpg|\.png|\.mp3|\.mp4|\.csv))["\']')

        # Find all matches in the content
        matches = file_pattern.findall(content)

        for match in matches:
            file_url = match[0]  # Get the URL from the regex match

            # Convert relative URLs to absolute URLs
            file_url = urljoin(base_url, file_url)
            print(f"Attempting to download file from URL: {file_url}")

            # Validate the URL (ensure it's properly formed and points to a downloadable file)
            parsed_url = urlparse(file_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                print(f"Skipping invalid URL: {file_url}")
                continue

            try:
                # Download the file using requests
                response = requests.get(file_url, stream=True)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                print(f"Server response status for {file_url}: {response.status_code}")

                # Determine the file name (use the last part of the URL path)
                filename = os.path.basename(parsed_url.path)
                file_name_without_extension, file_extension = os.path.splitext(filename)
                unique_id = f"{int(time.time())}"
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                unique_file_name = f"{file_name_without_extension}_{unique_id}_{timestamp}{file_extension}"

                # Save the file to the local filesystem in the specified downloads directory
                file_path = os.path.join(self.download_dir, unique_file_name)
                print(f"Saving file as: {file_path}")

                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            file.write(chunk)

                print(f"Downloaded file {file_url} saved as {file_path}")

            except requests.RequestException as e:
                print(f"Failed to download {file_url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        # Verify the directory contents (optional)
        print("Files in download directory:", os.listdir(self.download_dir))

    def is_downloadable(self, url):
        downloadable_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.zip', '.tar', '.gz', '.rar',
                                   '.exe']
        return any(url.endswith(ext) for ext in downloadable_extensions)

    def download_and_capture(self, url, retries=5):
        filename = urlparse(url).path.split('/')[-1]
        local_filename = os.path.join(self.download_dir, filename)
        print(f"Starting traffic capture for download: {url}")
        unique_identifier = f"{int(time.time())}_download"

        # Start the sniffer before initiating the download
        print("Starting sniffer...")
        sniffer = AsyncSniffer()
        sniffer.start()

        # Download the file
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            for attempt in range(retries):
                try:
                    with session.get(url, stream=True, allow_redirects=True) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('Content-Length', 0))
                        downloaded_size = 0
                        with open(local_filename, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                        if downloaded_size == total_size:
                            print(f"Successfully downloaded file: {local_filename}")
                            break
                        else:
                            print(f"Download incomplete: {downloaded_size}/{total_size} bytes downloaded.")
                            if attempt < retries - 1:
                                print(f"Retrying download... (Attempt {attempt + 1}/{retries})")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download {url}: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying download... (Attempt {attempt + 1}/{retries})")

        finally:
            # Stop the sniffer after download is completed
            print("Stopping sniffer...")
            sniffer.stop()
            captured_packets = sniffer.results

            # Save the captured packets to a .pcap file
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            pcap_file = f"download_traffic_{timestamp}_{unique_identifier}.pcap"
            if captured_packets:
                wrpcap(pcap_file, captured_packets)
                print(f"Traffic for {url} download recorded in {pcap_file}")
                self.organize_pcap(pcap_file, url, timestamp)
            else:
                print("No packets captured for download")

    def wait_for_download_completion(self, download_dir, timeout=600):
        start_time = time.time()
        while any(fname.endswith('.crdownload') for fname in os.listdir(download_dir)):
            if time.time() - start_time > timeout:
                raise TimeoutError("Download did not complete within the given timeout period")
            time.sleep(1)
        print("Download completed")

    def click_and_download(self, url):
        print(f"Click and download from: {url}")
        try:
            self.driver.get(url)
            time.sleep(3)  # wait for the page and elements to load

            # Prepare for packet capture
            unique_identifier = f"{int(time.time())}_click"
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            pcap_file = f"download_traffic_{timestamp}_{unique_identifier}.pcap"

            # Start the sniffer
            print("Starting packet capture")
            self.start_capture(unique_identifier)

            # Click the download buttons
            download_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Download')]")
            for button in download_buttons:
                button.click()
                time.sleep(5)  # Short sleep to ensure downloads start

            # Wait for downloads to complete
            print("Waiting for downloads to complete")
            download_dir = self.download_dir
            self.wait_for_download_completion(download_dir)
            print(f"Downloaded from: {url}")

            # Stop the sniffer and get results
            captured_packets = self.stop_capture()

            # Save the captured packets if any were captured
            if captured_packets:
                wrpcap(pcap_file, captured_packets)
                print(f"Traffic for {url} download recorded in {pcap_file}")
                self.organize_pcap(pcap_file, url, timestamp)
            else:
                print("No packets captured for download")

        except Exception as e:
            print(f"Failed to interact and download from {url}: {e}")
            # Stop the sniffer and get results
            captured_packets = self.stop_capture()

            # Save the captured packets if any were captured
            if captured_packets:
                wrpcap(pcap_file, captured_packets)
                print(f"Traffic for {url} download recorded in {pcap_file}")
            else:
                print("No packets captured for download")

    def download_embedded_content(self):
        try:
            # Check for iframe
            iframe_elements = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframe_elements:
                src = iframe.get_attribute('src')
                if self.is_valid_url(src) and self.is_downloadable(src):
                    self.download_and_capture(src)
                    return

            # Check for embed tag
            embed_elements = self.driver.find_elements(By.TAG_NAME, 'embed')
            for embed in embed_elements:
                src = embed.get_attribute('src')
                if self.is_valid_url(src) and self.is_downloadable(src):
                    self.download_and_capture(src)
                    return

            # Check for object tag
            object_elements = self.driver.find_elements(By.TAG_NAME, 'object')
            for obj in object_elements:
                data = obj.get_attribute('data')
                if self.is_valid_url(data) and self.is_downloadable(data):
                    self.download_and_capture(data)
                    return

            print("No downloadable embedded content found.")
        except Exception as e:
            print(f"Failed to download embedded content: {e}")

    def start_crawling(self, operation):
        try:
            if operation.lower() == 'download':
                self.crawl_for_downloads()
            elif operation.lower() == 'browse':
                self.crawl_for_browsing()
            elif operation.lower() == 'video':
                self.crawl_for_video()
            else:
                print("Invalid operation specified. Please choose from 'downloading', 'browsing', or 'video'.")
        finally:
            self.close()

    def wait_for_downloads(self):
        # Poll the download directory to check for the completion of downloads
        while True:
            if not any([filename.endswith(".crdownload") for filename in os.listdir(self.download_dir)]):
                break
            print("Waiting for downloads to complete...")
            time.sleep(2)  # Wait a bit before checking again

    def crawl_for_downloads(self):
        for url in self.urls:
            self.queue.put(url)

        while not self.queue.empty() and self.total_links < self.max_links:
            url = self.queue.get()
            if url in self.visited:
                self.queue.task_done()
                continue

            print(f"Crawling: {url}")
            self.visited.add(url)
            self.total_links += 1

            unique_identifier = f"{self.total_links}_{int(time.time())}"
            self.apply_random_network_conditions()

            self.close_browser()  # Close any previous browser session
            self.open_browser()  # Open a new browser session

            self.start_capture(unique_identifier)
            content = self.fetch_content(url)
            if content:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                pcap_file = f"downloadzip_traffic_{self.total_links}_{timestamp}_{unique_identifier}.pcap"
                log_file = f"browser_log_{self.total_links}_{timestamp}_{unique_identifier}.txt"
                self.save_browser_log(log_file)
                print(f"Browser log for {url} saved in {log_file}")

                links = self.extract_links(content, url)
                self.download_files(content, url)
                self.wait_for_downloads()  # Wait for all downloads to complete

                for link in links:
                    if link not in self.visited:
                        self.queue.put(link)
                self.crawled_links.update(links)

                captured_packets = self.stop_capture()
                if captured_packets:
                    wrpcap(pcap_file, captured_packets)
                    print(f"Traffic for {url} recorded in {pcap_file}")
                    self.organize_pcap(pcap_file, url, timestamp)

            self.queue.task_done()
            self.close_browser()  # Close the browser after processing the URL

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("Browser closed.")

    def open_browser(self):
        # Initialize the browser (e.g., Chrome) with GUI
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=ChromeService(), options=options)
        print("Browser opened with GUI.")

    def crawl_for_browsing(self):
        for url in self.urls:
            self.queue.put(url)

        while not self.queue.empty() and self.total_links < self.max_links:
            url = self.queue.get()
            if url in self.visited:
                self.queue.task_done()
                continue

            print(f"Crawling: {url}")
            self.visited.add(url)
            self.total_links += 1

            print(f"Applying network conditions and starting traffic capture for {url}")
            self.apply_random_network_conditions()

            unique_identifier = f"{self.total_links}_{int(time.time())}"

            self.start_capture(unique_identifier)
            content = self.fetch_content(url)
            if content:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                pcap_file = f"web_traffic_{self.total_links}_{timestamp}_{unique_identifier}.pcap"

                # Save browser log
                log_file = f"browser_log_{self.total_links}_{timestamp}_{unique_identifier}.txt"
                self.save_browser_log(log_file)
                print(f"Browser log for {url} saved in {log_file}")

                directory = os.path.dirname(pcap_file)

                # Step 2: Construct the new file path
                log_file = os.path.join(directory, log_file)

                time.sleep(30)
                captured_packets = self.stop_capture()
                if captured_packets:
                    wrpcap(pcap_file, captured_packets)
                    print(f"Traffic for {url} recorded in {pcap_file}")
                    self.organize_pcap(pcap_file, url, timestamp)
                else:
                    print(f"No packets captured for {url}")

                links = self.extract_links(content, url)
                for link in links:
                    if link not in self.visited:
                        self.queue.put(link)
                self.crawled_links.update(links)

            self.queue.task_done()

    def crawl_for_video(self):
        for url in self.urls:
            self.queue.put(url)

        while not self.queue.empty() and self.total_links < self.max_links:
            url = self.queue.get()
            if url in self.visited:
                self.queue.task_done()
                continue

            print(f"Crawling: {url}")
            self.visited.add(url)
            self.total_links += 1

            # Apply network conditions before initiating the traffic capture.
            print(f"Applying network conditions for {url}")
            self.apply_random_network_conditions()

            # Start capturing traffic right before loading the URL
            unique_identifier = f"{self.total_links}_{int(time.time())}"
            print(f"Starting traffic capture for {url}")
            self.start_capture(unique_identifier)

            # Fetch content after starting the capture
            content = self.fetch_content(url)

            if content:
                # If content is successfully fetched, play videos if any
                self.play_videos(url)

                # Wait for a specific duration while the video plays and traffic is captured
                print("Waiting 60 seconds to capture traffic while the video plays...")
                time.sleep(60)  # Delay for 60 seconds to allow video streaming data capture

            # Stop the capture after the wait
            captured_packets = self.stop_capture()

            if captured_packets:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                pcap_file = f"web_traffic_{self.total_links}_{timestamp}_{unique_identifier}.pcap"

                # Save browser log
                log_file = f"browser_log_{self.total_links}_{timestamp}_{unique_identifier}.txt"
                self.save_browser_log(log_file)
                print(f"Browser log for {url} saved in {log_file}")

                wrpcap(pcap_file, captured_packets)
                print(f"Traffic for {url} recorded in {pcap_file}")
                self.organize_pcap(pcap_file, url, timestamp)
            else:
                print("No packets captured for {url}")

            links = self.extract_links(content, url)
            for link in links:
                if link not in self.visited:
                    self.queue.put(link)
            self.crawled_links.update(links)

            self.queue.task_done()

    def start_capture(self, unique_identifier):
        # Get the IP address of the current machine
        local_ip = get_if_addr(conf.iface)

        # Set up a BPF filter to capture traffic only to and from the local machine
        filter_str = f"host {local_ip}"

        # Initialize and start the sniffer with the specified filter
        self.sniffer = AsyncSniffer(filter=filter_str)
        self.sniffer.start()
        print(f"Started sniffing traffic for {unique_identifier} on IP {local_ip}")

    def stop_capture(self):
        # Implement stopping of traffic capture and return captured packets
        self.sniffer.stop()
        captured_packets = self.sniffer.results  # Access the results property
        return captured_packets

if __name__ == "__main__":
    # Load URLs from a JSON file
    with open('download_links.json', 'r') as file:
        urls = json.load(file)

    operation = 'video'
    max_links = 100  # Adjust this number as needed


    crawler = WebCrawler(urls, operation, max_links, headless=False)
    crawler.start_crawling(operation)



