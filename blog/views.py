# blog/views.py
# This module contains all view functions for the blog app.
# Views handle HTTP requests, fetch data from the database,
# and return HTTP responses (usually rendered HTML templates).

from django.shortcuts import render
# "render" is a Django shortcut that combines a template with a
# context dictionary and returns an HttpResponse with the rendered text.
# It replaces the manual process of loading a template and rendering it.

from .models import Post
# Import the Post model from the same app's models.py.
# The dot (.) means "current package" — i.e., the blog app.


def post_list(request):
    """
    View function to display all published blog posts.

    How it works:
    1. Queries the database for posts with status = PUBLISHED.
    2. Passes the resulting queryset to the template as 'posts'.
    3. Django's template engine renders the HTML with real data.

    Args:
        request: The HTTP request object sent by the user's browser.
                 Django automatically passes this to every view function.

    Returns:
        HttpResponse: Rendered HTML page showing all published posts.
    """

    # Query only published posts from the database.
    # "Post.objects" is the default Manager that provides database query methods.
    # ".filter()" returns a QuerySet — a lazy collection of database rows
    #   that match the given condition(s).
    # "status=Post.Status.PUBLISHED" filters posts where the status field
    #   equals 'PB' (the PUBLISHED choice defined in the model).
    # Because the model's Meta class has ordering=['-publish'],
    #   the results are automatically ordered by publish date (newest first).
    posts = Post.objects.filter(status=Post.Status.PUBLISHED)

    # Render the template and return the HTTP response.
    # Arguments:
    #   request — the original HTTP request (required by render).
    #   'blog/post_list.html' — path to the template file,
    #       relative to the app's "templates/" directory.
    #   {'posts': posts} — the context dictionary. The key 'posts'
    #       becomes a variable available inside the template.
    #       The template uses {% for post in posts %} to loop over it.
    return render(request, 'blog/post_list.html', {'posts': posts})
