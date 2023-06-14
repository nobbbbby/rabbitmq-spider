import json

from scrapy import Request

from RabbitScrape.spiders import RabbitMQSpider


class YourSpider(RabbitMQSpider):
    """Demo"""
    name = 'demo'
    api = 'demo.queue'

    def make_request_from_data(self, data):
        msg_dict = json.loads(data)
        url = msg_dict['url']

        return Request(url)

    def parse(self, response, **kwargs):
        self.logger.debug(response.status)
