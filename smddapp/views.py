
from django.contrib.auth import get_user_model, login, logout
from django.http import Http404

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str ,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, status, authentication, generics, parsers
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


from . serializers import *
# Create your views here.
from.models import User, Profile
from smddpost.models import Post, Comment

#Public Users View
class Userview (generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [authentication.SessionAuthentication]
    filter_backends = [DjangoFilterBackend,SearchFilter ]
    search_fields = ["username"]

    # def get(self, request):
    #     current_user = request.user
    #     serializer= self.serializer_class(current_user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    
class Usersview (APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [authentication.SessionAuthentication]
    def get(self, request, username):
        user = Profile.objects.filter(user__username=username).first()
        serializer= PublicUsersSerializer(user, context = {"request" : request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                print(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
class LoginView(generics.CreateAPIView):

    permission_classes = [permissions.AllowAny]
    authentication_classes = [authentication.SessionAuthentication]
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def  post(self, request):
         clean_data = request.data
         serializer = self.get_serializer(data=clean_data)
         if serializer.is_valid(raise_exception=True):
             user = serializer.check_user(clean_data)
             login(request, user)
             return Response(serializer.data, status=status.HTTP_200_OK)
         
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
    
class sessionView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [authentication.SessionAuthentication]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"isAuthenticated": True})
        return Response({"isAuthenticated": False})
        
class PasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes= [authentication.SessionAuthentication]
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

    def patch(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success" : "Pasword reset success"}, status=status.HTTP_201_CREATED)
        return Response({"error" : "Pasword reset failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        
class PublicPostView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes =[authentication.SessionAuthentication]
    def get(self, request):
        queryset = Post.objects.all().order_by('?')
        print(queryset)
        serializer = PublicPostSerializer(queryset, many=True,  context={"request" : request})
        return Response(serializer.data)


class userProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def get(self, request, username):
        current_user = request.user.username
        if str(username).lower() != str(current_user).lower():
            raise Http404
        current_user = request.user.username
        
        profile = Profile.objects.filter(user__username__iexact=current_user).first()
        serializer= UserProfileSerializer( profile, many=False, context={"request" : request})
        return Response([serializer.data], status=status.HTTP_200_OK)
    
# Profile Update view

class UserProfileUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [authentication.SessionAuthentication]
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


    

        


    
        



        
