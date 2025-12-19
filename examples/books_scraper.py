"""
Books to Scrape - Web Scraping Example
=======================================
This script demonstrates web scraping using requests and BeautifulSoup
on books.toscrape.com - a website specifically designed for scraping practice.

Author: Akhilesh Talekar
Date: December 2024
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/page-{}.html"

# Headers to mimic a real browser request
# This helps avoid being blocked by websites that detect bot traffic
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Rating word to number mapping
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Delay between requests (in seconds) - BE RESPECTFUL!
REQUEST_DELAY = 1


# =============================================================================
# SCRAPING FUNCTIONS
# =============================================================================

def get_page(url):
    """
    Fetch a page and return BeautifulSoup object.
    
    Args:
        url (str): The URL to fetch
        
    Returns:
        BeautifulSoup: Parsed HTML content or None if failed
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_book_data(book_element):
    """
    Extract data from a single book element.
    
    Args:
        book_element: BeautifulSoup element representing a book
        
    Returns:
        dict: Dictionary containing book data
    """
    # Extract title (from the 'title' attribute of the anchor tag)
    title_element = book_element.find("h3").find("a")
    title = title_element.get("title", "Unknown Title")
    
    # Extract price (remove currency symbol and convert to float)
    price_element = book_element.find("p", class_="price_color")
    price_text = price_element.text.strip() if price_element else "£0.00"
    price = float(price_text.replace("£", "").replace("Â", ""))
    
    # Extract rating (from class name like "star-rating Three")
    rating_element = book_element.find("p", class_="star-rating")
    rating_class = rating_element.get("class", ["star-rating", "Zero"])
    rating_word = rating_class[1] if len(rating_class) > 1 else "Zero"
    rating = RATING_MAP.get(rating_word, 0)
    
    # Extract availability
    availability_element = book_element.find("p", class_="instock")
    availability = "In Stock" if availability_element else "Out of Stock"
    
    # Extract book URL for potential further scraping
    book_url = BASE_URL + "catalogue/" + title_element.get("href", "").replace("../", "")
    
    return {
        "Title": title,
        "Price (£)": price,
        "Rating": rating,
        "Availability": availability,
        "URL": book_url
    }


def scrape_page(page_number):
    """
    Scrape all books from a single page.
    
    Args:
        page_number (int): Page number to scrape
        
    Returns:
        list: List of book dictionaries
    """
    if page_number == 1:
        url = BASE_URL
    else:
        url = CATALOGUE_URL.format(page_number)
    
    print(f"Scraping page {page_number}: {url}")
    
    soup = get_page(url)
    if not soup:
        return []
    
    # Find all book articles on the page
    books = soup.find_all("article", class_="product_pod")
    
    return [extract_book_data(book) for book in books]


def scrape_all_books(max_pages=5):
    """
    Scrape books from multiple pages.
    
    Args:
        max_pages (int): Maximum number of pages to scrape
        
    Returns:
        list: List of all book dictionaries
    """
    all_books = []
    
    for page in range(1, max_pages + 1):
        books = scrape_page(page)
        all_books.extend(books)
        
        print(f"  Found {len(books)} books on page {page}")
        
        # Respectful delay between requests
        if page < max_pages:
            time.sleep(REQUEST_DELAY)
    
    return all_books


# =============================================================================
# DATA PROCESSING & EXPORT
# =============================================================================

def create_dataframe(books_data):
    """
    Create a pandas DataFrame from books data.
    
    Args:
        books_data (list): List of book dictionaries
        
    Returns:
        pd.DataFrame: DataFrame with book data
    """
    df = pd.DataFrame(books_data)
    
    # Sort by rating (descending) then by price (ascending)
    df = df.sort_values(by=["Rating", "Price (£)"], ascending=[False, True])
    
    return df


def save_to_csv(df, filename):
    """Save DataFrame to CSV file."""
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Data saved to {filename}")


def save_to_excel(df, filename):
    """Save DataFrame to Excel file."""
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"Data saved to {filename}")


def display_summary(df):
    """Display summary statistics of the scraped data."""
    print("\n" + "=" * 50)
    print("SCRAPING SUMMARY")
    print("=" * 50)
    print(f"Total books scraped: {len(df)}")
    print(f"Average price: £{df['Price (£)'].mean():.2f}")
    print(f"Price range: £{df['Price (£)'].min():.2f} - £{df['Price (£)'].max():.2f}")
    print(f"Average rating: {df['Rating'].mean():.2f} stars")
    print("\nRating distribution:")
    print(df['Rating'].value_counts().sort_index(ascending=False))
    print("\nTop 5 highest-rated affordable books:")
    top_books = df.head(5)[["Title", "Price (£)", "Rating"]]
    print(top_books.to_string(index=False))


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to run the scraper."""
    print("=" * 50)
    print("BOOKS TO SCRAPE - Web Scraping Demo")
    print("=" * 50)
    print(f"Target: {BASE_URL}")
    print("This is a practice website designed for learning web scraping.")
    print("=" * 50 + "\n")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Scrape books (limiting to 3 pages for demo)
    print("Starting scraping process...\n")
    books_data = scrape_all_books(max_pages=3)
    
    if not books_data:
        print("No data scraped. Please check your internet connection.")
        return
    
    # Create DataFrame
    df = create_dataframe(books_data)
    
    # Display summary
    display_summary(df)
    
    # Save to files
    print("\n" + "=" * 50)
    print("SAVING DATA")
    print("=" * 50)
    
    csv_path = os.path.join(output_dir, "books_data.csv")
    excel_path = os.path.join(output_dir, "books_data.xlsx")
    
    save_to_csv(df, csv_path)
    save_to_excel(df, excel_path)
    
    print("\n✅ Scraping completed successfully!")
    print(f"Output files are in: {output_dir}")


if __name__ == "__main__":
    main()
