In this chapter, we will add pagination to the post list page to navigate through all posts. We will also
learn how to build class-based views with Django and convert the post_list view to a class-based
view named PostListView.
We will create the post_share view to share posts via email. We will use Django forms to share posts
and send email recommendations via Simple Mail Transfer Protocol (SMTP). To add comments to
posts, we will create a Comment model to store comments, and we will build the post_comment view
using forms for models.

Using canonical URLs for models
A website might have different pages that display the same content. In our application, the initial part
of the content for each post is displayed both on the post list page and the post detail page. A canonical
URL is the preferred URL for a resource. You can think of it as the URL of the most representative
page for specific content. There might be different pages on your site that display posts, but there is
a single URL that you use as the main URL for a post.

Canonical URLs allow you to specify the URL for the master copy of a page. Django allows you to im-
plement the get_absolute_url() method in your models to return the canonical URL for the object.
We will use the post_detail URL defined in the URL patterns of the application to build the canon-
ical URL for Post objects. Django provides different URL resolver functions that allow you to build
URLs dynamically using their name and any required parameters. We will use the reverse() utility
function of the django.urls module.
Edit the models.py file of the blog application to import the reverse() function and add the get_
absolute_url() method to the Post model as follows. The new code is highlighted in bold:
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
class PublishedManager(models.Manager):
def get_queryset(self):
return (
super().get_queryset().filter(status=Post.Status.PUBLISHED)
)
class Post(models.Model):
# ...
class Meta:
ordering = ['-publish']
indexes = [
models.Index(fields=['-publish']),
]
def __str__(self):
return self.title
def get_absolute_url(self):
return reverse(
'blog:post_detail',
args=[self.id]
)
The reverse() function will build the URL dynamically using the URL name defined in the URL pat-
terns. We have used the blog namespace followed by a colon and the post_detail URL name. Remem-
ber that the blog namespace is defined in the main urls.py file of the project when including the URL
patterns from blog.urls. The post_detail URL is defined in the urls.py file of the blog application.


explain for studensts using shell to print url using reverse

<a href="{% url 'post_detail' %}">
    Post Detail
</a>
# urls.py
if you have this url pattern:
path("post_detail/<int:id>/", views.post_detail, name="post_detail")
then you will show in html like this:
<a href="/post_detail/1/">
    Post Detail
</a>

but in your model or view or in python code you can't use {% url %} tag as it used in template files.
Instead, you can use the reverse() function to build the URL dynamically.

from django.urls import reverse

url = reverse("post_detail", args=[1])

print(url)
# Output: /post_detail/1/

why using reverse intead of writing direct url like this 
return redirect("post_detail/")

as if we change the path in urls.py file, the redirect will not work anymore.but reverse generate url dynamically.

post = Post.objects.get(id=5)
url = reverse("post_detail", args=[post.id])
print(url)
# Output: /post_detail/5/
# in future /post_detail/5/ will be /posts/5/  or /blog/django-admin-tips/ 
how to make object know the url of itself?
by write get_absolute_url() method in the model:
def get_absolute_url(self):
    return reverse(
        'blog:post_detail',
        args=[self.id]
    )


#Creating SEO-friendly URLs for posts
The canonical URL for a blog post detail view currently looks like /blog/1/. We will change the URL
pattern to create SEO-friendly URLs for posts. We will be using both the publish date and slug values
to build the URLs for single posts. By combining dates, we will make a post detail URL to look like /
blog/2024/1/1/who-was-django-reinhardt/. We will provide search engines with friendly URLs to
index, containing both the title and date of the post.
To retrieve single posts with the combination of publication date and slug, we need to ensure that no
post can be stored in the database with the same slug and publish date as an existing post. We will
prevent the Post model from storing duplicated posts by defining slugs to be unique for the publica-
tion date of the post.
Edit the models.py file and add the following unique_for_date parameter to the slug field of the
Post model:
class Post(models.Model):
# ...
slug = models.SlugField(
max_length=250,
unique_for_date='publish'
)
# ..
By using unique_for_date, the slug field is now required to be unique for the date stored in the
publish field. Note that the publish field is an instance of DateTimeField, but the check for unique
values will be done only against the date (not the time). Django will prevent you from saving a new post
with the same slug as an existing post for a given publication date. We have now ensured that slugs are
unique for the publication date, so we can now retrieve single posts by the publish and slug fields.
We have changed our models, so, let’s create migrations. Note that unique_for_date is not enforced
at the database level, so no database migration is required. However, Django uses migrations to keep
track of all model changes. We will create a migration just to keep migrations aligned with the current
state of the model.