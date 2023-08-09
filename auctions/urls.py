from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name = "create"),
    path("<int:auction_id>", views.item, name = "item"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("bid", views.bid, name = "bid"),
    path("closed",views.closed,name = "closed"),
    path("<str:Category>", views.category, name = "category")
]
