"""Primary URLConf handling."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('laborganizer/', include('laborganizer.urls')),
    path('teachingassistant/', include('teachingassistant.urls'))
]
