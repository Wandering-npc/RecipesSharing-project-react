from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_display = ('pk', 'username', 'email', 'get_follows_count', 'get_recipes_count')

    def get_follows_count(self, obj):
        return obj.following.count()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

admin.site.register(Follow)
