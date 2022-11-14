
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .product_stock.urls import urlpatterns as product_stock_urls
from .account.urls import urlpatterns as account_urls
from .core import views as core_views

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r"^index/", core_views.index, name="index"),
    re_path(r"^product-stock/", include((product_stock_urls,"product_stock"), namespace="product_stock")),
    re_path( r"^account/", include( (account_urls, "account"), namespace="account" ) ),
    re_path( r'^robots.txt$', lambda r: HttpResponse( "User-agent: *\nDisallow: /",
                                                  content_type="text/plain"
                                                  )
         ),
]
