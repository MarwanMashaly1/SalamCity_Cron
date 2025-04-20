import google.generativeai as genai
import os
import time
from datetime import datetime, timedelta
import re
import json
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('GENAI_API_KEY')
print("api key: ", api_key)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')


class Categorize:
    def __init__(self, token_counter_min, rpd, rpm):
        self.token_counter_min = token_counter_min
        self.rpd = rpd
        self.rpm = rpm
        self.start_time_minute = datetime.now()
        self.start_time_day = datetime.now()

    def check_limits(self):
        # Check if a minute has passed
        if datetime.now() - self.start_time_minute >= timedelta(minutes=1):
            self.start_time_minute = datetime.now()
            self.token_counter_min = 0
            self.rpm = 0

        # Check if a day has passed
        if datetime.now() - self.start_time_day >= timedelta(days=1):
            self.start_time_day = datetime.now()
            self.rpd = 0

        if self.token_counter_min >= 1000000:
            time.sleep(60 - (datetime.now() - self.start_time_minute).seconds)
            self.token_counter_min = 0
            self.start_time_minute = datetime.now()

        if self.rpm >= 15:
            time.sleep(60 - (datetime.now() - self.start_time_minute).seconds)
            self.rpm = 0
            self.start_time_minute = datetime.now()

        if self.rpd >= 1000:
            return "token limit reached per day"
    
    def refine_response(self, response):
        # Remove all newline characters
        response = response.replace('\n', ', ')

        # Remove all "yes" and "xx" values
        response = re.sub(r': yes|: xx', '', response)

        # Split the response into categories
        categories = response.split(', ')

        # Create a dictionary to store the categories
        refined_response = {}

        # Create a set to store the categories that have already been added
        added_categories = set()

        # Create a counter to keep track of the number of categories
        category_count = 0

        # Iterate over the categories
        for i, category in enumerate(categories):
            # Remove any leading or trailing whitespace
            category = category.strip()

            # If the category contains a colon, split it and only keep the part after the colon
            if ':' in category:
                category = category.split(': ')[1]

            # If the category is not empty and has not been added yet, add it to the dictionary
            if category and category not in added_categories:
                refined_response[f'category{category_count+1}'] = category
                added_categories.add(category)
                category_count += 1

            # If we have already added 5 categories, break the loop
            if category_count >= 5:
                break

        return refined_response

    def classify(self, event_name, event_description):
        self.check_limits()
        print("desc type: ", type(event_description))
        if event_name == None and event_description != None:
            print("event name is none")

            input_text = '''
                Given the following event description can you categorize the event in one word where the category follows an Islamic manner and choose specificly from the following list of categories and don't go outside of them:
                Community Gatherings
                Charity and Volunteering
                Sports and Recreation
                Professional Development
                Health and Wellness
                Advocacy and Awareness
                Youth
                Children
                Art and Culture
                Educational Programs
                Halaqas
                Lectures
                Conferences
                Seminars
                Workshops
                Quranic Activities
                Quran Recitation Sessions
                Quran Memorization Classes
                Tafsir (Quranic Exegesis) Sessions
                Religious Education
                Islamic Studies Classes
                Fiqh (Islamic Jurisprudence) Classes
                Seerah (Prophet's Biography) Classes
                Religious Celebrations
                Ramadan Events
                Eid Celebrations
                Brothers
                Sisters

                and the answer must follow this format:
                category1: xx, category2: xx
                if you can't determine the category from the description, please write "uncategorized". Do not answer with each one as yes or no but write only the categories names as detailed before and seperate each one with a comma.
                ... 
                and an event can have 1,2,3 or more categories based on the description
                DO NOT SAY ANYTHING ELSE OR ADD ANYTHING ELSE TO THE RESPONSE EXCEPT THE CATEGORIES BASED ON THE DESCRIPTION EARLIER

                ''' + "description: " + event_description
        elif event_name != None and event_description != None:
            input_text = ''' 
                Given the following event name and description can you  categorize the event in one word where the category follows an Islamic manner and choose specificly from the following list of categories and don't go outside of them:
                Community Gatherings
                Charity and Volunteering
                Sports and Recreation
                Professional Development
                Health and Wellness
                Advocacy and Awareness
                Youth
                Children
                Art and Culture
                Educational Programs
                Halaqas
                Lectures
                Conferences
                Seminars
                Workshops
                Quranic Activities
                Quran Recitation Sessions
                Quran Memorization Classes
                Tafsir (Quranic Exegesis) Sessions
                Religious Education
                Islamic Studies Classes
                Fiqh (Islamic Jurisprudence) Classes
                Seerah (Prophet's Biography) Classes
                Religious Celebrations
                Ramadan Events
                Eid Celebrations
                Brothers
                Sisters

                and the answer must follow this format:
                category1: xx, category2: xx
                if you can't determine the category from the description, please write "uncategorized". Do not answer with each one as yes or no but write only the categories names as detailed before and seperate each one with a comma.

                ... 
                and an event can have 1,2,3 or more categories based on the description
                DO NOT SAY ANYTHING ELSE OR ADD ANYTHING ELSE TO THE RESPONSE EXCEPT THE CATEGORIES BASED ON THE DESCRIPTION EARLIER
                ''' + "name: " + event_name + " description: " + event_description
        else:
            return "uncateogrized"
        
        tokens = int(model.count_tokens(input_text).total_tokens)
        self.token_counter_min += tokens    
        print("token count: ", self.token_counter_min)
        self.rpd += 1
        self.rpm += 1

        if self.token_counter_min > 1000000:
            return "token limit reached per minute"
        if self.rpd >= 1000:
            return "token limit reached per day"
        if self.rpm >= 15:
            return "requests limit reached per minute"
        output = model.generate_content(input_text)
        output_text = output.candidates[0].content.parts[0].text
        refined_response = self.refine_response(output_text)
        categories_str = json.dumps(refined_response)
        # print(output.candidates[0].content.parts[0].text)
        print(categories_str)
        return categories_str


# classify("Sisters’ Circle of Mercy: Sisterhood in Islam", "Join us for another Sisters' Circle of Mercy session. Meet new sisters and talk about topics that matte to our community! When: Friday, June 21st - 6:00pm to 7:00pm What: Finding honourable Company: Sisterhood in Islam Who: Girls 12-16 Where: Jami Omar 2nd floor, room231")
# classify("High School Girls Study Space", "Calling all High School Girls! Come study at KMA to prepare for your exams! Free wifi tea, coffee, and snacks provided!")


def refine_response( response):
    # Remove all newline characters
    response = response.replace('\n', ', ')

    # Remove all "yes" and "xx" values
    response = re.sub(r': yes|: xx', '', response)

    # Split the response into categories
    categories = response.split(', ')

    # Create a dictionary to store the categories
    refined_response = {}

    # Create a set to store the categories that have already been added
    added_categories = set()

    # Create a counter to keep track of the number of categories
    category_count = 0

    # Iterate over the categories
    for i, category in enumerate(categories):
        # Remove any leading or trailing whitespace
        category = category.strip()

        # If the category contains a colon, split it and only keep the part after the colon
        if ':' in category:
            category = category.split(': ')[1]

        # If the category is not empty and has not been added yet, add it to the dictionary
        if category and category not in added_categories:
            refined_response[f'category{category_count+1}'] = category
            added_categories.add(category)
            category_count += 1

        # If we have already added 5 categories, break the loop
        if category_count >= 5:
            break

    return refined_response
