from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Projects, Report

class UserProjectsInline(admin.TabularInline):
    model = User.projects.through
    extra = 1

class UserAdmin(BaseUserAdmin):
    inlines = [UserProjectsInline]

    list_display = ('username', 'first_name', 'last_name', 'birthday', 'tg_id')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

admin.site.register(User, UserAdmin)
admin.site.register(Projects)
admin.site.register(Report)


