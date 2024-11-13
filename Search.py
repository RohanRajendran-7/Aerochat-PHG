import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# def calculate_partial_match_percentage(keyword, text):
#     """
#     This function calculates the partial match percentage of the keyword in the text.
#     It checks how much of the keyword appears in sequence in the text.
#     """
#     # Convert the keyword and text to lowercase for case-insensitive comparison
#     keyword = keyword.lower()
#     text = text.lower()

#     # Initialize variables to count matches
#     match_in_text = 0
    
#     # Sliding window approach: check if sequential parts of the keyword are found in the text
#     for i in range(len(keyword)):
#         if keyword[i:i + len(text)] in text:
#             match_in_text += 1
    
#     # Calculate match percentage as (matched characters / total characters in keyword) * 100
#     match_percentage = (match_in_text / len(keyword)) * 100 if len(keyword) > 0 else 0
#     return match_percentage

def calculate_partial_match(keyword, text):
    """
    This function checks if any part of the keyword appears in the text.
    It returns "Yes" if there's a match, otherwise "No".
    """
    # Convert the keyword and text to lowercase for case-insensitive comparison
    keyword = keyword.lower()
    text = text.lower()

    # Check if the keyword is found in the text
    if keyword in text:
        return "Yes"
    else:
        return "No"

def search_past_24_hours_with_selenium(keywords):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    driver = webdriver.Chrome(options=options)

    keyword_matches = {keyword: {"total": 0, "matches": 0} for keyword in keywords}

    # Iterate over each keyword
    for query in keywords:
        base_url = f"https://www.google.com/search?q={query}&tbs=qdr:d"  # Time filter for past 24 hours
        page_num = 0
        results = []

        print(f"Searching for keyword: {query}")

        while True:
            search_url = f"{base_url}&start={page_num * 10}"
            driver.get(search_url)
            time.sleep(random.randint(2, 5))  # Random delay to mimic human behavior

            # Wait for search results to load
            wait = WebDriverWait(driver, 10)
            try:
                # Wait until titles are present
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'h3')))
            except Exception as e:
                print(f"Error or no results on page {page_num + 1}: {str(e)}")
                break  # Exit if no titles are found

            # Extract search results
            page_results = []
            search_items = driver.find_elements(By.CSS_SELECTOR, '.tF2Cxc')  # CSS selector for individual result blocks

            for item in search_items:
                try:
                    title = item.find_element(By.CSS_SELECTOR, 'h3').text
                    url = item.find_element(By.CSS_SELECTOR, '.yuRUbf a').get_attribute('href')
                    
                    # Try to get snippet from multiple possible elements
                    snippet = None
                    try:
                        snippet = item.find_element(By.CSS_SELECTOR, '.IsZvec').text  # Common snippet element
                    except:
                        try:
                            snippet = item.find_element(By.CSS_SELECTOR, '.VwiC3b').text  # Alternative snippet element
                        except:
                            snippet = "No snippet available"  # Fallback if no snippet found

                    # Check if the keyword matches the title or content (snippet)
                    result_data = {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "matches": {"is_title_match": False, "is_content_match": False}
                    }

                    title_match_percentage = calculate_partial_match(query, title)
                    snippet_match_percentage = calculate_partial_match(query, snippet)
                    print(title_match_percentage, "- title", "\n", snippet_match_percentage,query, title , snippet )
                    if title_match_percentage:
                        result_data["matches"]["is_title_match"] = True
                        keyword_matches[query]["matches"] += 1

                    if snippet_match_percentage:
                        result_data["matches"]["is_content_match"] = True
                        keyword_matches[query]["matches"] += 1

                    keyword_matches[query]["total"] += 1

                    page_results.append(result_data)

                except Exception as e:
                    print(f"Skipping a result due to an error: {e}")
                    continue

            if not page_results:
                print("No more results found on this page. Ending scrape.")
                break  # Stop if no results are found on this page

            results.extend(page_results)
            print(f"Fetched {len(page_results)} results from page {page_num + 1}.")

            # Move to the next page
            page_num += 1
            delay = random.randint(2, 5)
            print(f"Sleeping for {delay} seconds...")
            time.sleep(delay)

        # Output collected results for the current keyword
        print(f"\nCollected Results for keyword: {query}")
        for result in results:
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet']}")
            print(f"Title Match: {result['matches']['is_title_match']}, Content Match: {result['matches']['is_content_match']}")
            print("-" * 80)

    # Keyword match summary for all keywords
    print("\nKeyword Match Summary:")
    for keyword, match_data in keyword_matches.items():
        print(f"Keyword: {keyword}")
        print(f"Total Results: {match_data['total']}")
        print(f"Matching Results: {match_data['matches']}")
        print("-" * 40)
    driver.quit()
    return keyword_matches
