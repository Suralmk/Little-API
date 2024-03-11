from rest_framework import serializers
from .  models import  Post, Comment
from rest_framework.reverse import reverse

from smddapp.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()




class PostUserSerializer(serializers.Serializer):
    username = serializers.CharField()

class CommentsProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")
    username = serializers.CharField(source="user.username")
    class Meta:
        model = Profile
        fields = ["full_name", "username"]

class PostProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")
    username = serializers.CharField(source="user.username")
    class Meta:
        model = Profile 
        fields = ["username","full_name", "bio", "profile_pic", "bg_pic", "personal_intrests", "birth_date", "location" ]

class PostViewSerializer(serializers.Serializer):
    pass

class UserPostViewSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model=Post
        fields = ["url", "title", "caption", "picture"]


    def get_url(self, obj):
        return f"http://127.0.0.1:8000/users/{obj.profile.username}/profile/posts/{obj.id}/"
    

class PostDetailViewSerializer(serializers.ModelSerializer):
    comments_url = serializers.HyperlinkedIdentityField(view_name="post-comments-view", lookup_field="id")

    class Meta:
        model=Post
        fields = "__all__"


        
    def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url)


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "picture", "caption"]

    def create_post(self, clean_data, profile):
        print(clean_data)
        post =Post.objects.create(
            title=clean_data['title'],
            picture=clean_data['picture'],
            caption=clean_data['caption'],
            profile = profile
        )
        post.save()
        return post
    

# ====================================================
# Post Comment Serializer
# ====================================================
class PostCommentSerializer(serializers.ModelSerializer):

    comment = serializers.CharField()
    likes = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    owner = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model= Comment
        fields = "__all__"

    def get_owner(self, obj):
        profile = Profile.objects.get(user=obj.owner)
        serializer = CommentsProfileSerializer(profile, many=False)
        return serializer.data
    
class PostCommentCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ["comment"]

    def create_comment(self, clean_data, post, current_user):
        post =Comment.objects.create(
            post=post,
            owner=current_user,
            comment=clean_data['comment']
        )
        post.save()
        return post
    
# ====================================================
# Post Like Serializer
# ====================================================

class PostLikeSerializer(serializers.Serializer):
    likes = PostUserSerializer(read_only=True, many=False)