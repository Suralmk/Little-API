from django.contrib import admin
from . models import User,  Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ['email','username',  'active','staff', 'admin']
    class Meta:
        model = User
        fields = "__all__"
admin.site.register(User, UserAdmin)
admin.site.register(Profile)


