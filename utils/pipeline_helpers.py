# utils/pipeline_helpers.py

import logging
from datetime import datetime
from utils.rate_limiter import RateLimiter
from categorize import Categorize
from dateutil import parser
import time



logger = logging.getLogger(__name__)
rate_limiter = RateLimiter(rate=1, burst=1)
cat = Categorize(token_counter_min=0, rpd=0, rpm=0)

def categorize(title, desc):
    while True:
        try:
            cats = cat.classify(title, desc)
            return cats
        except Exception as e:
            msg = str(e)
            if "token limit reached per day" in msg:
                logger.warning('Daily token limit reached, categorizing as uncategorized.')
                return "uncategorized"
            elif ("token limit reached per minute" in msg or 
                  "requests limit reached per minute" in msg):
                logger.warning('Minute token/request limit reached, sleeping...')
                time.sleep(90)
                continue
            else:
                logger.error(f"Unexpected error in categorize: {msg}")
                return "uncategorized"

def handle_event(db, ev, spider):
    cats = categorize(ev.get("title"), ev.get("description", ""))
    with rate_limiter:
        date_str = ev.get("date")
        normalized_date = parse_date(date_str) if date_str else None

        db.add_event(
            title=ev.get("title"),
            date=normalized_date,
            image=ev.get("image"),
            link=ev.get("link"),
            start_time=ev.get("start_time"),
            end_time=ev.get("end_time"),
            location=ev.get("location"),
            short_description=ev.get("short_description"),
            full_description=ev.get("full_description") or ev.get("description"),
            categories=cats,
            sub_links=ev.get("sub_links") or ev.get("registration_link") or ev.get("other_links"),
            other_info=ev.get("other_info") or ev.get("iframe"),
            created_at=ev.get("created_at") or datetime.utcnow(),
            cost=ev.get("cost"),
            is_video=ev.get("is_video", False),
            organization_id=spider.org_id,
            organization_name=spider.org_name
        )
        logger.info("Added %s event to database: %s", spider.org_name, ev.get("title") or ev.get("link"))

def handle_prayer_time(db, prayer_time, spider):
    with rate_limiter:
        db.add_prayer_time(
            prayer_time.get("prayer_name"),
            prayer_time.get("athan_time"),
            prayer_time.get("iqama_time"),
            organization_id=spider.org_id,
            organization_name=spider.org_name
        )
        logger.info("Added %s prayer time to database: %s", spider.org_name, prayer_time.get("prayer_name"))

def parse_date(date_str):
    """
    Parse a date string in various formats and return a string in 'YYYY-MM-DD' format.
    Returns None if parsing fails.
    """
    try:
        dt = parser.parse(date_str, fuzzy=True, dayfirst=False)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None