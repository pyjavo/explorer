from django.urls import include, path
from django.views.generic import TemplateView

from . import views


app_name = "registers"
urlpatterns = [
    path('load-dataset', views.load_dataset, name='load_dataset'),
    path('process-dataset', views.process_dataset, name='process_dataset'),
    path('my-datasets', views.my_datasets, name='my_datasets'),
    path("<uuid:register_id>/", views.register_detail, name="detail"),
    path(
        "download/<uuid:register_id>/",
        views.download_new_dataset,
        name="download_new_dataset"
    ),
]
