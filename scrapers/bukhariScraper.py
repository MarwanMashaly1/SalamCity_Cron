import requests
import time, random
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

class BukhariSpider:
    BASE_URL = "https://bukharicentre.com"

    def __init__(self, js_render=False):
        self.js_render = js_render
        self.org_id = 13
        self.org_name = "Bukhari Centre"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = Request("https://bukharicentre.com/events/", headers=headers)
        self.events_page = urlopen(req).read()
        self.events_soup = BeautifulSoup(self.events_page, 'html.parser')
        print("Bukhari Spider initialized")
        
    def get_events(self):
        """
        Scrape the events listing page, gather event title, image, link, 
        and also fetch inside-page descriptions. Returns a list of dicts.
        """
        events_page_url = f"{self.BASE_URL}/events/"
        print(f"Fetching events listing page: {events_page_url}")
        resp = requests.get(events_page_url, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to fetch {events_page_url}, status: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all articles that represent events
        # The HTML snippet shows article tags with class "w-grid-item"
        articles = soup.find_all("article", class_="w-grid-item")
        
        events = []
        for article in articles:
            event_info = {}
            
            # 1) Grab the link and title from <a ... aria-label="something">
            link_tag = article.find("a", attrs={"aria-label": True})
            if not link_tag:
                # In case the structure is slightly different
                continue
            
            link = link_tag["href"]
            title = link_tag["aria-label"].strip()
            
            # 2) Grab the thumbnail image from <img ... src="...">
            image_tag = link_tag.find("img")
            image_url = ""
            if image_tag and image_tag.get("data-src"):
                image_url = image_tag["data-src"]
                print(f"Found image: {image_url}")

            event_info["title"] = title
            event_info["link"] = link
            event_info["image"] = image_url
            
            # 3) Visit the event detail page to get the detailed description
            event_info["description"] = self._get_event_description(link)

            events.append(event_info)
            
            # Sleep a bit to reduce load & not appear too “bot-like”
            time.sleep(random.uniform(1, 3))
        
        return events

    def _get_event_description(self, url):
        """
        Fetch the event’s detail page and extract the main descriptive text
        from <div class="w-post-elm post_content ..."> (or any suitable selector).
        """
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"Could not open detail page {url}, status: {resp.status_code}")
                return ""
            
            detail_soup = BeautifulSoup(resp.text, "html.parser")

            # Looking for a <div> that holds the main post content, e.g.:
            #   <div class="w-post-elm post_content us_custom_xxxxx us_animate_this start" itemprop="text">...</div>
            # The class might differ, so you can find by partial class match or a more general approach
            content_div = detail_soup.find("div", class_="w-post-elm post_content")
            if content_div:
                # Get all text (with newlines or spaces). We can be more sophisticated if needed.
                return content_div.get_text(separator="\n", strip=True)
            else:
                # Fallback: maybe the text is in another container or <main>?
                main_tag = detail_soup.find("main", {"id": "page-content"})
                if main_tag:
                    return main_tag.get_text(separator="\n", strip=True)
                else:
                    return ""
        except Exception as e:
            print(f"Error fetching detail page {url}: {e}")
            return ""

if __name__ == "__main__":
    spider = BukhariSpider()
    events = spider.get_events()
    print(events)
