from django.urls import include, path
from rest_framework import routers

from .views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                    UsersViewSet)

router = routers.DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
