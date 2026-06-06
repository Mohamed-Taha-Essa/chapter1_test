# blog/views.py
# This module contains all view functions for the blog app.
# Views handle HTTP requests, fetch data from the database,
# and return HTTP responses (usually rendered HTML templates).

from django.shortcuts import render
from django.urls import resolve

from .models import Post
# Import the Post model from the same app's models.py.
# The dot (.) means "current package" — i.e., the blog app.


def post_list(request):
    # Fetch all Post objects from the database, ordered by published_date in descending order.
    posts = Post.objects.all()
    # for posting in posts:
    #     print(posting.get_absolute_url())

    return render(request, 'blog/post_list.html', {'posts': posts})

from urllib.parse import urlparse
from django.urls import resolve
from django.http import Http404, HttpResponseRedirect



def post_detail(request, id):
  
    post = Post.objects.get(id=id)
    url = f'/blog/{id}/'
    #print(request.path)

    match = resolve(url)
    # print(match)
    print(match.func)
    print(match.args)
    print(match.kwargs)
    print(match.url_name)

    #what is using for 
    """debugging URLs
    security checks
    logging
    middleware analysis"""



  
    return render(request, 'blog/post_detail.html', {'post': post})
