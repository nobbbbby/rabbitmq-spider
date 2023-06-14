import pika as pika


def connect2rabbit(settings):
    config = settings
    credentials = pika.PlainCredentials(username=config.get('RABBIT_USERNAME', 'guest'),
                                        password=config.get('RABBIT_PASSWORD', 'guest'))

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.get('RABBIT_HOST', 'localhost'),
                                  port=config.get('RABBIT_PORT', 5672),
                                  credentials=credentials,
                                  virtual_host=config.get('RABBIT_VIRTUAL_HOST',
                                                          '/')))
    return connection.channel()
