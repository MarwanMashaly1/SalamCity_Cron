from bs4 import BeautifulSoup
from urllib.request import urlopen
import time, random
from utils.browser import get_html

class RahmaSpider:
    def __init__(self, js_render=False):
        self.js_render = js_render
        self.org_id = 3
        self.org_name = "Masjid Ar-Rahma"
        # Fetch events page HTML
        events_url = "https://www.mymasjid.ca/events"
        self.events_page = get_html(events_url)
        
        # Fetch prayer times page HTML
        prayer_url = "https://app.mymasjid.ca/protected/public/timetable"
        self.prayer_page = get_html(prayer_url)
        
        self.events_soup = BeautifulSoup(self.events_page, 'html.parser')
        self.prayer_soup = BeautifulSoup(self.prayer_page, 'html.parser')
        print("Rahma Spider initialized")

    def get_events(self):
        .3
        events = []
        table = self.events_soup.find(lambda tag: tag.name == 'table' and tag.has_attr(
            'id') and tag['id'] == "tablepress-4")
                
        rows = table.findAll(lambda tag: tag.name == 'tr')
        for row in rows:
            if row.find('td') is not None:
                event = {}
                # event_name = row.find('td').text
                event["title"] = row.find('td').text
                # check if href exists if yes get url
                if row.find('a') is not None:
                    event_link = row.find('a')['href']
                
                    # check if it is not null
                    event["link"] = event_link
                    # check if event link is a google forms link
                    if "google.com" not in event_link:
                        event_info = self.get_eventInfo(event_link)
                        if "image" in event_info:
                            event["image"] = event_info["image"]
                        if "description" in event_info:
                            event["description"] = event_info["description"]
                else:
                    event["link"] = "https://events.mymasjid.ca/events"


                events.append(event)
                time.sleep(random.uniform(2, 5))
        return events

    def get_prayer_times(self):
        prayerTimes = []
        # prayerTimes.append(
        #     ("Masjid Ar-Rahma", "1216 Hunt Club Rd, Ottawa, ON K1V 2P1", "(613) 523-9977"))
        table = self.prayer_soup.find("table", {"class": "table table-sm"})
        if table is not None:
            for row in table.findAll("tr"):
                if row.find('td') is not None:
                    if row.find('td').text == "Salāh":
                        continue
                    prayer = {}
                    prayer_eng = row.find('td').text
                    athan_time = row.find('td').find_next_sibling().text
                    iqama_time = row.find(
                        'td').find_next_sibling().find_next_sibling().text
                    # prayer_ar = row.find('td').find_next_sibling(
                    # ).find_next_sibling().find_next_sibling().text
                    prayer["prayer_name"] = prayer_eng
                    prayer["athan_time"] = athan_time
                    prayer["iqama_time"] = iqama_time
                    prayerTimes.append(prayer)
        return prayerTimes

    def get_eventInfo(self, event_link):
        eventInfo = {}
        event_page = urlopen(event_link).read()
        event_soup = BeautifulSoup(event_page, 'html.parser')
        event_description = event_soup.find(class_='content event_details')
        if event_description is not None:
            eventInfo["description"] = event_description.text

        if event_soup.find(class_='content event_poster') is not None:
            event_image = event_soup.find(class_='content event_poster')
            eventInfo["image"] = "https://events.mymasjid.ca" + event_image.find('img')['src']
            # eventInfo.append("https://events.mymasjid.ca" +
            #                  event_image.find('img')['src'])
        return eventInfo
