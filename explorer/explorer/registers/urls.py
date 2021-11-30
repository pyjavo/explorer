from django.urls import include, path
from django.views.generic import TemplateView

from . import views


app_name = "registers"
urlpatterns = [
    #path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path('load-dataset', views.load_dataset, name='load_dataset'),
    path('process-dataset', views.process_dataset, name='process_dataset'),
]
