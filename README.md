# Glassdoor Job Scrapper
This project provides a tool for scraping job listings from Glassdoor using Python and Selenium. It automates the process of fetching job data including titles, companies, locations, and salaries, making it easier to analyze the job market or to find job opportunities automatically.

<img src="https://github.com/SejalKankriya/glassdoor-job-scrapper/assets/43418191/45ddf83b-eed1-4c9f-97dc-1d5b64401b6c" width="60%" height="60%">

## Features

- Scrape job listings from Glassdoor based on job title and location.
- Automatically handle pop-ups and web page navigations.
- Save job listings data into a CSV file for easy use and analysis.
- Run in both standard and headless mode for efficient background execution.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6+
- pip

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/glassdoor-job-scraper.git
cd glassdoor-job-scraper
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage
To run the scraper, navigate to the project directory and run:

```bash
python glassdoor_scraper.py
```

## Configuring the Script
Edit the main() function in glassdoor_scraper.py to specify different job titles and locations:

```bash
def main():
    driver = setup_driver()
    try:
        login_to_glassdoor(driver, "Data Scientist", "New York, United States")
        load_more_jobs(driver)
        job_data = scrape_jobs(driver)
        save_to_csv(job_data, "glassdoor_jobs.csv")
    finally:
        driver.quit()
```

## Output
The script will output a CSV file named glassdoor_jobs.csv containing the scraped job listings. Each row represents a different job and includes columns for the job title, company, location, salary, and a link to the job posting.

## License
Distributed under the MIT License.
