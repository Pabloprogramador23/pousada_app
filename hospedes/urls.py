from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HospedeViewSet

router = DefaultRouter()
router.register(r'hospedes', HospedeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
