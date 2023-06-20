# rabbitmq-spider

rabbitmq-spider is an open-source tool that helps with web scraping by using RabbitMQ and Scrapy to distribute and scale
scraping tasks across multiple instances.

Inpsired by [scrapy-redis](https://github.com/rmax/scrapy-redis).

## Features

1. It only uses RabbitMQ for message generation tasks and does not use RabbitMQ to implement Scrapy’s queue.
2. It can automatically acknowledge (ack) or negatively acknowledge (nack) messages based on the response results.

## Installation 

```shell
pip install rabbitmq_spider
```
## Usage

### 1.Add config values:

```python
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = '5672'
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
RABBITMQ_VIRTUAL_HOST = '/'

SPIDER_MIDDLEWARES = {
    'rabbitscrape.middlewares.RabbitmqSpiderMiddleware': 49,
}
```

### 2.Add RabbitMQSpider to your spider

```python
import json

from rabbitmq_spider.spiders import RabbitMQSpider
from scrapy import Request


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
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
