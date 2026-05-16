from django.contrib import admin
from .models import Post
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = [ 'status', 'created' ,'publish']
    search_fields = ['title' ,'body']
    ordering = ['publish']
    show_facets = admin.ShowFacets.ALWAYS 

    class Meta:
        model = Post
        fields = '__all__'
