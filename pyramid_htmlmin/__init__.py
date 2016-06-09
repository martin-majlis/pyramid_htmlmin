"""
Binding betwen Pyramid and htmlmin

"""

import logging

from pyramid.tweens import INGRESS
from pyramid.request import Response
from pyramid.settings import asbool
from htmlmin import minify


__version__ = '0.4'

log = logging.getLogger(__name__)
htmlmin_opts = {}


def accepts_gzipped(request):
    return 'gzip' in [encoding.strip() for encoding in
                      request.headers['Accept-Encoding'].split(',')]


def htmlmin_tween_factory(handler, registry):
    def tween_view(request):
        response = handler(request)
        try:
            if (response.content_type and
                    response.content_type.startswith('text/html')):
                response.text = minify(response.text, **htmlmin_opts)
                if accepts_gzipped(response):
                    response.encode_content('gzip')

        except Exception:
            log.exception('Unexpected exception while minifying content')
        return response

    return tween_view


def includeme(config):
    """
    Add pyramid_htmlmin n your pyramid include list.
    """
    log.info('Loading htmlmin pyramid plugin')
    for key, val in config.registry.settings.items():
        if key.startswith('htmlmin.'):
            log.debug('Setup %s = %s' % (key, val))
            htmlmin_opts[key[8:]] = asbool(val) 

    config.add_tween('pyramid_htmlmin.htmlmin_tween_factory', under=INGRESS)
