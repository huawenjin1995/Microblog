#coding: utf-8
#对列表进行分页

import math
from flask import abort

class ListPagination(object):

    def __init__(self, iterable, page=1, per_page=15):

        if page < 1:
            abort(404)

        self.iterable = iterable
        self.page = page
        self.per_page = per_page

        self.total = len(iterable)

        start_index = (page - 1) * per_page
        end_index = page * per_page

        self.items = iterable[start_index:end_index]

        if not self.items and page != 1:
            abort(404)

    @property
    def pages(self):
        """The total number of pages"""
        return int(math.ceil(self.total / float(self.per_page)))

    def prev(self):
        assert self.iterable is not None, ('an object is required for this method to work')
        iterable = self.iterable
        return self.__class__(iterable, self.page -1, self.per_page)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self):
        assert self.iterable is not None, ('an object is required for this method to work')
        iterable = self.iterable
        return self.__class__(iterable, self.page + 1, self.per_page)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
               right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge or
                num > self.pages - right_edge or
                (num >= self.page - left_current and
                 num <= self.page + right_current)
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num
        if last != self.pages:
            yield None