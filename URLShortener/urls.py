from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('useraccounts.urls')),
    path('', include('shortener.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path('media/<path:path>', login_required(serve), {'document_root': settings.MEDIA_ROOT}),
    ]