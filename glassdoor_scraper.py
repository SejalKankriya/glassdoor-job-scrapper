import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import csv
import time

def setup_driver():
        """Setup the Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        chrome_options.add_argument("--window-size=1920x1080")  # Set the window size
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
    
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.glassdoor.com/Job/index.htm")
        # driver.maximize_window()
        return driver

def handle_popups_if_present(driver):
    """Closes the sign-up/login popup if it appears."""
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "CloseButton")),
            message="Checking for pop-up close button."
        )
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("No popup appeared within the wait time.")
    except NoSuchElementException:
        print("No close button found for the popup.")

def login_to_glassdoor(driver, job_title, location):
    """Log into Glassdoor and perform initial job search."""
    search = driver.find_element(By.CSS_SELECTOR, '[class="Autocomplete_autocompleteInput__Ngcdi Autocomplete_roundLeftBorder__NBhQ9"]')
    loc = driver.find_element(By.CSS_SELECTOR, '[class="Autocomplete_autocompleteInput__Ngcdi Autocomplete_roundRightBorder__OybBh"]')
    search.send_keys(job_title)
    loc.send_keys(location)
    search.send_keys(Keys.ENTER)
    time.sleep(5)  # Wait for results to load

def load_more_jobs(driver, num_clicks=10):
    """Load more jobs by clicking the 'Load More' button multiple times."""
    popup_closed = False
    for _ in range(num_clicks):
        try:
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="load-more"]')))
            button.click()
            time.sleep(2)  # Wait for more jobs to load
            
            if not popup_closed:
                    handle_popups_if_present(driver)
                    popup_closed = True

            time.sleep(3)
        except TimeoutException:
            print("Load more button not found or not clickable.")
            break

def scrape_jobs(driver):
    """Scrape job data from the page."""
    job_data = []
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="JobsList_jobListItem"]')))
    # close_glassdoor_popup(driver)
    job_listings = driver.find_elements(By.CSS_SELECTOR, '[class="JobsList_jobListItem__wjTHv"]')
    for job in job_listings:
        job_data.append(extract_job_data(job))
    return job_data

def extract_job_data(job):
    """Extract data from a single job listing."""
    try:
        job_title = job.find_element(By.CSS_SELECTOR, '[class="JobCard_jobTitle___7I6y"]').text.strip()
        company = job.find_element(By.CSS_SELECTOR, '[class="EmployerProfile_compactEmployerName__LE242"]').text.strip()
        location = job.find_element(By.CSS_SELECTOR, '[class="JobCard_location__rCz3x"]').text.strip()
        apply_link = job.find_element(By.CSS_SELECTOR, '[class="JobCard_trackingLink__GrRYn"]').get_attribute("href")
        salary = job.find_element(By.CLASS_NAME, "JobCard_salaryEstimate__arV5J").text.strip().split(" (")[0]
    except NoSuchElementException:
        salary = "N/A"  # Default to N/A if no salary info is found
    return {
        "Job Title": job_title,
        "Company": company,
        "Location": location,
        "Salary": salary,
        "Apply Link": apply_link,
    }

def save_to_csv(job_data, filename):
    """Save the scraped job data to a CSV file."""
    df = pd.DataFrame(job_data)
    df = df[['Job Title', 'Company', 'Location', 'Salary', 'Apply Link']]
    df.to_csv(filename, index=False, encoding='utf-8')

def main():
    job_title = "Data Scientist"
    location = "New York, United States"
    filename = "glassdoor_jobs.csv"
    driver = setup_driver()
    try:
        login_to_glassdoor(driver, job_title, location)
        load_more_jobs(driver)
        job_data = scrape_jobs(driver)
        save_to_csv(job_data, filename)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
