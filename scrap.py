import requests
from bs4 import BeautifulSoup
import json

# Set up your Google Custom Search API details
API_KEY = 'AIzaSyDZE6--pmdsqIk9vehwC_ETn7YELXh2AwI'
CX = '346640fd765c64a9f'

def search_keywords(keywords, api_key, cx):
    # List to store the results for all keywords
    keyword_matches = {}
    
    for keyword in keywords:
        # Initialize the result for the current keyword
        keyword_matches[keyword] = {
            'total_results': 0,
            'matching_results': 0,
            'matches': []
        }
        
        # Perform the search for the current keyword
        search_results = google_search(keyword, api_key, cx)
        
        # Get the total number of results from the API
        total_results = search_results.get('searchInformation', {}).get('totalResults', 0)
        keyword_matches[keyword]['total_results'] = total_results
        
        # Check each result for matching keyword in the title or content
        for result in search_results.get('items', []):
            # Fetch the full content of the URL
            page_content = fetch_page_content(result['link'])
            
            if page_content:
                # Check if the keyword is present in the title
                is_title_match = keyword.lower() in result['title'].lower()
                
                # Check if the keyword is present in the full page content
                is_content_match = keyword.lower() in page_content.lower()
                
                # If either is a match, store the result with flags
                if is_title_match or is_content_match:
                    keyword_matches[keyword]['matching_results'] += 1
                    keyword_matches[keyword]['matches'].append({
                        'title': result['title'],
                        'url': result['link'],
                        'snippet': result['snippet'],
                        'published_at': result.get('published_at', 'Unknown'),
                        'is_title_match': is_title_match,
                        'is_content_match': is_content_match
                    })
    
    return keyword_matches

def google_search(query, api_key, cx, date_restrict='1d'):
    search_url = 'https://www.googleapis.com/customsearch/v1'
    
    params = {
        'q': query,                       # Search query (the keyword)
        'key': api_key,                   # Your API key
        'cx': cx,                         # Your Custom Search Engine ID
        'dateRestrict': date_restrict,    # Restrict search to the last 24 hours
        'num': 10,                        # Number of results per query (max 10)
    }
    
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {}

def fetch_page_content(url):
    """
    Fetch the entire content of the page and return the text.
    This uses BeautifulSoup to parse the HTML and extract visible text.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch URL {url} - Status code: {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from the page, excluding scripts and styles
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()  # Remove them

        page_text = soup.get_text()
        
        # Optionally, filter or clean up the text
        page_text = ' '.join(page_text.split())  # Clean up extra spaces/newlines

        return page_text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page content from {url}: {e}")
        return ""

# Example usage:

# List of keywords to search for
keywords = ["Prince Group", "Chen zhi Cambodia"]

# Call the search function
matches = search_keywords(keywords, API_KEY, CX)

# Print the results
for keyword, data in matches.items():
    print(f"Results for keyword: {keyword}")
    print(f"Total Results: {data['total_results']}")
    print(f"Matching Results: {data['matching_results']}")
    if data['matches']:
        for result in data['matches']:
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet']}")
            print(f"Published At: {result['published_at']}")
            print(f"Is Title Match: {result['is_title_match']}")
            print(f"Is Content Match: {result['is_content_match']}")
            print("-" * 80)
    else:
        print("No matching results found.")
    print("\n")
