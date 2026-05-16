# Chapter 1 — Django ORM & QuerySets

> This chapter covers how Django communicates with the database without writing raw SQL.
> You will learn how to **create**, **read**, **update**, and **delete** data using Python code.

---

## 1. What is the Django ORM?

The **ORM (Object-Relational Mapper)** is Django's built-in tool that lets you:

- Work with the database using **Python objects** instead of SQL
- Automatically generate SQL queries behind the scenes
- Switch between databases (SQLite, PostgreSQL, MySQL) without changing your code

```
Python code  →  Django ORM  →  SQL query  →  Database
```

---

## 2. What is a QuerySet?

A **QuerySet** is a list of database objects returned by Django.

- It maps to a **`SELECT`** SQL statement
- Filters map to **`WHERE`** or **`LIMIT`** clauses
- QuerySets are **lazy** — they only hit the database when you actually use the result

```python
# This does NOT run a database query yet — it is lazy
all_posts = Post.objects.all()

# The query runs HERE when you loop over it
for post in all_posts:
    print(post.title)
```

---

## 3. Admin Tips: `raw_id_fields` and Facet Counts

### `raw_id_fields`

By default, Django admin loads **all related objects** into a dropdown.  
This is fine for small datasets, but for **100,000+ records** it will be very slow.

```python
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ['author']
```

✅ **Why use it?**
- Faster admin pages
- Better for large datasets
- Replaces the slow dropdown with a simple ID input field

---

### Facet Counts (`show_facets`)

Facet counts show **how many objects match each filter** before you click it.

```python
class PostAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALLOW
```

| Option | Behaviour |
|---|---|
| `ShowFacets.ALLOW` | User can toggle counts on/off (default) |
| `ShowFacets.ALWAYS` | Counts are always shown |
| `ShowFacets.NEVER` | Counts are never shown |

> **Note:** Counts are off by default because they add extra database queries, which can slow down admin pages with millions of objects.

---

## 4. Creating Objects

### Method 1 — Two-step (create in memory, then save)

```python
from django.contrib.auth.models import User
from blog.models import Post

# Step 1: Get the author from the database
user = User.objects.get(username='admin')

# Step 2: Create the object in memory (NOT saved yet)
post = Post(
    title='Another post',
    slug='another-post',
    body='Post body.',
    author=user
)

# Step 3: Save to the database (runs an INSERT SQL statement)
post.save()
```

### Method 2 — One-step with `create()`

```python
Post.objects.create(
    title='One more post',
    slug='one-more-post',
    body='Post body.',
    author=user
)
``` 

### Method 3 — Get or Create

Retrieves an object if it exists, or creates it if it does not.  
Returns a **tuple**: `(object, created)` where `created` is `True` or `False`.

```python
user, created = User.objects.get_or_create(username='user2')
```

---

## 5. Reading / Retrieving Objects

### `get()` — Fetch a single object

```python
user = User.objects.get(username='admin')
```

⚠️ **Raises exceptions if:**
- No result found → `DoesNotExist`
- More than one result → `MultipleObjectsReturned`

**Safe alternative** — use `filter()` and slice:

```python
post = Post.objects.filter(author=user)[0]
```

### `all()` — Fetch all objects

```python
all_posts = Post.objects.all()
```

---

## 6. Filtering Objects

Use `.filter()` to add conditions (like SQL `WHERE`).

```python
Post.objects.filter(title='Who was Django Reinhardt?')
```

To see the SQL generated:

```python
posts = Post.objects.filter(title='Who was Django Reinhardt?')
print(posts.query)
```

---

## 7. Field Lookups (Double Underscore `__`)

Django uses `field__lookup_type` syntax for advanced filtering.

### Text Lookups

| Lookup | Example | SQL Equivalent |
|---|---|---|
| `exact` (default) | `filter(id__exact=1)` | `WHERE id = 1` |
| `iexact` | `filter(title__iexact='django')` | Case-insensitive match |
| `contains` | `filter(title__contains='Django')` | `WHERE title LIKE '%Django%'` |
| `icontains` | `filter(title__icontains='django')` | Case-insensitive LIKE |
| `startswith` | `filter(title__startswith='Who')` | `WHERE title LIKE 'Who%'` |
| `istartswith` | `filter(title__istartswith='who')` | Case-insensitive |
| `endswith` | `filter(title__endswith='?')` | `WHERE title LIKE '%?'` |
| `iendswith` | `filter(title__iendswith='reinhardt?')` | Case-insensitive |

### Numeric / Comparison Lookups

| Lookup | Example | SQL Equivalent |
|---|---|---|
| `in` | `filter(id__in=[1, 3])` | `WHERE id IN (1, 3)` |
| `gt` | `filter(id__gt=3)` | `WHERE id > 3` |
| `gte` | `filter(id__gte=3)` | `WHERE id >= 3` |
| `lt` | `filter(id__lt=3)` | `WHERE id < 3` |
| `lte` | `filter(id__lte=3)` | `WHERE id <= 3` |

### Date Lookups

```python
from datetime import date

Post.objects.filter(publish__date=date(2024, 1, 31))  # exact date
Post.objects.filter(publish__year=2024)               # by year
Post.objects.filter(publish__month=1)                 # by month
Post.objects.filter(publish__day=1)                   # by day
Post.objects.filter(publish__date__gt=date(2024, 1, 1)) # date greater than
```

### Related Object Lookups (ForeignKey traversal)

```python
# Posts by author username
Post.objects.filter(author__username='admin')

# Posts by username starting with 'ad'
Post.objects.filter(author__username__startswith='ad')

# Posts in 2024 by 'admin'
Post.objects.filter(publish__year=2024, author__username='admin')
```

---

## 8. Chaining Filters

Each `.filter()` returns a new QuerySet — you can chain them:

```python
Post.objects.filter(publish__year=2024) \
            .filter(author__username='admin')
```

---

## 9. Excluding Objects

Use `.exclude()` to remove matching objects from results:

```python
# All 2024 posts whose title does NOT start with 'Why'
Post.objects.filter(publish__year=2024) \
            .exclude(title__startswith='Why')
```

---

## 10. Ordering Objects

```python
Post.objects.order_by('title')        # ascending (A → Z)
Post.objects.order_by('-title')       # descending (Z → A)
Post.objects.order_by('author', 'title')  # multiple fields
Post.objects.order_by('?')            # random order
```

> The default order is set in the model's `Meta` class with `ordering`.

---

## 11. Limiting QuerySets (Slicing)

```python
Post.objects.all()[:5]       # SQL: LIMIT 5 — first 5 posts
Post.objects.all()[3:6]      # SQL: OFFSET 3 LIMIT 6 — posts 4, 5, 6
Post.objects.order_by('?')[0]  # one random post
```

> ⚠️ Negative indexing is **not supported** on QuerySets.

---

## 12. Counting Objects

```python
Post.objects.filter(id__lt=3).count()
# Returns: integer (e.g., 2)
# SQL: SELECT COUNT(*) WHERE id < 3
```

---

## 13. Checking If Objects Exist

```python
Post.objects.filter(title__startswith='Why').exists()
# Returns: True or False
```

---

## 14. Updating Objects

```python
post = Post.objects.get(id=1)
post.title = 'New title'
post.save()   # runs an UPDATE SQL statement
```

---

## 15. Deleting Objects

```python
post = Post.objects.get(id=1)
post.delete()
```

> ⚠️ Deleting an object also deletes any related objects linked via `ForeignKey` with `on_delete=CASCADE`.

---

## Quick Reference Summary

| Operation | Method | SQL |
|---|---|---|
| Get all | `Post.objects.all()` | `SELECT *` |
| Get one | `Post.objects.get(id=1)` | `SELECT ... LIMIT 1` |
| Filter | `Post.objects.filter(...)` | `WHERE` |
| Exclude | `Post.objects.exclude(...)` | `WHERE NOT` |
| Order | `Post.objects.order_by(...)` | `ORDER BY` |
| Limit | `Post.objects.all()[:5]` | `LIMIT 5` |
| Count | `Post.objects.count()` | `SELECT COUNT(*)` |
| Exists | `Post.objects.exists()` | `SELECT 1` |
| Create | `Post.objects.create(...)` | `INSERT` |
| Update | `post.save()` | `UPDATE` |
| Delete | `post.delete()` | `DELETE` |


## 16. Complex Lookups with Q Objects

By default, when you pass multiple conditions to `.filter()`, Django joins them with **AND**.

```python
# This returns posts where publish year is 2024 AND author is 'admin'
Post.objects.filter(publish__year=2024, author__username='admin')
```

But what if you need **OR** logic? That's where **Q objects** come in.

### What is a Q Object?

A `Q` object wraps a single lookup condition.  
You can then combine them using logical operators:

| Operator | Symbol | Meaning |
|---|---|---|
| AND | `&` | Both conditions must be true |
| OR | `\|` | At least one condition must be true |
| XOR | `^` | Exactly one condition must be true |

### Example — Filter with OR

```python
from django.db.models import Q

# Define two separate conditions
starts_who = Q(title__istartswith='who')
starts_why = Q(title__istartswith='why')

# Get posts where title starts with 'who' OR 'why'
Post.objects.filter(starts_who | starts_why)
```

### Example — Mix AND and OR

```python
# Published posts where title starts with 'who' OR 'why'
Post.objects.filter(
    Q(title__istartswith='who') | Q(title__istartswith='why'),
    status=Post.Status.PUBLISHED   # AND this condition
)
```

> 📖 Official docs: [Q objects](https://docs.djangoproject.com/en/5.0/topics/db/queries/#complex-lookups-with-q-objects)

---

## 17. When Are QuerySets Evaluated?

QuerySets are **lazy** — they don't hit the database when you write them.  
They only run the SQL query when they are actually **used**.

```python
# No database query yet — just a description of what to fetch
posts = Post.objects.filter(status='PB')

# The query runs HERE when you iterate
for post in posts:
    print(post.title)
```

### QuerySets are evaluated when you:

| Action | Example |
|---|---|
| Iterate (loop) | `for post in Post.objects.all()` |
| Slice | `Post.objects.all()[:3]` |
| Call `list()` | `list(Post.objects.all())` |
| Call `len()` | `len(Post.objects.all())` |
| Call `repr()` | `repr(Post.objects.all())` |
| Use in `bool()` / `if` | `if Post.objects.filter(...):` |
| Pickle or cache | (advanced use cases) |

> 💡 **Why does this matter?**  
> Because you can chain as many `.filter()` calls as you want without any performance cost — the database is only queried once, at the end.

---

## 18. Custom Model Managers

### What is a Manager?

Every model has a **manager** — the bridge between your model and the database.  
The default manager is always called `objects`:

```python
Post.objects.all()   # "objects" is the default manager
```

### Why Create a Custom Manager?

If you find yourself filtering by the same condition repeatedly:

```python
Post.objects.filter(status=Post.Status.PUBLISHED)  # tedious to repeat
```

You can create a **custom manager** to make this reusable.

---

### Method 1 — Add a Method to the Existing Manager

This keeps `Post.objects` but adds a new method to it.  
Use it like: `Post.objects.published()`

```python
# models.py

class PostManager(models.Manager):
    def published(self):
        """Return only published posts."""
        return self.filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    # ... fields ...
    objects = PostManager()  # replaces the default manager
```

**Usage:**

```python
Post.objects.published()                            # all published posts
Post.objects.published().filter(title__icontains='django')  # chain more filters
```

---

### Method 2 — Create a Separate Manager (Recommended)

This creates a brand-new manager that **always filters** published posts.  
Use it like: `Post.published.all()`

```python
# models.py

class PublishedManager(models.Manager):
    def get_queryset(self):
        """Override the default QuerySet to only include published posts."""
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Post(models.Model):
    # ... fields ...
    objects   = models.Manager()    # keep the default manager
    published = PublishedManager()  # our custom manager
```

**Usage:**

```python
Post.published.all()                              # all published posts
Post.published.filter(title__startswith='Who')   # filter on top
```

> ⚠️ **Important:** Always keep `objects = models.Manager()` if you add custom managers.  
> If you don't, `Post.objects` will stop working.

### Test it in the Django shell

```bash
python manage.py shell
```

```python
from blog.models import Post

# Using the custom manager
Post.published.all()
Post.published.filter(title__startswith='Who')
```

---

## 19. Creating Views

A **view** is a Python function that:
1. Receives an HTTP request from the browser
2. Fetches data from the database
3. Returns an HTTP response (usually rendered HTML)

### View 1 — List of All Published Posts

```python
# blog/views.py

from django.shortcuts import render
from .models import Post

def post_list(request):
    # Fetch all published posts using our custom manager
    posts = Post.published.all()

    # Render the template and pass posts as context
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}        # 'posts' becomes available in the template
    )
```

**What `render()` does:**

| Argument | What it is |
|---|---|
| `request` | The browser's HTTP request object |
| `'blog/post/list.html'` | Path to the HTML template file |
| `{'posts': posts}` | Context data passed into the template |

---

### View 2 — Single Post Detail (with manual 404)

```python
# blog/views.py

from django.http import Http404

def post_detail(request, id):
    try:
        # Try to find the published post with this id
        post = Post.published.get(id=id)
    except Post.DoesNotExist:
        # If not found, return a 404 error page
        raise Http404("No Post found.")

    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )
```

---

### View 2 — Cleaner Version with `get_object_or_404`

Django provides a shortcut that does the `try/except` for you:

```python
# blog/views.py

from django.shortcuts import render, get_object_or_404

def post_detail(request, id):
    # Automatically raises 404 if not found — no try/except needed
    post = get_object_or_404(
        Post,
        id=id,
        status=Post.Status.PUBLISHED
    )

    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )
```

> ✅ **Best practice:** Always use `get_object_or_404()` instead of a manual `try/except`.  
> It's shorter, cleaner, and follows the Django convention.

---

## 20. Creating URL Patterns

URL patterns tell Django **which view to call** when someone visits a URL.

### Step 1 — Create `blog/urls.py`

```python
# blog/urls.py

from django.urls import path
from . import views

# Namespace: lets you reference URLs as 'blog:post_list', 'blog:post_detail'
app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),          # /blog/
    path('<int:id>/', views.post_detail, name='post_detail'),  # /blog/5/
]
```

**How `path()` works:**

| Part | Example | Meaning |
|---|---|---|
| Route string | `''` | Matches the root URL of this app |
| Route with capture | `'<int:id>/'` | Captures an integer from the URL and names it `id` |
| View | `views.post_list` | The function to call |
| Name | `name='post_list'` | A nickname to use in templates and Python code |

**Path converters:**

| Converter | Example | Matches |
|---|---|---|
| `int` | `<int:id>` | A positive integer like `5` |
| `str` | `<str:name>` | Any string (default) |
| `slug` | `<slug:post>` | Letters, numbers, hyphens, underscores |
| `uuid` | `<uuid:pk>` | A UUID string |

> 💡 For complex patterns (e.g. regex), use `re_path()` instead of `path()`.

---

### Step 2 — Include Blog URLs in the Project's `urls.py`

```python
# project/urls.py

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # All blog URLs are now accessible under /blog/
    path('blog/', include('blog.urls', namespace='blog')),
]
```

**Result:**

| URL in browser | View called |
|---|---|
| `/blog/` | `post_list` |
| `/blog/5/` | `post_detail` with `id=5` |
| `/blog/12/` | `post_detail` with `id=12` |

### Using Named URLs in Templates

Once you define URL names, never hardcode paths in templates.  
Use the `{% url %}` tag instead:

```html
<!-- Instead of: <a href="/blog/">Posts</a> -->
<a href="{% url 'blog:post_list' %}">Posts</a>

<!-- Instead of: <a href="/blog/5/">Read More</a> -->
<a href="{% url 'blog:post_detail' post.id %}">Read More</a>
```

> ✅ This way, if you ever change your URL structure, you only update `urls.py` — not every template.

