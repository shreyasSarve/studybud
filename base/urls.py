from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create_room/", views.createRoom, name="createroom"),
    path("update_room/<str:pk>/", views.updateRoom, name="updateroom"),
    path("datele_room/<str:pk>/", views.deleteRoom, name="deleteroom"),
    path("datele_message/<str:pk>/", views.deleteMessage, name="deletemessage"),
    path("profile/<str:pk>/", views.userProfile, name="userprofile"),
    path("updateprofile/", views.updateProfile, name="updateprofile"),
    path("topics/", views.topicsPage, name="topics"),

]
