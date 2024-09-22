from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .apps import MovieCollectionConfig
from .views import UserAPI

router = DefaultRouter()
app_name = MovieCollectionConfig.name

router.register(r'collection', views.CollectionAPI, basename='CollectionAPI')
router.register(r'movies', views.MovieAPI, basename='MovieAPI')
router.register(r'register', views.RegisterAPI, basename='RegisterAPI')
router.register(r'request-count', views.RequestDataAPI, basename='RequestDataAPI')
router.register(r'user', UserAPI, 'UserAPI')
router.register(r'db/movies', views.MoviesFromDbAPI, basename='MoviesFromDbAPI')
urlpatterns = [
]
urlpatterns += router.urls