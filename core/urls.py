from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('offers/', include('offers_app.api.urls')),
    path('orders/', include('orders_app.api.urls')),
    path('profile/', include('profile_app.api.urls')),
    path('reviews/', include('reviews_app.api.urls')),  
]
