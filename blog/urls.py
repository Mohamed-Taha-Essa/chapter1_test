# blog/urls.py
# This module defines the URL patterns for the blog app.
# Each pattern maps a URL path to a specific view function.
# These URLs are "included" into the project's main urls.py
# using: path('blog/', include('blog.urls'))

from django.urls import path
# "path" is Django's function for defining URL routes.
# It takes: route string, view function, and an optional name.

from . import views
# Import the views module from the current app (blog).
# This gives us access to views.post_list and any future view functions.


# "app_name" sets a namespace for this app's URLs.
# This allows you to reference URLs as 'blog:post_list' in templates
# and avoid naming conflicts with other apps that might have
# a view also named 'post_list'.
app_name = 'blog'

# urlpatterns — A list of URL patterns that Django checks (in order)
# when a request comes in. The first matching pattern is used.
urlpatterns = [
    # path('', ...) — Matches the root URL of this app.
    # Since the project includes this as 'blog/', the full URL is: /blog/
    # "views.post_list" — The view function to call when this URL is matched.
    # "name='post_list'" — A unique name for this URL pattern.
    #     You can use it in templates: {% url 'blog:post_list' %}
    #     and in Python code: reverse('blog:post_list')
    path('', views.post_list, name='post_list'),
]
