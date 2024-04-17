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

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
def setup_driver():
    """Setup the Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-gpu") # Disable GPU hardware acceleration
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
    chrome_options.add_argument(f'user-agent={USER_AGENT}')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.glassdoor.com/Job/index.htm")

    return driver

def handle_popups_if_present(driver):
    """Closes the sign-up/login popup if it appears."""
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "CloseButton"))).click()
        print("Popup closed.")
    except TimeoutException:
        print("No popup was found.")

def login_to_glassdoor(driver, job_title, location):
    """Log into Glassdoor and perform initial job search."""
    search = driver.find_element(
        By.CSS_SELECTOR, '[class="Autocomplete_autocompleteInput__Ngcdi Autocomplete_roundLeftBorder__NBhQ9"]')
    loc = driver.find_element(
        By.CSS_SELECTOR, '[class="Autocomplete_autocompleteInput__Ngcdi Autocomplete_roundRightBorder__OybBh"]')
    search.send_keys(job_title)
    loc.send_keys(location)
    search.send_keys(Keys.ENTER)
    time.sleep(5)

def load_more_jobs(driver, num_clicks=10):
    """Load more jobs by clicking the 'Load More' button multiple times."""
    popup_closed = False
    for _ in range(num_clicks):
        try:
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-test="load-more"]')))
            button.click()
            time.sleep(2)

            if not popup_closed:
                handle_popups_if_present(driver)
                popup_closed = True

            time.sleep(3)
        except TimeoutException:
            print("Load more button not found or not clickable.")
            break

def scrape_jobs(driver):
    """Scrape job data from the page."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jobs = soup.find_all('li', class_='JobsList_jobListItem__wjTHv')
    return [extract_job_data(job) for job in jobs if job]


def extract_job_data(job, base_url="https://www.glassdoor.com"):
    """Extract data from a single job listing using BeautifulSoup."""
    data = {}
    try:
        job_title_tag = job.select_one('.JobCard_jobTitle___7I6y')
        data['Job Title'] = job_title_tag.get_text(strip=True) if job_title_tag else "N/A"

        company_tag = job.select_one('.EmployerProfile_compactEmployerName__LE242')
        data['Company'] = company_tag.get_text(strip=True) if company_tag else "N/A"

        location_tag = job.select_one('.JobCard_location__rCz3x')
        data['Location'] = location_tag.get_text(strip=True) if location_tag else "N/A"

        apply_link_tag = job.select_one('.JobCard_trackingLink__GrRYn')
        relative_link = apply_link_tag['href'] if apply_link_tag and 'href' in apply_link_tag.attrs else "N/A"
        data['Apply Link'] = base_url + relative_link if relative_link.startswith("/partner") else relative_link

        # Extract salary, clean up unwanted text
        salary_tag = job.find('div', class_='JobCard_salaryEstimate__arV5J')
        if salary_tag:
            salary_text = salary_tag.text.strip()
            if "Employer est." in salary_text:
                salary_text = salary_text.replace("(Employer est.)", "").strip()
            data['Salary'] = salary_text.split(" (")[0]
        else:
            data['Salary'] = "N/A"

    except AttributeError as e:
        print(f"An error occurred while parsing job data: {e}")
        return None  # Return None if any essential data is missing or an error occurs

    return data

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
