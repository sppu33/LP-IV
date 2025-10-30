import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# ------------------------------------------
# A Simple Web Crawler
# ------------------------------------------
class WebCrawler:
    """A simple recursive web crawler class."""

    def __init__(self, seed_url, max_depth=2):
        """
        Initialize the crawler.
        seed_url  : Starting URL
        max_depth : Maximum link depth to crawl
        """
        self.seed_url = seed_url
        self.max_depth = max_depth
        self.visited_urls = set()                  # To avoid visiting same link twice
        self.base_domain = urlparse(seed_url).netloc  # Restrict crawling to same website

    def crawl(self):
        """Start crawling from the seed URL."""
        self._crawl_recursive(self.seed_url, 0)

    def _crawl_recursive(self, current_url, depth):
        """
        Recursive crawling function.
        current_url : Current URL to visit
        depth       : Current recursion depth
        """
        # Stop if we reached max depth or already visited
        if depth > self.max_depth or current_url in self.visited_urls:
            return

        print(f"Crawling (Depth {depth}): {current_url}")
        self.visited_urls.add(current_url)

        try:
            # Send GET request to fetch page content
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()  # Raise error for invalid responses

            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags that contain href attributes (links)
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']
                # Convert relative link to absolute URL
                absolute_url = urljoin(current_url, href)

                # Parse URL and ensure it's valid and from same domain
                parsed_url = urlparse(absolute_url)
                if (parsed_url.scheme in ['http', 'https'] and
                        parsed_url.netloc == self.base_domain):
                    # Recursive call to crawl next link
                    self._crawl_recursive(absolute_url, depth + 1)

        except requests.exceptions.RequestException as e:
            # Handles all HTTP, connection, or timeout errors
            print(f"Could not fetch URL {current_url}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {current_url}: {e}")

# ------------------------------------------
# Main Function
# ------------------------------------------
def main():
    """Main function to start the web crawler."""
    # Safe website to test crawler
    seed_url = "http://info.cern.ch/hypertext/WWW/TheProject.html"
    # seed_url = "https://medium.com/@mandalsaurav3/do-hard-things-if-you-want-an-easy-life-81be3a096207"
    
    # Create crawler object with max depth of 2
    crawler = WebCrawler(seed_url, max_depth=2)
    
    # Start crawling
    crawler.crawl()
    print(f"\nCrawling finished. Visited {len(crawler.visited_urls)} unique pages.")

# Run main if script is executed directly
if __name__ == "__main__":
    main()
