from django.contrib import admin
from django.urls import path
from search_app import views  # views modulini to'liq import qilamiz

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Bosh sahifa (qidiruv)
    path('', views.index, name='index'), 
    
    # Autosuggestion (avtomatik takliflar) uchun API
    path('suggest/', views.suggest, name='suggest'),
]