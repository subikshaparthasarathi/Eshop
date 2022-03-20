
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include
from .import settings
from django.conf.urls.static import static
from store import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('activate/<uidb64>/<token>', views.activate, name="activate")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
