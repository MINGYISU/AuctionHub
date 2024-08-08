from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"), 
    path("register", views.register, name="register"), 
    path("create", views.create, name="create"), 
    path("display/<str:identity>", views.display, name="display"), 
    path("placebid/<str:identity>", views.place_bid, name="placebid"), 
    path("changewl/<str:identity>", views.change_wl, name="changewl"), 
    path("watchlist", views.show_watchlist, name="showwatchlist"), 
    path("close/<str:identity>", views.close, name="close"), 
    path("comment/<str:identity>", views.write_comment, name="comment"), 
    path("sellinglist", views.sell_list, name="selllist")
]
