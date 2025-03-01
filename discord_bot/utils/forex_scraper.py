from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from .forex_cache import ForexEventCache
import time
import re


# Common economic acronyms and their full names
ECONOMIC_ACRONYMS = {
    "CPI": r"(?:Core )?Consumer Price Index|CPI",
    "GDP": r"(?:Prelim )?Gross Domestic Product|GDP",
    "NFP": r"Non-Farm Payrolls|NFP",
    "FOMC": r"Federal Open Market Committee|FOMC",
    "PMI": r"(?:Manufacturing )?Purchasing Managers['\' ]* Index|PMI",
    "PPI": r"(?:Core )?Producer Price Index|PPI",
    "ISM": r"ISM (?:Manufacturing |Non-Manufacturing |Services )?(?:PMI|Index)",
    "BOE": r"Bank of England|BOE",
    "ECB": r"European Central Bank|ECB",
    "BOJ": r"Bank of Japan|BOJ",
    "BOC": r"Bank of Canada|BOC",
    "RBA": r"Reserve Bank of Australia|RBA",
    "RBNZ": r"Reserve Bank of New Zealand|RBNZ",
    "SNB": r"Swiss National Bank|SNB",
    "HPI": r"House Price Index|HPI",
    "PCE": r"(?:Core )?Personal Consumption Expenditure|PCE",
    "HICP": r"Harmonized Index of Consumer Prices|HICP",
    "ADP": r"ADP Non-Farm Employment Change|ADP",
}

def simplify_event_name(event_name):
    """Simplify event names by using acronyms where possible"""
    # First check if the event name is already just an acronym
    if event_name in ECONOMIC_ACRONYMS:
        return event_name
        
    # Check each acronym pattern
    for acronym, pattern in ECONOMIC_ACRONYMS.items():
        if re.search(pattern, event_name, re.IGNORECASE):
            # Special cases for common prefixes
            if any(prefix in event_name.lower() for prefix in ["core ", "prelim ", "final "]):
                prefix = next(p for p in ["Core ", "Prelim ", "Final "] 
                            if p.lower() in event_name.lower())
                return f"{prefix}{acronym}"
            return acronym
            
    # Special case for "Speaks" events
    if "speaks" in event_name.lower():
        name = event_name.split(" Speaks")[0]
        return f"{name} Speaks"
        
    return event_name

# Create a global cache instance
event_cache = ForexEventCache(cache_ttl=3600)  # 1 hour cache


import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys

def scrape_forex_factory():
    """
    Scrapes economic events from ForexFactory for the current month.
    Returns True if successful, False otherwise.
    """
    options = Options()
    # For now, do not run headless (visible browser)
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )

    try:
        print("Initializing Chrome driver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        now = datetime.now()
        month_abbr = now.strftime("%b").lower()  # e.g., 'feb'
        year = now.year
        url = f"https://www.forexfactory.com/calendar?month={month_abbr}.{year}"
        print(f"\nScraping calendar: {url}")
        
        driver.get(url)
        
        # Simulated scrolling using PAGE_DOWN keys to mimic user scrolling
        body = driver.find_element(By.TAG_NAME, "body")
        prev_scroll = 0
        while True:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)  # allow content to load
            curr_scroll = driver.execute_script("return window.pageYOffset;")
            if curr_scroll == prev_scroll:
                break
            prev_scroll = curr_scroll
        
        # Wait until the calendar table is loaded
        wait = WebDriverWait(driver, 10)
        calendar_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "calendar__table")))
        # Uncomment below to inspect full HTML if needed:
        # print(calendar_table.get_attribute("outerHTML"))

        month_data = {}
        current_date = None
        
        rows = calendar_table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            classes = row.get_attribute("class").split()
            
            # Process date rows
            if "calendar__row--day-breaker" in classes:
                try:
                    td = row.find_element(By.TAG_NAME, "td")
                    td_text = td.get_attribute("textContent").strip()  # e.g., "Thu Feb 6"
                    print("Day-breaker td text:", td_text)
                    match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}", td_text, re.IGNORECASE)
                    if match:
                        date_str = match.group(0)  # e.g., "Feb 6"
                        current_date = datetime.strptime(f"{date_str} {year}", "%b %d %Y").strftime("%Y-%m-%d")
                        month_data[current_date] = []
                        print(f"\nFound new date: {current_date}")
                    else:
                        print("No valid date found in day-breaker row from td text.")
                except Exception as e:
                    print("Error processing date row:", e)
                continue  # Skip processing the day-breaker row

            # Process event rows (only if current_date is set)
            if current_date and row.get_attribute("data-event-id"):
                try:
                    event = {}
                    
                    # Extract time
                    try:
                        time_cell = row.find_element(By.CLASS_NAME, "calendar__time")
                        time_divs = time_cell.find_elements(By.TAG_NAME, "div")
                        if time_divs:
                            time_text = time_divs[0].text.strip()
                        else:
                            time_text = time_cell.text.strip()
                        event['time'] = time_text if time_text else "All Day"
                    except Exception:
                        event['time'] = "All Day"

                    # Extract currency
                    try:
                        currency_cell = row.find_element(By.CLASS_NAME, "calendar__currency")
                        event['currency'] = currency_cell.text.strip()
                    except Exception:
                        event['currency'] = ""

                    # Extract event name (using your simplify_event_name function)
                    try:
                        event_cell = row.find_element(By.CLASS_NAME, "calendar__event")
                        titles = event_cell.find_elements(By.CLASS_NAME, "calendar__event-title")
                        if titles:
                            event_name = titles[0].text.strip()
                        else:
                            event_name = event_cell.text.strip()
                        event['event'] = simplify_event_name(event_name)
                    except Exception:
                        event['event'] = ""
                    
                    # Extract importance
                    try:
                        impact_cell = row.find_element(By.CLASS_NAME, "calendar__impact")
                        icons = impact_cell.find_elements(By.TAG_NAME, "span")
                        if icons:
                            impact_class = icons[0].get_attribute("class")
                        else:
                            impact_class = impact_cell.text.strip()
                        if "ff-impact-red" in impact_class:
                            event['importance'] = "High"
                        elif "ff-impact-ora" in impact_class:
                            event['importance'] = "Medium"
                        elif "ff-impact-yel" in impact_class:
                            event['importance'] = "Low"
                        else:
                            event['importance'] = "Non-Economic"
                    except Exception:
                        event['importance'] = "Unknown"

                    month_data[current_date].append(event)
                    print(f"Added event on {current_date}: {event}")
                except Exception as e:
                    print(f"Error processing event row: {e}")
                    continue
            elif row.get_attribute("data-event-id"):
                print("Event row encountered before any valid date was set.")
                    
        print(f"\nTotal dates processed: {len(month_data)}")
        # Update the cache with the new data.
        event_cache.month_data = month_data
        return True

    except Exception as e:
        print(f"Error in scraping: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            driver.quit()
        except Exception:
            pass
