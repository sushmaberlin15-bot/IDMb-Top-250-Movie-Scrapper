from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time

print(" Starting browser...")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get("https://www.imdb.com/chart/top/")

    time.sleep(20)

    if "human verification" in driver.title.lower():
        input("Complete IMDb's verification in Chrome, then press Enter here...")
        

    movie_selector = "li.ipc-metadata-list-summary-item"
    WebDriverWait(driver, 60).until(
        lambda browser: len(browser.find_elements(By.CSS_SELECTOR, movie_selector)) >= 250
    )

    print(" Page loaded")

    movies = driver.find_elements(By.CSS_SELECTOR, movie_selector)
    print("Movies found:", len(movies))

    data = []
    for i, movie in enumerate(movies, start=1):
        title_elements = movie.find_elements(By.CSS_SELECTOR, "h3, a[href*='/title/']")
        title = next((element.text.strip() for element in title_elements if element.text.strip()), "")
        if not title:
            title = next(
                (element.get_attribute("aria-label") for element in title_elements if element.get_attribute("aria-label")),
                "",
            )
        if not title:
            raise RuntimeError(f"IMDb row {i} has no title; CSV was not changed.")

        rating_elements = movie.find_elements(By.CLASS_NAME, "ipc-rating-star--rating")
        if not rating_elements:
            raise RuntimeError(f"IMDb row {i} has no rating; CSV was not changed.")
        rating = rating_elements[0].text
        data.append([i, title, rating])

    if len(data) != 250:
        raise RuntimeError(f"Expected 250 movies, collected {len(data)}; CSV was not changed.")

    df = pd.DataFrame(data, columns=["Rank", "Title", "Rating"])
    df.to_csv("imdb_top_250.csv", index=False)

    print(" CSV created successfully!")
finally:
    driver.quit()