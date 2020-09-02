# -*- coding: UTF-8 -*-

from random import randint
from time import time

import chardet
import orjson
from tornado.options import options
from tornado.log import access_log, app_log
from tornado.web import RequestHandler

try:
    from influxdb import InfluxDBClient
except ImportError:
    app_log.warning(
        'The InfluxDB Python Driver not installed. '
        'Widgets Simple Stat InfluxDB Module will NEVER be loaded.')
    InfluxDBClient = None


def _simple_stat_influxdb(app_name, handler, random_nonce):
    _influxdb = getattr(_simple_stat_influxdb, '_influxdb', None)
    if not _influxdb:
        _influxdb = InfluxDBClient.from_dsn(
            dsn=options.widgets_simple_stat_influxdb_dsn)
        try:
            _influxdb.create_database(
                dbname=f'widgets_stat_{app_name}')
            _influxdb.switch_database(
                database=f'widgets_stat_{app_name}')
            _simple_stat_influxdb._influxdb = _influxdb
        except Exception as e:
            app_log.warning(e)
    _influxdb = getattr(_simple_stat_influxdb, '_influxdb', None)
    if not _influxdb:
        app_log.warning('Simple Stat InfluxDB Module Load Error')
        return
    _influxdb.write_points([dict(
        measurement='request',
        tags=dict(
            path=handler.request.path,
            method=handler.request.method,
            status=handler.get_status(),
        ),
        fields=dict(
            random_nonce=random_nonce,
            ip=handler.request.remote_ip,
            latency=handler.request.request_time(),
        ),
    )])


def generate_widgets_default_log_request(app_name: str):

    def log_request(handler: RequestHandler):
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()

        random_nonce = f'{randint(0, 0xFFFFF):05X}{int(time() * 1e3):011X}'

        headers = orjson.dumps(
            dict(handler.request.headers.get_all()),
            option=orjson.OPT_SORT_KEYS | orjson.OPT_STRICT_INTEGER)
        if headers:
            log_method(f'[{random_nonce}] HEADERS: {headers.decode()}')
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
                    try:
                        log_method(f'[{random_nonce}] '
                                   f'BODY: {body.decode(encoding=encoding)}')
                    except UnicodeDecodeError:
                        try:
                            log_method(
                                f'[{random_nonce}] BODY: {body.decode()}')
                        except UnicodeDecodeError:
                            log_method(
                                f'[{random_nonce}] '
                                f'BODY: **HIDDEN (UnicodeDecodeError)**')

        log_method(
            f'[{random_nonce}] ' '%d %s %.2fms',
            handler.get_status(),
            handler._request_summary(),     # NOQA
            request_time,
        )

        if InfluxDBClient and options.widgets_simple_stat_influxdb_dsn:
            _simple_stat_influxdb(
                app_name=app_name, handler=handler, random_nonce=random_nonce)

    return log_request
