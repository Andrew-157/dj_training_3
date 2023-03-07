from django.contrib import admin
from .models import Article


@admin.register(Article)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['topic', 'content', 'author', 'pub_date', 'tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
