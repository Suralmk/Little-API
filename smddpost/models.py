from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

import uuid
from smddapp.models import Profile




User = get_user_model()
# Create your models here.

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.profile.user.id, filename)


    


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=1000, verbose_name="post_title", null=True, blank=True)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="picture", null=True, blank=True, default="default_bg.png")
    caption = models.TextField(max_length=10000, verbose_name="caption")
    date_posted = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="like_user", blank=True, default="")
    shares = models.IntegerField(default=0)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE , related_name="post_profile" )

    def get_absolute_url(self):
        return reverse('post-details', args=[str(self.id)])
    
    def __str__(self) :
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name ="commented_post")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment = models.CharField(max_length = 300, null=True)
    likes = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)