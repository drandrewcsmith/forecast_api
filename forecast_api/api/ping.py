from falcon import HTTP_OK
import logging


_log = logging.getLogger(__name__)


class PingResource(object):

    def on_get(self, request, response):

        response.status = HTTP_OK
        response.body = 'pong'
