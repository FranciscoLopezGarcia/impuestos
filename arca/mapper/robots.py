import time
import urllib.robotparser as robotparser
from urllib.parse import urlparse

from config import USER_AGENT, REQUEST_DELAY


class RobotsManager:
    def __init__(self, base_url: str):
        parsed = urlparse(base_url)
        self.robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        self.rp = robotparser.RobotFileParser()
        self.rp.set_url(self.robots_url)
        self.rp.read()

    def can_fetch(self, url: str) -> bool:
        return self.rp.can_fetch(USER_AGENT, url)

    def wait(self):
        time.sleep(REQUEST_DELAY)
