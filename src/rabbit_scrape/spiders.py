from time import sleep

from scrapy import Spider, signals
from scrapy.exceptions import DontCloseSpider

from . import connection


class RabbitMQSpider(Spider):
    """starts requests from rabbitmq"""
    routing_key = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = None
        self.retry_delay = None
        self.auto_ack = False

    def start_requests(self):
        """yield start requests from RabbitMQ."""
        yield from self.next_requests()

    def setup_rabbitmq(self, crawler):
        if not self.routing_key:
            self.routing_key = f'{self.name}:start_urls'

        self.server = connection.connect2rabbit(crawler.settings)
        self.retry_delay = crawler.settings.getint('RABBIT_RETRY_DELAY', 5)
        self.auto_ack = crawler.settings.getint('RABBITMQ_AUTO_ACK', False)
        self.declare_rabbitmq()
        self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def declare_rabbitmq(self):
        # declare exchange or queue
        self.server.queue_declare(self.routing_key)

    def next_requests(self):
        """ Provides a request to be scheduled.
        :return: Request object or None
        """
        while True:
            if self.server.is_closed:
                self.server = connection.connect2rabbit(self.crawler.settings)

            method_frame, header_frame, data = self.server.basic_get(queue=self.routing_key, auto_ack=self.auto_ack)
            if any([method_frame, header_frame, data]):
                tag = method_frame.delivery_tag
                try:
                    req = self.make_request_from_data(data)
                except:
                    self.logger.error(f'error msg {data}')
                    if not self.auto_ack:
                        self.crawler.stats.inc_value('rabbitmq/nacked')
                        self.server.basic_nack(tag, requeue=False)
                    return
                if not self.auto_ack:
                    req.meta['mq_tag'] = method_frame.delivery_tag
                self.crawler.stats.inc_value('rabbitmq/get')
                self.logger.debug(f'Start req url:{repr(req)}')
                yield req
            else:
                break

    def make_request_from_data(self, data):
        raise NotImplementedError(f'{self.__class__.__name__}.parse callback is not defined')

    def schedule_next_request(self):
        """ Schedules a request, if exists.
        :return:
        """

        self.crawler.engine.slot.start_requests = iter(self.next_requests())
        self.crawler.engine.slot.nextcall.schedule()

    def spider_idle(self):
        """ Waits for request to be scheduled.
        :return: None
        """
        self.logger.debug(f'The queue is empty, retry getting in {self.retry_delay}s...')
        sleep(self.retry_delay)
        self.server.basic_recover(requeue=True)
        self.schedule_next_request()
        raise DontCloseSpider

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.setup_rabbitmq(crawler)
        return spider
