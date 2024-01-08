import json
import logging
import os
import time
import urllib.parse
from datetime import datetime, date, timedelta

from selenium.webdriver.common.by import By
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.common.exceptions import WebDriverException


logger = logging.getLogger('hellodump')


class HelloWattExporter:

    def __init__(self):
        try:
            self.driver = webdriver.Firefox()
            self.authenticate()
            time.sleep(2)
        except Exception as e:
            logger.exception(f'A {e.__class__} exception occurred.')
            self.close()

    def close(self) -> None:
        if self.driver is not None:
            self.driver.close()
            self.driver.quit()

    def export(self, day: str | date):
        try:
            self.export_day_consumption(day)
        except Exception as e:
            logger.exception(f'A {e.__class__} exception occurred.')
            self.close()

    def authenticate(self):
        self.driver.get("https://www.hellowatt.fr/mon-compte/me-connecter")
        self.driver.implicitly_wait(2)

        email_box = self.driver.find_element(by=By.XPATH, value="//input[@name='login' and @class='Input']")
        email_box.send_keys(os.getenv('HW_EMAIL'))

        password_box = self.driver.find_element(by=By.XPATH, value="//input[@name='password' and @class='Input']")
        password_box.send_keys(os.getenv('HW_PASSWORD'))

        submit_button = self.driver.find_element(by=By.XPATH, value="//button[@form='loginUserForm']")
        submit_button.click()

    def export_day_consumption(self, day: date | str):
        if isinstance(day, str):
            day = date.fromisoformat(day)
        logger.debug(f'Exporting day consumption for "{day.isoformat()}".')
        start_date = datetime.combine(day, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        start_date = start_date.astimezone().isoformat(timespec='seconds')
        end_date = end_date.astimezone().isoformat(timespec='seconds')
        url = f"https://www.hellowatt.fr/api/homes/667580/sge_measures/courbe?" \
              + urllib.parse.urlencode({'startDate': start_date, 'endDate': end_date})
        self.driver.get(url)
        for request in self.driver.requests:
            if request.response and request.url == url:
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                data = json.loads(body.decode('utf-8'))

                os.makedirs('./data/raw/', exist_ok=True)
                with open(f'./data/raw/{day.isoformat()}.json', 'w+') as fd:
                    json.dump(data, fd, indent=4)


if __name__ == '__main__':
    hw = HelloWattExporter()
    export_date = date.fromisoformat('2023-12-24')
    while export_date < date.fromisoformat('2024-01-08'):
        hw.export(export_date)
        export_date += timedelta(days=1)
    hw.close()
