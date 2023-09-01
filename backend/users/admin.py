from django.contrib import admin
from users.models import User, Follow



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass

