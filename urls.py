from django.urls import path

from .views import index_view, api_v2_replacements, api_v2_notifications

urlpatterns = [
    path('', index_view),
    path('webapp/', index_view),
    path('v2.0/replacements/', api_v2_replacements),
    path('v2.0/replacements/<str:date>/', api_v2_replacements),
    path('v2.0/replacements//<str:schoolclass>', api_v2_replacements),
    path('v2.0/replacements/<str:date>/<str:schoolclass>', api_v2_replacements),
    path('v2.0/notifications/', api_v2_notifications),
    path('v2.0/notifications/<str:date>/', api_v2_notifications),
]
