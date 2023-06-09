from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("home/", views.home, name='home'),
    path("<int:id>", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("view/", views.view, name="view"),
    # path("event/<slug:slug>", views.search, name="search")
]