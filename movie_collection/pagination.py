from collections import OrderedDict
from functools import cached_property

from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .constants import Constant
from user_collections.settings import env


class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # check if custom_count is set
        if hasattr(self.object_list, 'custom_count'):
            return self.object_list.custom_count
        try:
            return self.object_list.values('pk').count()
        except Exception as e:
            print(e)
        return super(FasterDjangoPaginator, self).count

class CustomPageNumberPagination(PageNumberPagination):
    page_size = env(Constant.DEFAULT_PAGE_SIZE)
    page_size_query_param = "page_size"
    django_paginator_class = FasterDjangoPaginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', OrderedDict([
                ('current_page', self.page.number),
                ('next_page', self.page.next_page_number() if self.page.has_next() else None),
                ('prev_page', self.page.previous_page_number() if self.page.has_previous() else None),
                ('total_pages', self.page.paginator.num_pages),
                ('page_size', self.page.paginator.per_page),
                ('count', self.page.paginator.count),
                ('source', 'db'),
            ])),
            ('links', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
            ])),
            ('results', data)
        ]))

