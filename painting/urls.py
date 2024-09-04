
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('auth/', include('allauth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)

# urls.py
from django.conf.urls import handler400, handler403, handler404, handler500
from django.shortcuts import render

# Reference your custom error templates
def custom_bad_request(request, exception):
    return render(request, 'errors/400.html', status=400)

def custom_permission_denied(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_server_error(request):
    return render(request, 'errors/500.html', status=500)

# Set handlers for error pages
handler400 = 'painting.urls.custom_bad_request'
handler403 = 'painting.urls.custom_permission_denied'
handler404 = 'painting.urls.custom_page_not_found'
handler500 = 'painting.urls.custom_server_error'


