# 📘 Django 5 By Example — Chapter 2 (Part 2): Teaching Reference Guide

> **Topic:** Recommending Posts by Email — Forms, Views, SMTP, and Environment Variables  
> **Purpose:** A clean, structured reference to use when teaching students this section.

---

## 📋 Table of Contents

1. [The Big Picture — What We Are Building](#1-the-big-picture--what-we-are-building)
2. [Django Forms — Two Base Classes](#2-django-forms--two-base-classes)
3. [Creating the EmailPostForm](#3-creating-the-emailpostform)
4. [Form Fields & Widgets — Reference Table](#4-form-fields--widgets--reference-table)
5. [Handling the Form in a View — GET vs POST](#5-handling-the-form-in-a-view--get-vs-post)
6. [Form Lifecycle — Step by Step](#6-form-lifecycle--step-by-step)
7. [Sending Emails with Django](#7-sending-emails-with-django)
8. [Working with Environment Variables (python-decouple)](#8-working-with-environment-variables-python-decouple)
9. [Complete: The post_share View with Email](#9-complete-the-post_share-view-with-email)
10. [The Share Template](#10-the-share-template)
11. [Adding the URL Pattern](#11-adding-the-url-pattern)
12. [Testing Without a Real SMTP Server](#12-testing-without-a-real-smtp-server)
13. [Common Mistakes & Gotchas](#13-common-mistakes--gotchas)
14. [Summary Table](#14-summary-table)

---

## 1. The Big Picture — What We Are Building

We want users to be able to **share a blog post with a friend via email**.

### 🗺️ What We Need to Build

```
User clicks "Share this post"
        │
        ▼
  GET /blog/1/share/          ← Show empty form
        │
        ▼
  User fills name, email, friend's email, comment
        │
        ▼
  POST /blog/1/share/         ← Form submitted
        │
    ┌───┴───────────────┐
    │  is_valid()?      │
    │                   │
  False               True
    │                   │
  Show errors        Send email
  (keep data)            │
                     Redirect / success message
```

### 📁 Files We Will Touch

| File               | Action                                    |
|-------------------|-------------------------------------------|
| `blog/forms.py`   | **CREATE** — Define `EmailPostForm`       |
| `blog/views.py`   | **MODIFY** — Add `post_share` view        |
| `blog/urls.py`    | **MODIFY** — Add URL for `post_share`     |
| `blog/post/share.html` | **CREATE** — Form template          |
| `settings.py`     | **MODIFY** — Add email configuration      |
| `.env`            | **CREATE** — Store sensitive credentials  |

---

## 2. Django Forms — Two Base Classes

Django provides two ways to build forms:

| Base Class   | Use When                                                   | Example                         |
|-------------|------------------------------------------------------------|---------------------------------|
| `forms.Form` | The form is **not directly tied** to a database model     | Contact form, search form, email share form |
| `forms.ModelForm` | The form **creates or edits** a model instance        | Post creation form, comment form |

### 🔍 Visual Difference

```python
# forms.Form — you define all fields manually
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

# forms.ModelForm — fields come from the model automatically
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'slug']
```

> **Teaching Tip:** For this chapter we use `forms.Form` because we're not creating/editing a Post —
> we're just collecting email info from the user.

---

## 3. Creating the EmailPostForm

Create the file `blog/forms.py` (Django convention: one `forms.py` per app):

```python
# blog/forms.py
from django import forms

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)       # Sender's name
    email = forms.EmailField()                  # Sender's email
    to = forms.EmailField()                     # Recipient's email
    comments = forms.CharField(
        required=False,                         # Optional field
        widget=forms.Textarea                   # Renders as <textarea>
    )
```

### 🔍 Field-by-Field Explanation

| Field      | Type          | Required? | HTML Element           | Notes                         |
|-----------|--------------|----------|------------------------|-------------------------------|
| `name`    | `CharField`  | ✅ Yes    | `<input type="text">`  | Max 25 chars enforced         |
| `email`   | `EmailField` | ✅ Yes    | `<input type="email">` | Must be a valid email address |
| `to`      | `EmailField` | ✅ Yes    | `<input type="email">` | Must be a valid email address |
| `comments`| `CharField`  | ❌ No     | `<textarea>`           | Widget overrides default input|

---

## 4. Form Fields & Widgets — Reference Table

### Common Field Types

| Field Class      | Validates                        | Default HTML Element         |
|-----------------|----------------------------------|------------------------------|
| `CharField`     | String, optional max_length      | `<input type="text">`        |
| `EmailField`    | Must be valid email format       | `<input type="email">`       |
| `IntegerField`  | Must be an integer               | `<input type="number">`      |
| `BooleanField`  | Must be True (checkbox)          | `<input type="checkbox">`    |
| `DateField`     | Must be a valid date             | `<input type="text">`        |
| `ChoiceField`   | Must match one of defined choices| `<select>`                   |
| `URLField`      | Must be a valid URL              | `<input type="url">`         |

> Full list: https://docs.djangoproject.com/en/5.0/ref/forms/fields/

### Common Widgets

```python
# Widget overrides how the field is DISPLAYED (not validated)

# Multi-line text input
comments = forms.CharField(widget=forms.Textarea)

# Password input (hides characters)
password = forms.CharField(widget=forms.PasswordInput)

# Radio buttons instead of dropdown
choice = forms.ChoiceField(
    choices=[('a', 'Option A'), ('b', 'Option B')],
    widget=forms.RadioSelect
)

# Hidden field (not shown to user)
token = forms.CharField(widget=forms.HiddenInput)
```

---

## 5. Handling the Form in a View — GET vs POST

The same view handles **both** showing the form (GET) and processing it (POST).

```python
# blog/views.py
from django.shortcuts import get_object_or_404, render
from .forms import EmailPostForm
from .models import Post

def post_share(request, post_id):
    # 1. Get the post (404 if not found or not published)
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    if request.method == 'POST':
        # 2a. Form was submitted — bind data to the form
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # 3. All fields are valid — access clean data
            cd = form.cleaned_data
            # ... send email here (coming up next)
    else:
        # 2b. First time visiting page — show empty form
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {'post': post, 'form': form}
    )
```

---

## 6. Form Lifecycle — Step by Step

### Step 1 — First Visit (GET Request)

```
Browser → GET /blog/5/share/
                  │
                  ▼
         form = EmailPostForm()    ← Empty, unbound form
                  │
                  ▼
         Rendered in template → User sees blank form
```

### Step 2 — User Submits (POST Request)

```
Browser → POST /blog/5/share/
                  │
                  ▼
         form = EmailPostForm(request.POST)   ← Bound form
                  │
                  ▼
         form.is_valid()
           │            │
          True         False
           │            │
    form.cleaned_data  form.errors
    {                  {
     'name': 'Ali',     'name': ['Too long'],
     'email': '...',    ...
     'to': '...',      }
     'comments': ''         │
    }                  Re-render with errors
           │
    → Send email!
```

### 📦 What is `cleaned_data`?

`cleaned_data` is a **dictionary** of validated and normalized field values.

```python
# After form.is_valid() returns True:
cd = form.cleaned_data

print(cd['name'])       # 'Mohamed'
print(cd['email'])      # 'sender@example.com'
print(cd['to'])         # 'friend@example.com'
print(cd['comments'])   # 'Check this out!'

# Use these values to send the email:
send_mail(
    subject=f"...",
    message=cd['comments'],
    from_email=cd['email'],
    recipient_list=[cd['to']],
)
```

> ⚠️ **Important:** Never use `request.POST['field']` directly for logic —
> always use `form.cleaned_data` after `is_valid()`. The cleaned data is:
> - **Validated** (confirmed to be correct format)
> - **Normalized** (e.g., email is stripped of whitespace, dates are Python `date` objects)

### 🔍 What is `form.errors`?

```python
# If is_valid() returns False:
print(form.errors)
# {'email': ['Enter a valid email address.'], 'name': ['Ensure this value has at most 25 characters.']}

# In templates, Django renders errors automatically:
{{ form.email.errors }}   # Shows errors for the email field
{{ form.errors }}         # Shows all errors as a dictionary
```

---

## 7. Sending Emails with Django

### Django's `send_mail()` Function

```python
from django.core.mail import send_mail

send_mail(
    subject='Hello from Django',          # Email subject
    message='This is the body.',          # Plain text body
    from_email='sender@example.com',      # From address
    recipient_list=['receiver@example.com'],  # List of recipients
    fail_silently=False,                  # Raise error if sending fails
)
```

### Required Django Email Settings

| Setting               | Default       | Description                                  |
|----------------------|--------------|----------------------------------------------|
| `EMAIL_HOST`         | `localhost`   | SMTP server hostname                         |
| `EMAIL_PORT`         | `25`          | SMTP port number                             |
| `EMAIL_HOST_USER`    | `''`          | Username to log in to the SMTP server        |
| `EMAIL_HOST_PASSWORD`| `''`          | Password for the SMTP server                 |
| `EMAIL_USE_TLS`      | `False`       | Use TLS (port 587) — recommended for Gmail  |
| `EMAIL_USE_SSL`      | `False`       | Use SSL (port 465) — alternative to TLS     |
| `DEFAULT_FROM_EMAIL` | (system default) | Default "From" address for all emails    |

> ⚠️ **TLS vs SSL:**  
> Use `EMAIL_USE_TLS = True` with port `587` (Gmail standard).  
> Don't set both `EMAIL_USE_TLS` and `EMAIL_USE_SSL` to True — they conflict.

---

## 8. Working with Environment Variables (python-decouple)

### 🤔 Why Not Just Write Credentials in settings.py?

```python
# ❌ NEVER DO THIS — credentials visible in source code
EMAIL_HOST_PASSWORD = 'my_secret_password_123'
```

If you push this to GitHub, your password is **public forever** (even if you delete it later).

### ✅ The Safe Way: Environment Variables

```
Code (settings.py)  →  reads from  →  .env file  →  credentials stay local
```

### Step 1: Install python-decouple

```bash
pip install python-decouple==3.8
```

### Step 2: Create the `.env` File

Create `.env` in the **project root** (same level as `manage.py`):

```bash
# .env
EMAIL_HOST_USER=your_account@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DEFAULT_FROM_EMAIL=My Blog <your_account@gmail.com>
SECRET_KEY=your-django-secret-key
```

> ⚠️ **Add `.env` to `.gitignore` immediately!**

```bash
# .gitignore
.env
```

### Step 3: Read Variables in `settings.py`

```python
# settings.py
from decouple import config

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
```

### 🔍 How `config()` Works

```python
from decouple import config

# Read from .env — raises error if not found
EMAIL_HOST_USER = config('EMAIL_HOST_USER')

# With a default value (won't raise error if missing)
DEBUG = config('DEBUG', default=True, cast=bool)

# Cast to int
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
```

---

### 📧 Gmail App Password Setup

Gmail blocks "less secure apps" by default. To send email via Gmail SMTP:

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification**
3. Go to **App Passwords** (appears after enabling 2FA)
4. Generate a new app password for "Mail" + "Other (Django)"
5. Copy the 16-character password into your `.env`:

```bash
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop   # the 16-char app password
```

---

## 9. Complete: The post_share View with Email

```python
# blog/views.py
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from .forms import EmailPostForm
from .models import Post

def post_share(request, post_id):
    # Retrieve the published post
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False  # Track if email was sent successfully

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # Build the full URL for the post
            post_url = request.build_absolute_uri(post.get_absolute_url())

            # Compose the email
            subject = (
                f"{cd['name']} recommends you read \"{post.title}\""
            )
            message = (
                f"Read \"{post.title}\" at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=cd['email'],
                recipient_list=[cd['to']],
            )

            sent = True  # Show success message in template
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )
```

### 🔍 `request.build_absolute_uri()` — What & Why

```python
# get_absolute_url() returns a relative path:
post.get_absolute_url()
# → /blog/2024/1/15/my-post/

# build_absolute_uri() makes it a full URL:
request.build_absolute_uri(post.get_absolute_url())
# → http://127.0.0.1:8000/blog/2024/1/15/my-post/
```

> We need the **full URL** in the email so the recipient can click and open the post.

---

## 10. The Share Template

```html
<!-- templates/blog/post/share.html -->
{% extends "blog/base.html" %}

{% block title %}Share a Post{% endblock %}

{% block content %}
    {% if sent %}
        <!-- ✅ Email was sent successfully -->
        <h1>Email sent!</h1>
        <p>
            "{{ post.title }}" was successfully sent to {{ form.cleaned_data.to }}.
        </p>
    {% else %}
        <!-- 📬 Show the form -->
        <h1>Share "{{ post.title }}" by email</h1>

        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit" value="Send email">
        </form>
    {% endif %}
{% endblock %}
```

### 🔐 What is `{% csrf_token %}`?

CSRF stands for **Cross-Site Request Forgery** — a security attack where a malicious site
tricks a logged-in user into submitting a form on your site without their knowledge.

```html
<form method="post">
    {% csrf_token %}   ← Django generates a secret token per session
    ...
</form>
```

Django **validates this token on every POST request**. If it's missing or wrong, Django
rejects the request with a `403 Forbidden` error. **Always include it in POST forms.**

### 🎨 Different Ways to Render a Form

```html
<!-- Option 1: Quick — wraps each field in <p> tags -->
{{ form.as_p }}

<!-- Option 2: Quick — wraps each field in <table> rows -->
{{ form.as_table }}

<!-- Option 3: Quick — wraps each field in <li> tags -->
{{ form.as_ul }}

<!-- Option 4: Manual — full control over HTML -->
<div>
    <label for="{{ form.name.id_for_label }}">Your name:</label>
    {{ form.name }}
    {% if form.name.errors %}
        <span class="error">{{ form.name.errors }}</span>
    {% endif %}
</div>
```

---

## 11. Adding the URL Pattern

```python
# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:post>/',
        views.post_detail,
        name='post_detail'
    ),
    # ← NEW
    path('<int:post_id>/share/', views.post_share, name='post_share'),
]
```

### Link to the Share Form from Post Detail Template

```html
<!-- templates/blog/post/detail.html -->
<p>
    <a href="{% url 'blog:post_share' post.id %}">
        Share this post
    </a>
</p>
```

---

## 12. Testing Without a Real SMTP Server

During development, avoid sending real emails. Use the **console backend** instead:

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

When you submit the share form, the email will be **printed in the terminal**:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Ali recommends you read "Who was Django Reinhardt"
From: ali@example.com
To: friend@example.com
Date: ...

Read "Who was Django Reinhardt" at http://127.0.0.1:8000/blog/2024/1/15/who-was-django-reinhardt/

Ali's comments: Great post, check it out!
```

> ✅ **For development:** use `console.EmailBackend`  
> ✅ **For production:** use real SMTP settings in `.env`

---

## 13. Common Mistakes & Gotchas

### ❌ Mistake 1: Forgetting `{% csrf_token %}` in POST Forms

```html
<!-- ❌ WRONG — Django will return 403 Forbidden -->
<form method="post">
    {{ form.as_p }}
    <button>Submit</button>
</form>

<!-- ✅ CORRECT -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button>Submit</button>
</form>
```

---

### ❌ Mistake 2: Using `request.POST` Data Directly Instead of `cleaned_data`

```python
# ❌ WRONG — raw, unvalidated, could be malicious
name = request.POST['name']

# ✅ CORRECT — validated and normalized by Django
if form.is_valid():
    name = form.cleaned_data['name']
```

---

### ❌ Mistake 3: Not Handling Both GET and POST in the Same View

```python
# ❌ WRONG — This only processes POST, crashes on GET
def post_share(request, post_id):
    form = EmailPostForm(request.POST)   # request.POST is empty on GET!
    ...

# ✅ CORRECT — Check the method first
def post_share(request, post_id):
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
    else:
        form = EmailPostForm()
```

---

### ❌ Mistake 4: Committing `.env` to Git

```bash
# ❌ NEVER commit .env to git
git add .env   # This exposes all your secrets!

# ✅ Add to .gitignore before the first commit
echo ".env" >> .gitignore
git add .gitignore
```

---

### ❌ Mistake 5: Both TLS and SSL Set to True

```python
# ❌ WRONG — these conflict!
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True

# ✅ Use one or the other:
# Gmail standard:
EMAIL_USE_TLS = True    # with EMAIL_PORT = 587
# OR
EMAIL_USE_SSL = True    # with EMAIL_PORT = 465
```

---

### ❌ Mistake 6: Using Gmail Password Instead of App Password

```bash
# ❌ WRONG — Gmail blocks regular passwords for SMTP
EMAIL_HOST_PASSWORD=my_gmail_password

# ✅ CORRECT — Generate an App Password from Google Account settings
EMAIL_HOST_PASSWORD=abcdefghijklmnop    # 16-char app password
```

---

## 14. Summary Table

| Concept               | Key Point                                                                |
|-----------------------|--------------------------------------------------------------------------|
| `forms.Form`          | Base class for standalone forms (not tied to a model)                   |
| `forms.ModelForm`     | Base class for forms that create/edit model instances                   |
| `EmailPostForm`       | Custom form with 4 fields: name, email, to, comments                   |
| `form.is_valid()`     | Validates all fields; returns `True` or `False`                         |
| `form.cleaned_data`   | Dict of validated + normalized field values; available after `is_valid()` |
| `form.errors`         | Dict of validation errors; available when `is_valid()` returns `False`  |
| `widget=forms.Textarea` | Overrides default HTML rendering to use `<textarea>`                 |
| `required=False`      | Makes a field optional                                                  |
| `send_mail()`         | Django function to send an email via configured SMTP                    |
| `EMAIL_USE_TLS`       | Use TLS on port 587 (recommended for Gmail)                             |
| `python-decouple`     | Library to load settings from `.env` file                              |
| `config('KEY')`       | Reads a value from the `.env` file                                      |
| `{% csrf_token %}`    | Security token required in all POST forms                               |
| `request.build_absolute_uri()` | Converts a relative URL to a full URL with domain             |
| `console.EmailBackend`| Prints emails to terminal instead of sending — great for development   |

---

*Last updated: June 2026 | Django 5 By Example — Chapter 2, Part 2*
