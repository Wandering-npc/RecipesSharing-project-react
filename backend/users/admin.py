from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')


admin.site.register(Follow)

