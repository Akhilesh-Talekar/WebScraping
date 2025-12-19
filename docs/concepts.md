# Web Scraping Concepts - Deep Dive

This document provides detailed explanations of key web scraping concepts and technologies.

---

## 📡 HTTP Protocol Deep Dive

### What is HTTP?

**HTTP (HyperText Transfer Protocol)** is the foundation of data communication on the web. It's a request-response protocol where a client (browser/scraper) sends requests to a server, which responds with the requested content.

### HTTP vs HTTPS

| Feature | HTTP | HTTPS |
|---------|------|-------|
| **Security** | Unencrypted | Encrypted (TLS/SSL) |
| **Port** | 80 | 443 |
| **URL Prefix** | `http://` | `https://` |
| **Use Case** | Legacy systems | Modern web (preferred) |

### Anatomy of an HTTP Request

```
GET /books/page-1.html HTTP/1.1
Host: books.toscrape.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: text/html,application/xhtml+xml
Accept-Language: en-US,en;q=0.9
Connection: keep-alive
Cookie: session_id=abc123
```

**Components:**
1. **Request Line**: Method + Path + HTTP Version
2. **Headers**: Metadata about the request
3. **Body**: Data sent with POST/PUT requests (optional)

### Anatomy of an HTTP Response

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 15234
Server: nginx
Date: Thu, 19 Dec 2024 10:30:00 GMT
Set-Cookie: visitor_id=xyz789

<!DOCTYPE html>
<html>...
```

**Components:**
1. **Status Line**: HTTP Version + Status Code + Status Message
2. **Headers**: Metadata about the response
3. **Body**: The actual content (HTML, JSON, etc.)

### Important Status Codes for Scrapers

| Code | Meaning | Scraper Action |
|------|---------|----------------|
| **200** | Success | Process the response |
| **301/302** | Redirect | Follow the redirect |
| **400** | Bad Request | Fix request format |
| **403** | Forbidden | Check if blocked |
| **404** | Not Found | Skip this URL |
| **429** | Rate Limited | Slow down requests |
| **500** | Server Error | Retry later |
| **503** | Service Unavailable | Wait and retry |

---

## 🌲 DOM (Document Object Model)

### What is the DOM?

The DOM is a programming interface that represents an HTML document as a tree structure. Each element, attribute, and piece of text becomes a **node** in this tree.

### Types of DOM Nodes

| Node Type | Description | Example |
|-----------|-------------|---------|
| **Document** | Root of the tree | `document` |
| **Element** | HTML tags | `<div>`, `<p>`, `<a>` |
| **Attribute** | Tag attributes | `class="header"` |
| **Text** | Text content | "Hello World" |
| **Comment** | HTML comments | `<!-- comment -->` |

### DOM Navigation

```
Parent-Child Relationships:
┌─────────────────────────────────────┐
│              <html>                 │  ← Root Element
│         ┌──────┴──────┐             │
│       <head>        <body>          │  ← Children of html
│         │             │             │
│      <title>        <div>           │  ← Grandchildren
│         │         ┌──┴──┐           │
│       "Text"    <h1>   <p>          │  ← Great-grandchildren
└─────────────────────────────────────┘
```

### CSS Selectors for Scraping

```python
# BeautifulSoup selector examples

# By tag name
soup.find('div')
soup.find_all('p')

# By class
soup.find(class_='product-title')
soup.find_all('div', class_='item')

# By ID
soup.find(id='main-content')

# By attribute
soup.find('a', href=True)
soup.find('input', {'type': 'text'})

# CSS selectors
soup.select('div.container > p.text')
soup.select('ul li:first-child')
soup.select('[data-id="123"]')

# Nested navigation
soup.find('div', class_='container').find('p')
```

---

## ⚙️ JavaScript Rendering

### The Problem

Many modern websites use JavaScript to load content dynamically. When you request a page with `requests`, you only get the initial HTML - not the content loaded by JavaScript.

### Static HTML Example

```html
<!-- What the server sends -->
<div class="products">
  <div class="product">Book 1 - $10</div>
  <div class="product">Book 2 - $15</div>
</div>
```

### Dynamic (JavaScript) Example

```html
<!-- What the server sends -->
<div class="products" id="product-container">
  <!-- Products loaded by JavaScript -->
</div>

<script>
  fetch('/api/products')
    .then(response => response.json())
    .then(data => {
      // Inject products into the page
      document.getElementById('product-container').innerHTML = 
        data.map(p => `<div>${p.name} - $${p.price}</div>`).join('');
    });
</script>
```

### Solutions

#### 1. Selenium WebDriver (Browser Automation)

Selenium controls a real browser, executing JavaScript just like a human user.

**How it works:**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Python    │ ──► │  Selenium   │ ──► │   Chrome    │
│   Script    │     │  WebDriver  │     │   Browser   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │   Website   │
                                        │   (Server)  │
                                        └─────────────┘
```

**Capabilities:**
- Execute JavaScript
- Click buttons
- Fill forms
- Scroll pages
- Handle pop-ups
- Wait for elements to load

#### 2. Finding Hidden APIs

Often, JavaScript fetches data from an API. You can call this API directly!

**Steps:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by XHR/Fetch
4. Reload the page
5. Find the API call
6. Copy the request and use it in Python

---

## 🔐 Security Elements

### CAPTCHA Types

#### 1. Text CAPTCHA
```
┌─────────────────────────┐
│   7 X k 2 F             │  ← Distorted text
│                         │
│   [_______________]     │  ← User input
└─────────────────────────┘
```

#### 2. Image CAPTCHA (reCAPTCHA v2)
```
┌─────────────────────────────────┐
│ Select all images with          │
│ TRAFFIC LIGHTS                  │
│ ┌─────┬─────┬─────┐             │
│ │ 🚗  │ 🚦  │ 🌳  │             │
│ ├─────┼─────┼─────┤             │
│ │ 🚦  │ 🏠  │ 🚦  │             │
│ ├─────┼─────┼─────┤             │
│ │ 🚶  │ 🚗  │ 🚦  │             │
│ └─────┴─────┴─────┘             │
│          [VERIFY]               │
└─────────────────────────────────┘
```

#### 3. reCAPTCHA v3 (Invisible)
- No user interaction required
- Monitors user behavior
- Assigns a score (0.0 - 1.0)
- Low scores trigger additional verification

### IP Blocking

**Why IPs Get Blocked:**
- Too many requests in short time
- Accessing restricted areas
- Pattern matching (bot behavior)
- Geographic restrictions

**Detection Methods:**
```
Request Pattern Analysis:
├── Request frequency (requests/minute)
├── Request timing (too regular = bot)
├── Request distribution (normal users vary)
└── Access patterns (unusual page sequences)
```

**Mitigation:**
```python
import time
import random

# Add random delays
delay = random.uniform(1, 3)  # 1-3 seconds
time.sleep(delay)

# Use rotating proxies (conceptual)
proxies = [
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
]
```

### User-Agent Rotation

Different browsers have different User-Agent strings:

```python
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

import random
headers = {"User-Agent": random.choice(USER_AGENTS)}
```

### Session Management

```python
import requests

# Using a session maintains cookies across requests
session = requests.Session()

# Login
login_data = {"username": "user", "password": "pass"}
session.post("https://example.com/login", data=login_data)

# Subsequent requests use the session cookies
response = session.get("https://example.com/protected-page")
```

---

## 📋 robots.txt Reference

### Reading robots.txt

Every website should have a `robots.txt` file at the root (e.g., `https://example.com/robots.txt`).

### Syntax Guide

```
# This is a comment

# Rules for all bots
User-agent: *
Disallow: /private/
Disallow: /admin/
Allow: /public/
Crawl-delay: 5

# Rules for specific bot
User-agent: Googlebot
Allow: /

# Sitemap location
Sitemap: https://example.com/sitemap.xml
```

### Parsing robots.txt in Python

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://books.toscrape.com/robots.txt")
rp.read()

# Check if we can fetch a URL
url = "https://books.toscrape.com/catalogue/page-1.html"
if rp.can_fetch("*", url):
    print("Allowed to scrape this URL")
else:
    print("Not allowed to scrape this URL")
```

---

## 🚀 Performance Tips

### 1. Connection Pooling

```python
import requests

# Reuse connections with a session
session = requests.Session()

for url in urls:
    response = session.get(url)  # Reuses TCP connection
```

### 2. Caching Responses

```python
import hashlib
import os
import pickle

def get_cached_response(url, cache_dir="cache"):
    # Create cache filename from URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{url_hash}.pkl")
    
    # Check if cached
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    
    # Fetch and cache
    response = requests.get(url)
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, "wb") as f:
        pickle.dump(response, f)
    
    return response
```

### 3. Async Scraping (Advanced)

For high-volume scraping, consider using `aiohttp` with `asyncio` for concurrent requests.

---

## 📚 Summary

| Topic | Key Takeaway |
|-------|--------------|
| **HTTP** | Understand request/response cycle and status codes |
| **DOM** | Learn CSS selectors for precise element targeting |
| **JavaScript** | Use Selenium when content loads dynamically |
| **CAPTCHA** | Respect them; find alternatives |
| **IP Blocking** | Rate limit and use proper headers |
| **robots.txt** | Always check and respect it |
| **Legal** | Read ToS, be ethical, don't cause harm |
