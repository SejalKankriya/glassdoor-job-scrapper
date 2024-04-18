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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"


def setup_driver():
    """Setup the Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'user-agent={USER_AGENT}')
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.glassdoor.com/Job/index.htm")

    return driver


def handle_popups_if_present(driver):
    """Attempt to close any popups that are found."""
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "CloseButton"))).click()
        logging.info("Popup closed.")
    except TimeoutException:
        logging.info("No popup was found.")


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
            logging.warning("Load more button not found or not clickable.")
            break


def scrape_jobs(driver):
    """Scrape job data from the page."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jobs = soup.find_all('li', class_='JobsList_jobListItem__wjTHv')
    return [extract_job_data(job) for job in jobs if job]


def extract_job_data(job):
    """Extract and return job data from a BeautifulSoup tag."""
    try:
        job_title_tag = job.select_one('.JobCard_jobTitle___7I6y')
        company_tag = job.select_one(
            '.EmployerProfile_compactEmployerName__LE242')
        location_tag = job.select_one('.JobCard_location__rCz3x')
        apply_link_tag = job.select_one('.JobCard_trackingLink__GrRYn')
        salary_tag = job.find('div', class_='JobCard_salaryEstimate__arV5J')

        return {
            "Job Title": job_title_tag.get_text(strip=True) if job_title_tag else "N/A",
            "Company": company_tag.get_text(strip=True) if company_tag else "N/A",
            "Location": location_tag.get_text(strip=True) if location_tag else "N/A",
            "Apply Link": f"https://www.glassdoor.com{apply_link_tag['href']}" if apply_link_tag else "N/A",
            "Salary": extract_salary(salary_tag)
        }

    except Exception as e:
        logging.error("Failed to extract job data: %s", e)
        return None


def extract_salary(salary_tag):
    """Extract and clean the salary data from a salary_tag."""
    if salary_tag:
        salary_text = salary_tag.text.strip()
        if "Employer est." in salary_text:
            salary_text = salary_text.replace("(Employer est.)", "").strip()
            salary_text = salary_text.split(" (")[0]
        return salary_text
    else:
        return "N/A"


def save_to_csv(job_data, filename):
    """Save the scraped job data to a CSV file."""
    df = pd.DataFrame(job_data)
    df = df[['Job Title', 'Company', 'Location', 'Salary', 'Apply Link']]
    df.to_csv(filename, index=False, encoding='utf-8')
    logging.info("Data saved to %s", filename)


def main():
    driver = setup_driver()
    try:
        login_to_glassdoor(driver, "Data Scientist", "New York, United States")
        load_more_jobs(driver)
        job_data = scrape_jobs(driver)
        save_to_csv(job_data, "glassdoor_jobs.csv")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
