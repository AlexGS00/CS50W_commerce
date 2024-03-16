from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("mylistings", views.my_listings, name="my_listings"),
    path("category/<str:category>", views.view_category, name="category"),
    path("create", views.create_listing, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.view_listing, name="listing"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.view_watchlist, name="watchlist"),
    path("bid/<int:listing_id>", views.add_bid, name="bid"),
    path("close/<int:listing_id>", views.close, name="close")
]
