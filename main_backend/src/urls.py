from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('store.api.v1.urls')),
    path('api/v1/', include('users.api.v1.urls')),
    path('api/v1/', include('orders.api.v1.urls')),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT})
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT})