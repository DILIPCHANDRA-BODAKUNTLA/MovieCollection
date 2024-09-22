import copy
import logging
import uuid
from datetime import datetime

from django.conf import settings
import re
from django.db import connection

from .models import RequestData


class MiddlewareAPI:
    ENVIRONMENT = settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else ''

    def __init__(self, get_response):
        self.start_time = datetime.now()
        self.flag = True
        self.get_response = get_response
        self.req_id = str(uuid.uuid4())

    @classmethod
    def get_processing_time(cls, start_time, end_time):
        processing_time = end_time - start_time
        return processing_time

    def process_request(self, request):
        self.req_id = str(uuid.uuid4())
        if self.flag:
            self.start_time = datetime.now()

    def process_response(self, request, response, request_body):
        total_time = self.get_processing_time(
            start_time=self.start_time, end_time=datetime.now())
        try:
            new_request_obj = self.build_request_tracking_obj(
                request, response, total_time, request_body)
            if self.ENVIRONMENT in ['DEV', 'PROD','LOCAL']:
                RequestData.objects.create(**new_request_obj)
        except Exception as e:
            logging.error(e)
        return response

    @staticmethod
    def _get_response_body(response):
        if response:
            try:
                if 'Content-Type' in response:
                    return str(response.content)
                if 'json' in response.headers.get('Content-Type', ''):
                    return str(response.content)
                else:
                    return 'Large Content.. ignored'
            except Exception as e:
                logging.error(msg=str(e))
        return ''

    @staticmethod
    def _convert_datetime_to_str(query_params: dict, request):
        for key in query_params:
            if isinstance(request.GET.get(key), datetime):
                query_params[key] = str(query_params[key])

    def build_request_tracking_obj(self, request, response, total_time, request_body) -> dict:
        user = request.user.id
        response_body = self._get_response_body(response)
        query_params = copy.deepcopy(request.GET)
        self._convert_datetime_to_str(query_params, request)
        new_request_obj = {"request_id": self.req_id, "user": user, "path": request.path,
                           "ip_address": request.META['REMOTE_ADDR'],
                           "cookies": dict(request.COOKIES),
                           "query_params": query_params,
                           "headers": str(request.META),
                           "client": str(
                               request.META.get('HTTP_CLIENT')),
                           "response_status": str(
                               response.status_code),
                           "body": str(request_body),
                           "method": request.method,
                           "response_data": response_body,
                           "node_id": settings.NODE_ID,
                           'execution_time': total_time,
                           'request_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                           "request_type": "incoming",
                           "query_count": request.query_count}
        return new_request_obj

    def __call__(self, request):
        connection.queries_log.clear()
        request_body = request.body
        self.process_request(request=request)
        response = self.get_response(request)
        query_cls = QueryCounter(_connection=connection)
        query_count = query_cls._count_queries()
        setattr(request, "query_count", query_count)
        self.process_response(request=request, response=response, request_body=request_body)
        response.headers["processor_node_id"] = settings.NODE_ID
        return response


class QueryCounter:
    select_pattern = re.compile(r'^SELECT ', re.IGNORECASE)
    insert_pattern = re.compile(r'^INSERT ', re.IGNORECASE)
    update_pattern = re.compile(r'^UPDATE ', re.IGNORECASE)
    delete_pattern = re.compile(r'\bDELETE\b', re.IGNORECASE)

    def __init__(self, _connection):
        self.connection = _connection

    def _count_queries(self):
        counts = {
            'SELECT': 0,
            'INSERT': 0,
            'UPDATE': 0,
            'DELETE': 0
        }

        if not hasattr(self.connection, 'queries') or not isinstance(self.connection.queries, list):
            raise ValueError("Connection object must have a 'queries' attribute that is a list.")

        for query in self.connection.queries:
            if 'sql' not in query:
                continue
            sql = query['sql']
            if QueryCounter.select_pattern.match(sql):
                counts['SELECT'] += 1
            elif QueryCounter.insert_pattern.match(sql):
                counts['INSERT'] += 1
            elif QueryCounter.update_pattern.match(sql):
                counts['UPDATE'] += 1
            elif QueryCounter.delete_pattern.search(sql):
                counts['DELETE'] += 1

        return counts

