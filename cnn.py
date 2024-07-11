import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the WebDriver (using Chrome in this example)
driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH or specify its location

try:
    # Open the desired webpage
    driver.get("https://www.israelhayom.co.il/podcasts/article/15800076")  # Replace with the URL of your target page
    # //*[@id="video_0_gheQ6rW1NPoEqbSogl_ttXuxaBzv1qbT1P4rYM2"]/button
    time.sleep(6)

    # Wait for the element to be present in the DOM
    # element = WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.XPATH, "//*[contains(text() , '@id=video_undefined_' ]/button"))
    # )                                              #//*[@id="video_undefined_1cOokOkVre5QQ6NxanvC"]/button

    element = driver.find_element(By.XPATH, "//*[contains(@id, 'video_')]/button")
    element.click()
    print("Element found and clicked.")

   # print("Element found and double-clicked.")
    time.sleep(20)
    # Optional: Perform additional actions or wait for results
    # ...

finally:
    # Close the browser
    driver.quit()
