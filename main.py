import logging
from datetime import datetime
from dotenv import load_dotenv
from db.models import Database
from utils.logger import setup_logging
from scrapers.rahmaScraper import RahmaSpider
from scrapers.snmcScraper import SnmcSpider
from scrapers.kmaScraper import KmaSpider
from scrapers.jamiOmarScraper import JamiOmarSpider
from scrapers.bukhariScraper import BukhariSpider
from utils.pipeline_helpers import handle_event, handle_prayer_time
import os

# Load ENV and set up logging
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# DB init
host   = os.getenv('DB_HOST')
port   = int(os.getenv('DB_PORT', 3306))      # default to 3306 if empty
name   = os.getenv('DB_NAME')
user   = os.getenv('DB_USER')
passwd = os.getenv('DB_PASSWORD')             # <— matches the workflow key

print("ENV VARS SET:", 
      "DB_HOST" in os.environ, 
      "DB_PORT" in os.environ, 
      "DB_NAME" in os.environ, 
      "DB_USER" in os.environ, 
      "DB_PASSWORD" in os.environ)

port = int(os.getenv('DB_PORT') or 3306)

db = Database(
    host=host,
    username=user,
    password=passwd,
    db_name=name,
    port=port
)

def run_pipeline():
    logger.info('Start pipeline at %s', datetime.utcnow())
    
    spiders = [
        (RahmaSpider, True), 
        (KmaSpider, True),
        (SnmcSpider, False),
        (JamiOmarSpider, False),
        (BukhariSpider, False)
    ]

    for SpiderClass, js_render in spiders:
        try:
            spider = SpiderClass(js_render=js_render)
            print(f"Spider initialized: {SpiderClass.__name__}")
            print(f"Spider: {spider}")

            # Events
            events = spider.get_events()
            for ev in events:
                handle_event(db, ev, spider)

            # Prayer Times (if available)
            if hasattr(spider, "get_prayer_times"):
                prayer_times = spider.get_prayer_times()
                for pt in prayer_times:
                    handle_prayer_time(db, pt, spider)

        except Exception:
            logger.exception('Failed processing %s', SpiderClass.__name__)

    db.update_old_activity()
    db.close_connection()
    logger.info('Pipeline complete')


if __name__ == '__main__':
    run_pipeline()
