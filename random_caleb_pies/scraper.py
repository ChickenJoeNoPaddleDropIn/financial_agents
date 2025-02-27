from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup

def scrape_forex_factory_with_selenium():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.forexfactory.com/calendar")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    events = []
    for row in soup.select(".calendar__row"):
        try:
            date = row.get("data-eventtimestamp", "N/A")
            time = row.select_one(".calendar__time")
            currency = row.select_one(".calendar__currency")
            impact = row.select_one(".calendar__impact")
            event = row.select_one(".calendar__event")
            actual = row.select_one(".calendar__actual")
            forecast = row.select_one(".calendar__forecast")
            previous = row.select_one(".calendar__previous")

            event_data = {
                "Date": date,
                "Time": time.text.strip() if time else "N/A",
                "Currency": currency.text.strip() if currency else "N/A",
                "Impact": impact.get("title", "N/A") if impact else "N/A",
                "Event": event.text.strip() if event else "N/A",
                "Actual": actual.text.strip() if actual else "N/A",
                "Forecast": forecast.text.strip() if forecast else "N/A",
                "Previous": previous.text.strip() if previous else "N/A",
            }
            events.append(event_data)
        except Exception as e:
            print(f"Error parsing row: {e}")

    return pd.DataFrame(events)

if __name__ == "__main__":
    df = scrape_forex_factory_with_selenium()
    print(df)
