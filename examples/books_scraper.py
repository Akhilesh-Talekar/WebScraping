"""
Books to Scrape - Web Scraping Example
Scraping book data from books.toscrape.com

Author: Akhilesh Talekar
Date: December 2024
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Using headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Fetch the webpage
url = "https://books.toscrape.com/"
response = requests.get(url, headers=headers)

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Find all book articles on the page
articles = soup.find_all("article", class_="product_pod")

items = []

for article in articles:
    # Get book title
    book_name = article.find("h3").find("a").get("title")
    
    # Get book price
    price_div = article.find("div", class_="product_price")
    book_price = price_div.find("p", class_="price_color").text.split("£")[1]
    
    # Get book rating
    book_rating = article.find("p", class_="star-rating").text
    
    items.append({
        "Title": book_name,
        "Price": float(book_price),
        "Rating": book_rating
    })

print(f"Total books extracted: {len(items)}\n")

# Create DataFrame
df = pd.DataFrame(items)
print(df.head(10))

# Export to CSV and Excel
df.to_csv("books_data.csv", index=False)
df.to_excel("books_data.xlsx", index=False)

print("\n✅ Scraping completed!")
