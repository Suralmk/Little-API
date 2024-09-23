
from django.contrib.auth import get_user_model, login, logout
from django.http import Http404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str ,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, status, authentication, generics, parsers, pagination
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view

from . serializers import *
# Create your views here.
from.models import User, Profile
from smddpost.models import Post
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from . utils import generate_username
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        profile = Profile.objects.filter(user=user).first()
        profile_data = UserProfileSerializer(profile, context = {"request" : cls}).data
        print(profile_data)
        token["profile"] = profile_data
        return token

@api_view(["GET"])
def index(request):
    return Response({"Project": "Little Social media website by Surafel Melaku"})

def get_auth_for_user(user, request):
    token =  RefreshToken.for_user(user)
    profile = Profile.objects.filter(user=user).first()
    profile_data = UserProfileSerializer(profile, context = {"request" : request}).data
    token["profile"] = profile_data
    return {
                "access" : str(token.access_token),
                "refresh" : str(token)
            }

@csrf_exempt
@api_view(['POST'])
def convert_token(request):
    code = request.data.get('code')  

    token_info_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={code}'
    google_response = requests.get(token_info_url)
    token_data = google_response.json()

    if 'error' in token_data:
        return Response({'error': token_data['error'], 'error_description': token_data.get('error_description')}, status=400)

    email = token_data.get('email')
    name = token_data.get('name')
    first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')

    demo_username = generate_username(first_name)

    print(token_data, "token data")
    for user in User.objects.all():
        if user.username == demo_username:
            demo_username = generate_username(first_name)
        pass

    try:
        user = User.objects.get(email=email)
        user_data = get_auth_for_user(user, request)
        return Response(user_data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:

        user = User.objects.create(
            email=email,
            username=demo_username,
            provider =True
        )
        
        user.set_unusable_password() 
        
        user.save()
        profile = Profile.objects.create(user=user, first_name=first_name, last_name=last_name)
        profile.save()
        tokens = get_auth_for_user(user, request)
        return Response(tokens, status=status.HTTP_201_CREATED)


#Public Users View
class Userview (generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend,SearchFilter ]
    search_fields = ["username"]

class UserSearchSerializer(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = SearchSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend,SearchFilter ]
    search_fields = ["first_name", "last_name" ,"user__username"]

class UsersSuggestion(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        profiles = Profile.objects.all().exclude(user=request.user)
        print(request.user.following.all())
        not_following = [profile for profile in  profiles if profile not in request.user.following.all()]
        data = []
        for profile in  not_following:
            serialozed_data = PublicProfileSerializer(profile,  context = {"request" : request}).data
            data.append(serialozed_data)
        return Response(data)

class UserDetailview (APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, username):
        user = Profile.objects.filter(user__username=username).first()
        if user:
            serializer= PublicUsersSerializer(user, context = {"request" : request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class LogInView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MyTokenObtainPairSerializer 

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(email=email, password=password)
        if not user:
            return Response({"detail" : "User with these credentials does not exist!"}, status=status.HTTP_401_UNAUTHORIZED)
        user_data = get_auth_for_user(user, request)
        return Response(user_data, status=status.HTTP_200_OK)
        
class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer
    authentication_classes = [authentication.SessionAuthentication]

    def post(self, request):
        clean_data = request.data
        serializer = self.get_serializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                tokens = get_auth_for_user(user, request)
                return Response(tokens, status=status.HTTP_201_CREATED)
         
class PasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PassswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request' : request})
        if serializer.is_valid(raise_exception=True):
            print('valid')
            return Response({'success':'Password reset link is succesfully send to your email.' }, status=status.HTTP_200_OK)
        return Response({"error" : "Email is not valid"}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetCheckAPIView(APIView):
    def get(self,request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token=token):
                return Response({"error" : "Token is not valid please request a new one!"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"valid": True, 'message': "Credentials are valid", "uidb64":uidb64, 'token': token }, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as e:
            return Response({"error" : "Token is not valid please request a new one!"}, status=status.HTTP_401_UNAUTHORIZED)

class CreateNewPasswordView(generics.CreateAPIView):
    serializer_class = CreateNewPasswordSerializer
    permission_classes =[permissions.AllowAny]

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success" : "Pasword reset success"}, status=status.HTTP_201_CREATED)
        return Response({"error" : "Pasword reset failed"}, status=status.HTTP_400_BAD_REQUEST)
    
class PublicPostView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.all()
    serializer_class = PublicPostSerializer

class userProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, username):
        current_user = request.user.username
        if str(username).lower() != str(current_user).lower():
            raise Http404
        current_user = request.user.username
        profile = Profile.objects.filter(user__username__iexact=current_user).first()
        serializer= UserProfileSerializer( profile, many=False, context={"request" : request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserProfileUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [ parsers.MultiPartParser, parsers.FormParser]
    
    def put(self, request, username):
        if username is not None:
            clean_data = request.data
            profile = Profile.objects.filter(user__username__iexact=username).first()
            serializer = ProfileUpdateSerializer(profile, data=clean_data, context = {"request" : request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
"""
User Following View and Following other users view
"""
class UserFollowingView(APIView):
     
     permission_classes = [permissions.IsAuthenticated]
     
     def get(self, request, username):
        current_user_name = request.user.username
        if str(username).lower() != str(current_user_name).lower():
            raise Http404
        current_user_profile = Profile.objects.filter(user=request.user).first()
        serializer=FollowerSerializer(current_user_profile, many=False, context={"request" : request})
        return Response(serializer.data, status=status.HTTP_200_OK)

     def post(self, request, username):
        current_user_name = request.user.username
        
        if str(username).lower() != str(current_user_name).lower():
            raise Http404
       
        try: 
             following = request.data["follow"].strip()
             if following is not None:
                following_user = Profile.objects.filter(user__username=following).first()
                if following_user in request.user.following.all():
                    return Response({"detail" : f"You already follow {following}"})
                elif following != str(request.user.username):
                    following_user.follower.add(request.user)
                    return Response({"detail" : f"You have followed {following}"})
             else:
                return Response({"detail" : "You can not follow yourself!"})
        except Exception as e:
             print(e)

        return Response({"detail" : "specify a user to follow!"})
        
     def put(self, request, username):
        current_user_name = request.user.username
        if str(username).lower() != str(current_user_name).lower():
            raise Http404
        try: 
             following = request.data["follow"].strip()
             if following is not None:
                following_user = Profile.objects.filter(user__username=following).first()
                following_user.follower.remove(request.user)
                return Response({"detail" : f"You have unfollowed {following}"})
             else:
                return Response({"detail" : "specify a user to follow!"})
        except Exception as e:
             print(e)

        return Response({"detail" : "specify a user to follow!"})
     
class UpdateEmailView(generics.UpdateAPIView):
    serializer_class = UpdateEmailSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        return Response({"success" : "Email Updated Succesfully"})
    
class UpdateUsernameView(generics.UpdateAPIView):
    serializer_class = UpdateUsernameSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        return Response({"success" : "Username Updated Succesfully"})
    
class UpdatePasswordView(generics.UpdateAPIView):
    serializer_class = UpdatePaswordSerializer

    def put(self, request):
        serializer = self.serializer_class(data=request.data, context={"request" : request})
        serializer.is_valid(raise_exception=True)
        return Response({"success" : "Password Updated Succesfully"})       