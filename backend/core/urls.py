from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .yasp import urlpatterns as dock_urls



urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/', include('profiles.urls')),
    path('posts/', include('posts.urls')),
    path('posts/', include('comments.urls')),
    path('chat/', include('chat.urls')),
]

urlpatterns += dock_urls

if settings.DEBUG:
    urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
