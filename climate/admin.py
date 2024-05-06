from django.contrib import admin
from climate.models import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'published_at')

    # def get_full_name(self, obj):
    #     return f"{obj.first_name} {obj.last_name}"
    # get_full_name.short_description = 'Full Name'

admin.site.register(News, NewsAdmin)
