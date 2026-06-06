from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
# Create your models here.
# post 1
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'


    title = models.CharField(max_length= 128)
    body = models.TextField()
    slug = models.SlugField(max_length=250)
    publish = models.DateTimeField(default=timezone.now)
#slug = models.SlugField(
# max_length=250,
# unique_for_date='publish'
# )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(
    max_length=2,
    choices=Status,
    default=Status.DRAFT
    )

    author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='blog_posts'
    )
    class Meta:
        ordering = ['-publish']
        indexes = [
        models.Index(fields=['-publish']),
        ]
    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        #first step to show for students how to use reverse function if the url change in future 
        #this not work 

        #return f'/blog/posts/{self.id}/'
        
        #second step to show for students how to use reverse function if the url change in future
        
        return reverse('blog:post_detail', args=[self.id])