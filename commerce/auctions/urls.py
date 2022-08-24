from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.add_listing, name="add"),
    path("item/<str:pk>", views.listing_page, name="listing"),
    path("item/<str:pk>/bid", views.bid,name="bid"),
    path('item/<str:pk>/close', views.close, name="close"),
    path('categories', views.category_list, name="categories"),
    path('categories/<str:cat>', views.category_index, name="category"),
    path('watchlist', views.watchlist, name='watchlist'),
    path('item/<str:pk>/watchlist_add', views.watchlist_add, name="watchlistadd"),
    path('item/<str:pk>/watchlist_remove', views.watchlist_remove, name="watchlist_remove"),
    path('my_listings', views.my_listings, name='my_listings'),
    path('<str:comment_id>/delete_comment', views.comment_delete, name="delete_comment")
]