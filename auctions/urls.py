from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_listing, name="new"),
    path("listing/<str:key>", views.view_listing, name="listing"),
    path("category/<str:categ>", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("mylistings", views.mylistings, name="mylistings"),
    path("won", views.won, name="won")
]
