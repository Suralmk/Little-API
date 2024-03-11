from django.urls import path
from .views import *
urlpatterns = [
    path('user/',UserPostView.as_view() ),
    path('create/',PostCreateView.as_view() ),
    path('update/',PostUpdateView.as_view() ),

    path('<slug:id>/',PostDetailView.as_view(), name="post-detail-view" ),
    path('<slug:id>/profile/',PostProfileViewView.as_view(), name="post-profile-view" ),
    path('<slug:id>/delete/',PostDeleteView.as_view() ),
    # path('<slug:id>/update/',UserPostDeleteView.as_view() ),

    #comment urls
    path('<slug:id>/comments/',PostCommentView.as_view(), name="post-comments-view"),
    path('<slug:id>/comments/create/',PostCommentCreateView.as_view() ),
    path('<slug:id>/comments/delete/',UserPostCommentDeleteView.as_view() ),

    # Likes View 
    # path('<slug:id>/like/',PostLikeAddView.as_view(), name="post-comments-view"),
    path('<slug:id>/like/',PostLikeAddView.as_view() ),
    path('<slug:id>/like/delete/',PostLikeRemoveView.as_view() ),
]