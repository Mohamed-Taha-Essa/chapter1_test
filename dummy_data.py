
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE' ,'project.settings')
django.setup()
from blog.models import Post
from faker import Faker
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


fake = Faker()
def create_posts(num = 10):

    users = []

    # Create users
    for i in range(10):
        username = f'user_{i+1}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': fake.email(),
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
            }
        )

        if created:
            user.set_password('password123')
            user.save()
        
        users.append(user)

    # Create posts
    for i in range(num):
        title = fake.sentence(nb_words=4)
        slug = slugify(title)
        body = '\n'.join(fake.paragraphs(nb=4))
        status = fake.random_element([Post.Status.DRAFT, Post.Status.PUBLISHED])
        author = fake.random_element(users)
        publish_date = timezone.now()

        post, created = Post.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'body': body,
                'status': status,
                'author': author,
                'publish': publish_date
            }
        )

create_posts(10)

