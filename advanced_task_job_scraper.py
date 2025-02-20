import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_jobs():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
    
    driver = uc.Chrome(options=options)
    driver.get("https://www.indeed.com/")
    
    wait = WebDriverWait(driver, 30)
    time.sleep(5)  # Wait for the page to load
    
    # Ensure the page is fully loaded
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Search for Python Developer jobs in Remote location
    try:
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']")))
        search_box.clear()
        search_box.send_keys("Python Developer")
    except Exception as e:
        print("Search box not found! Error:", e)
        driver.quit()
        return
    
    try:
        location_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='l']")))
        location_box.clear()
        location_box.send_keys("Remote")
        location_box.send_keys(Keys.RETURN)
    except Exception as e:
        print("Location box not found! Error:", e)
        driver.quit()
        return
    
    time.sleep(5)  # Wait for job listings to load
    
    jobs_data = []
    page_count = 0
    max_pages = 5  # Limit to 5 pages
    
    while page_count < max_pages:
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
        if not job_cards:
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.cardOutline")  # Alternative selector
        
        print(f"📄 Scraping page {page_count + 1}... Found {len(job_cards)} jobs.")
        
        for job in job_cards:
            title = job.find_element(By.CSS_SELECTOR, "h2.jobTitle").text if job.find_elements(By.CSS_SELECTOR, "h2.jobTitle") else "Title not available"
            company = job.find_element(By.CLASS_NAME, "companyName").text if job.find_elements(By.CLASS_NAME, "companyName") else "Company not available"
            location = job.find_element(By.CLASS_NAME, "companyLocation").text if job.find_elements(By.CLASS_NAME, "companyLocation") else "Location not available"
            date_posted = job.find_element(By.CLASS_NAME, "date").text if job.find_elements(By.CLASS_NAME, "date") else "Date not available"
            preview = job.find_element(By.CLASS_NAME, "job-snippet").text if job.find_elements(By.CLASS_NAME, "job-snippet") else "Description not available"
            job_link = job.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href") if job.find_elements(By.CSS_SELECTOR, "h2 a") else "No link available"

            jobs_data.append({
                "title": title,
                "company": company,
                "location": location,
                "date_posted": date_posted,
                "preview": preview,
                "job_link": job_link
            })
        
        # Pagination handling
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")
            driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript to avoid interception issues
            page_count += 1
            time.sleep(5)
        except:
            print("No more pages or pagination not found.")
            break
    
    driver.quit()
    
    # Save to JSON file
    with open("job_listings.json", "w") as f:
        json.dump(jobs_data, f, indent=4)
    
    print(f"✅ Scraping complete! {len(jobs_data)} jobs saved to job_listings.json 🎯")

if __name__ == "__main__":
    scrape_jobs()