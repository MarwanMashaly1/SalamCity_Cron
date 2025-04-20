from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse, parse_qs

class JamiOmarSpider:
    def __init__(self, js_render=False) -> None:
        self.js_render = js_render
        self.org_id = 6
        self.org_name = "Jami Omar"
        self.page = urlopen("https://www.jamiomar.org/")
        self.soup = BeautifulSoup(self.page, 'html.parser')

        print("Jami Omar Spider initialized")
    
    
    def get_events(self):
        event_container = self.soup.find('div', class_='event-wrap')
        event_urls = []
        for link in event_container.find_all('a', href=True):
            if link['href'] not in event_urls:
                event_urls.append(link['href'])
        # event_urls = [link['href'] for link in event_container.find_all('a', href=True)]
        events = []
        for url in event_urls:
            event = self.get_event_details(url)
            events.append(event)
        return events


        # events = []
        # main_div = self.soup.find_all('div', class_='Zc7IjY')
        # # list_items = main_div.find_all('div', class_='Zc7IjY')
        # count = 0
        # for item in main_div:
        #     if count > 7:
        #         break
        #     event_title = item.find('h4', class_='font_4').text.strip()

        #     button_link = item.find('div', class_='comp-kimeej6i').find('a')
            
        #     btn_url = ''
        #     btn_label = ''
        #     if button_link:
        #         # Extract link URL
        #         btn_url = button_link['href']
        #         # Extract button label
        #         btn_label = button_link.find('span', class_='StylableButton2545352419__label').text.strip()
        #     else:
        #         # Extract button label
        #         btn_label = item.find('span', class_='StylableButton2545352419__label').text.strip()
        #         btn_url = None

        #     # Extract donation instructions
        #     donation_instructions = item.find('div', class_='comp-kyqk9s96').find('p', class_='font_8').text.strip()

        #     # Extract image URL
        #     image_url = item.find('img')['src']

        #     # Check if 'blur_2' is present in the query parameters
        #     if 'blur_2' in image_url:
        #         image_url = image_url.replace(',blur_2', '')
        #     if 'w_101' in image_url and 'h_57' in image_url:
        #         image_url = image_url.replace('w_101', 'w_496')
        #         image_url = image_url.replace('h_57', 'h_264')
        #     events.append((image_url, event_title, donation_instructions, btn_url, btn_label))
        #     count +=1

        # return(events)
    def get_event_details(self, url):
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        event_details = {}

        event_details['link'] = url
        # Extract event image URL
        event_image = soup.find('img', {'class': 'img-fluid w-100 wp-post-image'})
        event_details['image'] = event_image['src'] if event_image else None

        # Extract event location
        event_location = soup.find('span', {'class': 'd-block thm-clr'})
        event_details['location'] = event_location.text if event_location else None

        # Extract event title
        event_title = soup.find('h2', {'class': 'mb-0'})
        event_details['title'] = event_title.text if event_title else None

        # Extract event time
        event_time_upper = soup.find('div', {'class': 'event-detail-price-button-inner'})
        if event_time_upper:
            event_time = event_time_upper.find('span', {'class': 'd-block thm-clr'})
            if event_time:
                time_text = event_time.text.strip()
                if 'am' in time_text or 'pm' in time_text:
                    time_parts = time_text.split(' - ')
                    event_details['start_time'] = time_parts[0]
                    event_details['end_time'] = time_parts[1] if len(time_parts) > 1 else None
                else:
                    event_details['start_time'] = None
                    event_details['end_time'] = None
            else:
                event_details['start_time'] = None
                event_details['end_time'] = None

        # Extract event cost
        event_cost = soup.find('span', {'class': 'price d-block'})
        event_details['cost'] = event_cost.text.strip() if event_cost else None

        # Extract event description
        event_description = soup.find('div', {'class': 'post-detail-desc w-100'})
        event_details['description'] = event_description.text.strip() if event_description else None

        # Extract event registration link if exists
        event_registration_link = soup.find('a', {'class': 'thm-btn bg-color1'})
        event_details['registration_link'] = event_registration_link['href'] if event_registration_link else None

        return event_details

    def get_prayertimes(self):
        times = []
        main_div = self.soup.find_all('div', class_='comp-kimeej6i')
        for item in main_div:
            if item.find('div', class_='comp-kimeej6i'):
                continue
            else:
                prayer_name = item.find('div', class_='font_4').text.strip()
                prayer_time = item.find('div', class_='font_5').text.strip()
                times.append((prayer_name, prayer_time))
        return(times)
        