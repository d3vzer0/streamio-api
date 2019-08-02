from app import app
import requests
import json


class Streaming:
    def __init__(self, faust_host=app.config['FAUST_HOST'], scraper_agent=app.config['SCRAPER_AGENT']):
        self.faust_host = faust_host
        self.scraper_agent = scraper_agent

    def state(self):
        url = '{0}/filters/state'.format(self.faust_host)
        get_state = requests.get(url)
        return get_state.json()

    async def refresh(self, refresh_type):
        url = '{0}/filters/{1}'.format(self.faust_host, refresh_type)
        refresh_filter = requests.get(url)
        return refresh_filter.json()

    async def confirm(self, target_url, state):
        url = '{0}/matches/confirm'.format(self.faust_host)
        confirm_url = requests.post(url, json={'url': target_url, 'state':state})
        return confirm_url.json()

    async def screenshot(self, target_url):
        url = '{0}/scrape/screenshot'.format(self.scraper_agent)
        screenshot_url = requests.post(url, json={'url': target_url })
        return screenshot_url.json()
