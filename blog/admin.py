from django.contrib import admin
from .models import Post
# Register your models here.

# # Action function - takes 3 parameters
# def make_published(modeladmin, request, queryset):
#     """Change selected posts from Draft to Published"""
#     # queryset.update() performs bulk SQL UPDATE
#     # returns number of objects updated
#     updated_count = queryset.update(status=Post.Status.PUBLISHED)
#     # Optional: display confirmation message to admin user
#     modeladmin.message_user(request, f'{updated_count} post(s) marked as published.')

# # Set a nice display name for the action in dropdown
# make_published.short_description = 'Mark selected posts as published'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = [ 'status', 'created' ,'publish']
    search_fields = ['title' ,'body']
    ordering = ['publish']
    raw_id_fields = ['author']
    show_facets = admin.ShowFacets.ALWAYS
    
    # Register the action - add it to this list
    actions = ["make_published" , "make_draft"] 


    def make_published(self, request, queryset):
        """Change selected posts to Published"""
        print('user===>' , request.user)
        print('user_type' , request.user.is_superuser)
        print('request permissions' , request.user.get_all_permissions())
        print('request groups' , request.user.groups.all())

        if(not request.user.is_superuser):
            self.message_user(request, 'Only superusers can perform this action.', level='error')
            return


        draft_posts = queryset.filter(status=Post.Status.DRAFT)
        updated_count = draft_posts.update(status=Post.Status.PUBLISHED)
        self.message_user(request, f'{updated_count} post(s) marked as published.')
    make_published.short_description = 'Mark selected posts as published'

    def make_draft(self, request, queryset):
        """Change selected posts to Draft"""

        print("list_display:", self.list_display)       # ['title', 'slug', 'author', 'publish', 'status']
        print("list_filter:", self.list_filter)        # ['status', 'created', 'publish']
        print("search_fields:", self.search_fields)      # ['title', 'body']
        print("ordering:", self.ordering)           # ['publish']
        print("show_facets:", self.show_facets)
        
        print("model:", self.model)              # <class 'blog.models.Post'>
        print("app_label:", self.model._meta.app_label)  # 'blog'
        print("model_name:", self.model._meta.model_name)  # 'post'
            
        print("has_add_permission:", self.has_add_permission(request))  # True or False
        print("has_change_permission:", self.has_change_permission(request))  # True or False
        print("has_delete_permission:", self.has_delete_permission(request))  # True or False
        
        
        
        
        published_posts = queryset.filter(status=Post.Status.PUBLISHED)
        updated_count = published_posts.update(status=Post.Status.DRAFT)
        self.message_user(request, f'{updated_count} post(s) marked as draft.')
    make_draft.short_description = 'Mark selected posts as draft'