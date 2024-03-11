from django.urls import path, include
from . views import *
urlpatterns = [
    # public urls
    
    path ('register/', RegisterView.as_view(), ),
    path ('login/', LoginView.as_view(), ),
    path ('logout/', LogoutView.as_view(), ),

    path('users/', Userview.as_view()),
    path('users/<str:username>/', Usersview.as_view()),
    path('posts/', PublicPostView.as_view()),

    # Session View
    path('session/', sessionView.as_view()),

    # Password reset Views
    path("reset-password/",PasswordResetView.as_view(), name='reset-password' ),
    path("reset-password/<uidb64>/<token>/",PasswordResetCheckAPIView.as_view(), name='reset-password-confirm' ),
    path("create-password/",CreateNewPasswordView.as_view(), name='create-password' ),

    # Profile Update urls
    path('update-email/' , UpdateEmailView.as_view(), name="update-email"),
    path('update-username/' , UpdateUsernameView.as_view(), name="update-username"),
    path('update-password/' , UpdatePasswordView.as_view(), name="update-password"),
    # Profile View
    path("<str:username>/", userProfileView.as_view()),
    path("<str:username>/update/", UserProfileUpdate.as_view()),

    # following View
    path("<str:username>/follow/", UserFollowingView.as_view()),

    # Posts View
    path("posts/", include("smddpost.urls")),

    

    
]