from django.urls import path, include
from .views import library_map
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, library_map, proximity_search

router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('map/', library_map, name='library_map'),
    path('proximity/', proximity_search, name='library-proximity'),
]
