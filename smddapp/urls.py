from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . views import *

urlpatterns = [
    # public urls
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('token/', MyTokenPairView.as_view(), name='token_obtain_pair'),
    path("login/",LogInView.as_view(), name="login"),

    path('google-login/', convert_token, name='convert_token'),

    path ('register/', RegisterView.as_view(), ),

    path('users/', Userview.as_view()),
    path('users/search/', UserSearchSerializer.as_view()),
    path('users/suggestion/', UsersSuggestion.as_view()),
    path('users/<str:username>/', UserDetailview.as_view()),
    path('posts/', PublicPostView.as_view()),

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
    path("<str:username>/follow-status/", UserFollowingView.as_view()),

    # Posts View
    path("posts/", include("smddpost.urls")),
    path("premium/", include("premium.urls")),    
]