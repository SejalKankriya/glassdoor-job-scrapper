import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver():
    """Setup the Chrome WebDriver."""
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.glassdoor.com/Job/index.htm")
    driver.maximize_window()
    return driver

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
    for _ in range(num_clicks):
        try:
            button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="load-more"]')))
            button.click()
            time.sleep(5)  # Wait for more jobs to load
        except TimeoutException:
            print("Load more button not found or not clickable.")
            break

def scrape_jobs(driver):
    """Scrape job data from the page."""
    job_data = []
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
    with open(filename, "w", newline='', encoding='utf-8') as file:
        fieldnames = ["Job Title", "Company", "Location", "Salary", "Apply Link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for job in job_data:
            writer.writerow(job)

def main():
    job_title = "data scientist"
    location = "united states"
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
