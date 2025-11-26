import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class FlipkartScraper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # ---------------- REVIEWS ----------------
    def get_top_reviews(self, product_url, count=2):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options, use_subprocess=True)

        try:
            driver.get(product_url)
            time.sleep(5)

            # Close login popup
            try:
                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
                time.sleep(1)
            except:
                pass

            # Scroll to load Ratings & Reviews
            for _ in range(6):
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(1.2)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            reviews = []
            seen = set()

            review_cards = soup.select("div.xgU6qg div.mlW33x")

            for card in review_cards:
                text_div = card.select_one("div.G4PxIA div div")
                if not text_div:
                    continue

                text = text_div.get_text(" ", strip=True)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)

                if len(reviews) >= count:
                    break

        except Exception:
            reviews = []

        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"


    # ---------------- PRODUCTS ----------------
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, use_subprocess=True)

        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(5)

        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = []

        cards = soup.select("div[data-id]")

        for card in cards:
            if len(products) >= max_products:
                break

            try:
                # ---- LINK & ID ----
                a_tag = card.select_one("a[href]")
                if not a_tag:
                    continue

                href = a_tag["href"]
                product_link = (
                    href if href.startswith("http")
                    else "https://www.flipkart.com" + href
                )

                pid_match = re.search(r"pid=([A-Z0-9]+)", product_link)
                product_id = pid_match.group(1) if pid_match else "N/A"

                # ---- TITLE ----
                title = a_tag.get_text(" ", strip=True)

                # ---- PRICE ----
                price_div = card.find("div", string=re.compile("₹"))
                price = price_div.get_text(strip=True) if price_div else "N/A"

                # ---- RATING ----
                rating_div = card.select_one("div.XQDdHH")
                rating = rating_div.get_text(strip=True) if rating_div else "N/A"

                # ---- REVIEW COUNT ----
                review_span = card.find("span", string=re.compile("Reviews"))
                if review_span:
                    match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", review_span.text)
                    total_reviews = match.group(0) if match else "N/A"
                else:
                    total_reviews = "N/A"

                # ---- REVIEWS ----
                top_reviews = self.get_top_reviews(
                    product_link,
                    count=review_count
                )

                products.append([
                    product_id,
                    title,
                    rating,
                    total_reviews,
                    price,
                    top_reviews
                ])

            except Exception as e:
                print(f"Skipped product due to error: {e}")
                continue

        driver.quit()
        return products

    # ---------------- CSV ----------------
    def save_to_csv(self, data, filename="product_reviews.csv"):
        path = r"E:\LLMOps\ecommerce-product-assistant\data\product_reviews.csv"
        # path = filename if os.path.isabs(filename) else os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "product_id",
                "product_title",
                "rating",
                "total_reviews",
                "price",
                "top_reviews"
            ])
            writer.writerows(data)
