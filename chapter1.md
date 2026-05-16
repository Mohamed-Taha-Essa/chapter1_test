
This is fine for a small number of records to show relation (name of author)

raw_id_fields = ['author'] 
But imagine you have:

100,000 authors
or 1 million users

Django would try to load all authors into the dropdown (slow , memory heavy)
Now Django replaces the dropdown with a raw ID input:
Why use it?

Faster admin pages
Better for large datasets
Avoid loading thousands of related objects

- Adding facet counts to filters explain it
- facet counts show how many objects belong to each filter option before you click it.
class PostAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALLOW

1 -admin.ShowFacets.ALLOW  -->Allow user to enable facets by toggle buttun.
    - Show counts only when _facets query parameter is enabled. This is still the default
    - By default in Django admin, counts are off because calculating them can create extra database queries which can slow down the page if the number of objects is millions .
2 -admin.ShowFacets.NEVER  -->Never show facets.
3 -admin.ShowFacets.ALWAYS  -->Always show facets.


## Working with QuerySets and managers

- queryser -->read and write content to the database programmatically.

- Django object-relational mapper (ORM) is a powerful database abstraction API that lets you
create, retrieve, update, and delete objects easily

- orm -> allow you to generate sql query 
     -interact with your database in a Pythonic fashion instead of writing raw SQL queries.

- The QuerySet equates to a SELECT SQL statement and the filters are limiting SQL
clauses such as WHERE or LIMIT.


----------------------
>>> from django.contrib.auth.models import User
>>> from blog.models import Post
>>> user = User.objects.get(username='admin')
>>> post = Post(title='Another post',
...slug='another-post',
...body='Post body.',
...author=user)
>>> post.save()



>>> user = User.objects.get(username='admin')
The get() method allows us to retrieve a single object from the database.
- This method executes a
SELECT SQL statement behind the scenes. Note that this method expects a result that matches the
query. If no results are returned by the database, this method will raise a DoesNotExist exception,
and if the database returns more than one result, it will raise a MultipleObjectsReturned exception.

- this is a problem if you want no exception happen on your code so we can using filter instead of get as it return list and can slice first object

>>> post = Post.objects.filter(author=user)[0]
>>> post
<Post: Another post>

post = Post(title='Another post', slug='another-post', body='Post body.',
author=user)

This object is in memory and not persisted to the database; we created a Python object that can be
used during runtime but is not saved into the database.

Finally, we are saving the Post object in the database using the save() method:
>>> post.save()
This action performs an INSERT SQL statement behind the scenes.


you can create
the object and persist it to the database in a single operation using the create() method, as follows:
>>> Post.objects.create(title='One more post',
slug='one-more-post',
body='Post body.',
author=user)

fetch an object from the database or create it if it’s absent.
The get_or_create() method facilitates this by either retrieving an object or creating it if not found.
This method returns a tuple with the object retrieved and a Boolean indicating whether a new object
was created. Th
>>> user, created = User.objects.get_or_create(username='user2')

## Updating objects

>>> post.title = 'New title'
>>> post.save()

## Retrieving objects

Each Django model has at least one manager, and the
default manager is called objects. You get a QuerySet object using your model manager.

all_posts = Post.objects.all()
This is how we create a QuerySet that returns all objects in the database. Note that this QuerySet has
not been executed yet. Django QuerySets are lazy, which means they are only evaluated when they
are forced to. This behavior makes QuerySets very efficient. If you don’t assign the QuerySet to a vari-
able but, instead, write it directly on the Python shell,

## Filtering objects
To filter a QuerySet, you can use the filter() method of the manager. This method allows you to
specify the content of a SQL WHERE clause by using field lookups.