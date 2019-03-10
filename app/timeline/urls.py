from django.urls import path, include
from rest_framework.routers import DefaultRouter

from timeline import views


router = DefaultRouter()
router.register('posts', views.PostViewSet)

app_name = 'timeline'

urlpatterns = [
    path('', include(router.urls))
]
