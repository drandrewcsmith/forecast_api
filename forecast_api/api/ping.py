import falcon
import logging


_log = logging.getLogger(__name__)


class PingResource(object):
    def __init__(self):
        pass

    def on_get(self, request, response):
        try:
            response.status = falcon.HTTP_OK
            response.body = 'pong'

        except Exception:
            _log.exception('problem ponging the ping')
            response.status = falcon.HTTP_INTERNAL_SERVER_ERROR
