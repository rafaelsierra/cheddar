# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from feeds.mixins import FeedListMixin

class FeedsListView(ListView, FeedListMixin):
    context_object_name = "book_list"
    post_read = False
    