from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

import urllib

def get_article_content(url, driver):
    """Navigate to the article URL and get its content."""
    try:
        driver.get(url)
        time.sleep(random.randint(2, 5))  # Random delay to mimic human behavior

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article, div, p, span')))
        
        content_elements = driver.find_elements(By.CSS_SELECTOR, 'p, span, div')
        content = " ".join([element.text for element in content_elements if element.text.strip()])
        
        return content if content else "Content not available"
    
    except Exception as e:
        print(f"Error visiting URL {url}: {e}")
        return "Error fetching content"

def calculate_partial_match(keyword, text):
    keyword = keyword.lower()
    text = text.lower()

    if keyword in text:
        return "Yes"
    else:
        return "No"

def search_google_news(keyword):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')  # Bypass detection
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36')  # Change user-agent
    driver = webdriver.Chrome(options=options)
    query = f'"{keyword}"' 
    encoded_query = urllib.parse.quote(query)
    base_url = f"https://news.google.com/search?q={encoded_query}"
    driver.get(base_url)
    time.sleep(random.randint(2, 5))

    results = []
    all_results = []
    wait = WebDriverWait(driver, 10)
    
    while True:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article')))
        except Exception as e:
            print(f"Error or no articles found: {str(e)}")
            break

        articles = driver.find_elements(By.CSS_SELECTOR, 'article')

        for article in articles:
            title = None
            url = None
            snippet = None

            try:
                # Attempt to get title and URL from different structures
                try:
                    title_element = article.find_elements(By.TAG_NAME, 'a')[1]
                    title = title_element.text
                    url = title_element.get_attribute('href')
                except:
                    pass

                # Try a different structure if the above fails
                if not title:
                    try:
                        title_element = article.find_element(By.CSS_SELECTOR, 'h4 a')
                        title = title_element.text
                        url = title_element.get_attribute('href')
                    except:
                        title = "Title not available"
                        url = "URL not available"

                # Extract snippet
                try:
                    snippet_element = article.find_element(By.CSS_SELECTOR, 'span')
                    snippet = snippet_element.text
                except:
                    snippet = "Snippet not available"

                # Get article content from the URL
                #article_content = get_article_content(url, driver) if url and url != "URL not available" else "URL not available"
                article_content=""
                result_data ={
                    "title": title, 
                    "url": url, 
                    "snippet": snippet, 
                    "content": article_content,
                    "matches": {"is_title_match": False, "is_content_match": False}
                }
                results.append(result_data)
                title_match_percentage = calculate_partial_match(keyword, title)
                snippet_match_percentage = calculate_partial_match(keyword, snippet)
                print(title_match_percentage, "- title", "\n", snippet_match_percentage,query, title , snippet )
                if title_match_percentage:
                    result_data["matches"]["is_title_match"] = True

                if snippet_match_percentage:
                    result_data["matches"]["is_content_match"] = True
                
            except Exception as e:
                print(f"Error processing an article: {e}")
                continue

        # Check if there's a "next" button to go to the next page
        try:
            next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next page"]')
            next_button.click()
            time.sleep(random.randint(2, 5))  # Delay before moving to the next page
        except:
            print("No more pages available or 'Next' button not found.")
            break

    # Output collected results
    print("\nCollected Results: ", len(results))
    for result in results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        #driver.get(result['url'])
        print(f"Snippet: {result['snippet']}")
        print(f"Content: {result['content'][:500]}...")  # Print a snippet of the content
        print("-" * 80)

        all_results.append({
            "keyword": query,
            "results": [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "is_title_match": result["matches"]["is_title_match"],
                    "is_content_match": result["matches"]["is_content_match"],
                    "match_type": "title_match" if result["matches"]["is_title_match"] else "content_match" if result["matches"]["is_content_match"] else "none"
                }
                for result in results
            ]
        })
    driver.quit()
    print(all_results)
    return all_results
