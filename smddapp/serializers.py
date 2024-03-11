from django.contrib.auth import get_user_model, authenticate, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import  force_str, smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse\



User = get_user_model()

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response

from . models import Profile
from smddpost.models import Post
from .utils import Util

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")

        if User.objects.filter(email=email).exists():
            raise ValidationError({"error" : "Email already exists!"})
        elif User.objects.filter(username=username).exists():
            raise ValidationError({"error" : "Username already exists"})
        return super().validate(attrs)
    
    def create(self, clean_data):
        user = User.objects.create_user(email=clean_data['email'],  
                                            username=clean_data['username'], 
                                            password=clean_data['password'],)
         
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()
        return user
    
class LoginSerializer(serializers.ModelSerializer): 
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "username","password"]

    def get_username(self, obj):
        user_email = obj['email']
        user = User.objects.filter(email=user_email).first()
        return user.username

    def check_user (self, clean_data):
        user = authenticate(email=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError("User not found")
        else:
            return user

class PassswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
            request = self.context.get('request')
            
            email = attrs.get('email', '')

            if User.objects.filter(email=email).exists():
                    user=User.objects.get(email=email)
                    uidb64=urlsafe_base64_encode(smart_bytes(user.id))
                    token = PasswordResetTokenGenerator().make_token(user)
                    current_site = get_current_site(request=request).domain
                    relative_link = reverse('reset-password-confirm', kwargs={'uidb64' : uidb64, 'token':token})
                    absurl = f'http://{current_site}{relative_link}'
                    email_body = f"Hello {user.username} \n\n Use this link bellow to reset your password \n {absurl}"
                    data = {
                        'email_body' : email_body, 
                        'to_email': user.email,
                        'email_subject' : 'Password Reset Request'
                        }
                    Util.send_email(data)

                    return super().validate(attrs)
            raise ValidationError("Email does not exist")
            


class CreateNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']


    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            print(user)

            if not PasswordResetTokenGenerator().check_token(user, token=token):
                
               raise AuthenticationFailed("The reset link is inavalid")
            
            user.set_password(password)
            user.save()
            return user
        
        except Exception as e:
            raise AuthenticationFailed("The reset link is inavalid")
        return super().validate(attrs)
  
class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "admin", "active", "staff","last_login"]

class PublicUsersPostSerializer(serializers.Serializer):
    pass

class PublicUsersSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="get_full_name")
    profile_pic = serializers.ImageField()
    bg_pic = serializers.ImageField()
    total_follower = serializers.IntegerField(source="get_total_follower")
    # total_following = serializers.IntegerField()
    bio = serializers.CharField()
    personal_intrests = serializers.CharField()
    location = serializers.CharField()
    posts = serializers.SerializerMethodField(read_only=True)

    def get_posts(self, obj):
        user_posts = Post.objects.filter(profile=obj).all()
        posts = PublicPostSerializer(user_posts, many=True, context = {"request" :self.context.get("request") })
        return [posts]
    
    def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url) 
     
class PublicUserSerializer(serializers.ModelSerializer):
       class Meta:
        model = User
        fields = ["username"]

class PublicProfileSerializer(serializers.ModelSerializer):
     full_name = serializers.CharField(source="get_full_name")
     username = serializers.CharField(source="user.username")
     class Meta:
         model = Profile
         fields = ["username","full_name", "bio", "profile_pic", "bg_pic", "personal_intrests", "birth_date", "location" ]


     def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url)

# Prfile Serializers
class UserProfileSerializer(serializers.ModelSerializer):
    user = ListUserSerializer(read_only=True)
    total_follower = serializers.IntegerField(source="get_total_follower")
    full_name = serializers.CharField(source="get_full_name")
    following = serializers.SerializerMethodField(read_only=True)
    follower = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"

    def get_following(self, obj):
        user = User.objects.filter(username=obj).first()
        followings = user.following.all()
        profiles = []
        for following in followings:
            followers_profile = Profile.objects.filter(user__username=following).first()
            serializer = PublicProfileSerializer(followers_profile, context={"request" : self.context.get("request")})
            profiles.append(serializer.data)
        return profiles
    

    def get_follower(self, obj):
        followers = obj.follower.all()
        profiles  = []
        for follower in followers:
            followers_profile = Profile.objects.filter(user=follower).first()
            serializer = PublicProfileSerializer(followers_profile, context={"request" : self.context.get("request")})
            profiles.append(serializer.data)
        return profiles
    
    def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url)
    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields = ["first_name", "last_name", "profile_pic", "bg_pic", "bio", "location", "birth_date", "phone", "personal_intrests"]

# Public Post Serialier
class PublicPostSerializer(serializers.ModelSerializer):
    """
    Serializers Post models to all user
    wheather they are logged or not logged in
    """
    post_url = serializers.HyperlinkedIdentityField(view_name="post-detail-view", lookup_field="id")
    comment_url = serializers.HyperlinkedIdentityField(view_name="post-comments-view", lookup_field="id")
    owner = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Post
        fields = "__all__"

    def get_owner(self, obj):
        profile = obj.profile
        serializer = PublicProfileSerializer(profile, many=False, context={"request" : self.context.get("request")})
        return serializer.data
        
    def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url)

class FollowerSerializer(serializers.ModelSerializer):
    follower = serializers.SerializerMethodField(read_only=True)
    following = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ["follower", "following"]

    def get_following(self, obj):
        user = User.objects.filter(username=obj).first()
        followings = user.following.all()
        profiles = []
        for following in followings:
            followers_profile = Profile.objects.filter(user__username=following).first()
            serializer = PublicProfileSerializer(followers_profile, context={"request" : self.context.get("request")})
            profiles.append(serializer.data)
        return profiles
    

    def get_follower(self, obj):
        followers = obj.follower.all()
        profiles  = []
        for follower in followers:
            followers_profile = Profile.objects.filter(user=follower).first()
            serializer = PublicProfileSerializer(followers_profile, context={"request" : self.context.get("request")})
            profiles.append(serializer.data)
        return profiles
    
class PublicUsersSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="get_full_name")
    profile_pic = serializers.ImageField()
    bg_pic = serializers.ImageField()
    total_follower = serializers.IntegerField(source="get_total_follower")
    # total_following = serializers.IntegerField()
    bio = serializers.CharField()
    personal_intrests = serializers.CharField()
    location = serializers.CharField()
    posts = serializers.SerializerMethodField(read_only=True)

    def get_posts(self, obj):
        user_posts = Post.objects.filter(profile=obj).all()
        print(user_posts)
        serializer = PublicPostSerializer(user_posts,  many=True, context = {"request" : self.context.get("request")})
        return serializer.data
    
    def get_photo_url(self, obj):
        request = self.context.get("request")
        url = obj.fingerprint.url
        return request.build_absolute_url(url) 
    
class UpdateEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=250)
    
    def validate(self, attrs):
        email = attrs.get("email")
        user = self.context.get("request").user
        if User.objects.filter(email=email).exists() :
            raise ValidationError({"error" : "Email is already taken!"})
        else:
            user.email = email
            user.save()
            attrs["user"] = user
        return super().validate(attrs)

class UpdateUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=250)

    def validate(self, attrs):
        username = attrs.get("username")
        user = self.context.get("request").user

        if User.objects.filter(username=username).exists():
            raise ValidationError({"error" : "Username is already taken"})
        else:
            user.username = username
            user.save()
        return super().validate(attrs)
    
class UpdatePaswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        user = self.context.get("request").user

        user.set_password(password)
        user.save()
        return super().validate(attrs)