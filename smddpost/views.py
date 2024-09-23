from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics, status, parsers

from . models import Post, Comment
from smddapp. models import Profile
from . serializers import *

# posts of the current logged in user
class UserPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        current_user_name = request.user.username
        # if str(username).lower() != str(current_user_name).lower():
        #     raise Http404
        post = Post.objects.filter(profile__user__username__iexact=request.user.username).all()
        serializer = PostDetailViewSerializer(post ,many=True, context={"request" : request})
        return Response(serializer.data)
    
# Post Detail View   
class PostDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        post = Post.objects.filter(id=id).first()
        print(post)
        serializer = PostDetailViewSerializer( post, many=False, context = {"request" : request} )
        return Response(serializer.data)
    
# Profile of each post
class PostProfileViewView (APIView):
    def get(self, username, request):
        pass
    
class PostDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        post = Post.objects.filter(id=id).delete()
        return Response({"detail" : "Post deleted succesfully!"}, status=status.HTTP_200_OK)

# Post create View
class PostCreateView( generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [ parsers.MultiPartParser, parsers.FormParser]
    serializer_class = PostCreateSerializer

    def post(self, request):
        clean_data = request.data
        profile = Profile.objects.filter(user=request.user).first()
        serializer = self.serializer_class(data=clean_data, context={"request" : request})

        if serializer.is_valid( raise_exception=True):
            serializer.create_post(clean_data, profile)
            print("serializer not valid")
        else:
            print("serializer not valid")
        return Response(serializer.data)
    
class PostUpdateView( generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, id):
        data = request.data
        post = Post.objects.filter(
        id= id
        ).first()
        post.title =data['title']
        post.caption=data['caption']
        post.picture=data["picture"]
        post.save()
        return Response(status=status.HTTP_200_OK)
    
"""Comment Views"""
class PostCommentView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, id):
        comment = Comment.objects.filter(post__id=id).all()
        serializer = PostCommentSerializer(comment, many=True)
        return  Response(serializer.data)
    
class PostCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostCommentCreateSerializer
    queryset =Comment.objects.all()

    def post(self, request, id):
        clean_data = request.data
        current_user = request.user
        post = Post.objects.filter( id=id).first()
        serializer = self.get_serializer(data=clean_data)
        if serializer.is_valid( raise_exception=True):
            serializer.create_comment( clean_data, post, current_user)
        return  Response(serializer.data)
    
class PostLikeAddView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, id=None):
        if id is not None:
            try : 
                post =Post.objects.filter(id=id).first()
            except Exception :
                return Response({"detail" : "Not Found"},status=status.HTTP_404_NOT_FOUND)
        likes = post.likes.all()
        serializer =PostUserSerializer (likes, many=True)
        return Response( serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, id=None):
        if id is not None:
            try : 
                post =Post.objects.filter(id=id).first()
            except Exception :
                return Response({"detail" : "Not Found"},status=status.HTTP_404_NOT_FOUND)
        post.likes.add(request.user)
        return Response( status=status.HTTP_200_OK)
    
    def delete(self,request, id=None):
        if id is not None:
            try : 
                post =Post.objects.filter(id=id).first()
            except Exception :
                return Response({"detail" : "Not Found"},status=status.HTTP_404_NOT_FOUND)
        likes = post.likes.remove(request.user)
        return Response( status=status.HTTP_200_OK)