import logging

from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)


class RabbitSpiderMiddleware:
    """auto ack message"""

    def _ack_rep(self, response, spider):
        tag = response.request.meta.pop('mq_tag', None)

        if tag:
            spider.server.basic_ack(delivery_tag=tag)
            logger.debug(f'Acked tag: {tag}')
            spider.crawler.stats.inc_value('rabbitmq/acked')

    def process_spider_output(self, response, result, spider):
        for r in result:
            if ItemAdapter.is_item(r):
                self._ack_rep(response, spider)
            yield r

    async def process_spider_output_async(self, response, result, spider):
        async for r in result:
            if ItemAdapter.is_item(r):
                self._ack_rep(response, spider)
            yield r

    def process_spider_exception(self, response, exception, spider):
        tag = response.request.meta.pop('mq_tag', None)
        if tag:
            spider.server.basic_nack(delivery_tag=tag)
            logger.warning(f'Nacked tag: {tag}, requeue to queue')
            spider.crawler.stats.inc_value('rabbitmq/nacked')
            spider.crawler.stats.inc_value('rabbitmq/requeued')
