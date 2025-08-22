from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/stock_updates/', consumers.StockConsumer.as_asgi()),
]
