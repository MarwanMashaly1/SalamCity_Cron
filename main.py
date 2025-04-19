import logging
from datetime import datetime
from dotenv import load_dotenv
from db.connections import DBConfig
from db.models import Database
from utils.logger import setup_logging
from utils.rate_limiter import RateLimiter
from categorize import Categorize
from scrapers.jami import JamiSpider
from scrapers.rahma import RahmaSpider
from scrapers.kma import KmaSpider
from scrapers.snmc import SnmcSpider
import time

# Load ENV
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# DB init
db_conf = DBConfig()
db = Database(db_conf)
rate_limiter = RateLimiter(rate=1)

# Import spiders
# ... add others

# Categorization (your existing class)
cat = Categorize(token_counter_min=0, rpd=0, rpm=0)


def categorize(title, desc):
    while True:
        cats = cat.classify(title, desc)
        if 'limit' in cats:
            logger.warning('Rate/cap limit, sleeping...')
            time.sleep(60)
            continue
        return cats


def run_pipeline():
    logger.info('Start pipeline at %s', datetime.utcnow())
    spiders = [
        (RahmaSpider, True),   # JS‑heavy → Browserless
        (KmaSpider, True),     # JS‑heavy → Browserless
        (SnmcSpider, False),   # static → BS4
        (JamiSpider, False),   # static → BS4
    ]

    for SpiderClass, js_render in spiders:
        try:
            spider = SpiderClass(js_render=js_render)
            events = spider.get_events()
            for ev in events:
                cats = categorize(ev['title'], ev.get('description',''))
                with rate_limiter():
                    db.add_event(
                        title=ev['title'],
                        link=ev.get('link'),
                        image=ev.get('image'),
                        full_description=ev.get('description'),
                        categories=cats,
                        created_at=datetime.utcnow(),
                        organization_id=spider.org_id,
                        organization_name=spider.org_name
                    )
        except Exception:
            logger.exception('Failed processing %s', SpiderClass.__name__)
    db.update_old_activity()
    db.close_connection()
    logger.info('Pipeline complete')

if __name__ == '__main__':
    run_pipeline()