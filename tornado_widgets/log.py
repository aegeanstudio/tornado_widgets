# -*- coding: UTF-8 -*-

import json
from random import randint
from time import time

import chardet
from tornado.log import access_log
from tornado.web import RequestHandler


def widgets_default_log_request(handler: RequestHandler):
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()

    random_nonce = f'{randint(0, 0xFFFFF):05X}{int(time() * 1e3):011X}'

    headers = json.dumps(dict(handler.request.headers.get_all()))
    if headers:
        log_method(f'[{random_nonce}] HEADERS: {headers}')
    query = handler.request.query
    if query:
        log_method(f'[{random_nonce}] QUERY: {query}')
    if handler.request.method.upper() not in ('GET', 'OPTIONS'):
        content_type = handler.request.headers.get('Content-Type', '')
        if not content_type:
            log_method(f'[{random_nonce}] '
                       f'BODY: **HIDDEN (Missing Content-Type)**')
        elif content_type.lower().startswith('multipart/form-data'):
            log_method(f'[{random_nonce}] '
                       f'BODY: **HIDDEN (multipart/form-data Detected)**')
        else:
            body = handler.request.body
            if body:
                encoding = chardet.detect(body)['encoding'] or 'utf-8'
                log_method(f'[{random_nonce}] '
                           f'BODY: {body.decode(encoding=encoding)}')

    log_method(
        f'[{random_nonce}] ' '%d %s %.2fms',
        handler.get_status(),
        handler._request_summary(),     # NOQA
        request_time,
    )
