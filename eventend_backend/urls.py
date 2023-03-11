from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from mpesa.urls import mpesa_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('api.urls', namespace = 'api')),
    path('mpesa/', include(mpesa_urls)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
