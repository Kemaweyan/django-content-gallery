from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # set the root URL for the Content Gallery app
    url(r'^gallery/', include('content_gallery.urls')),
    url(r'^testapp/', include('testapp.urls')),
    url(r'^$', RedirectView.as_view(pattern_name="testapp:cat_list")),
]

# serve images from MEDIA_ROOT directory in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
