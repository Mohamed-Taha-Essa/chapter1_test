from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
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
    slug = models.SlugField(
    max_length=250,
    unique_for_date='publish',
    blank=True
    )
    # # after that apply migration and update url to take year ,month ,day
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
    
    #to save slug automatic from admin
    def save(self, *args, **kwargs):
        if not self.slug and self.title:   # Auto-generate only if slug is empty
            # Generate base slug from title
            base_slug = slugify(self.title)
            
            # Add date from publish field
            date_str = self.publish.strftime("%Y-%m-%d")
            self.slug = f"{base_slug}-{date_str}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        #first step to show for students how to use reverse function if the url change in future 
        #this not work 

        #return f'/blog/posts/{self.id}/'
        
        #second step to show for students how to use reverse function if the url change in future
        
        return reverse('blog:post_detail', args=[self.id])
        # args=[
        #     self.publish.year,
        #     self.publish.month,
        #     self.publish.day,
        #     self.slug
        # ]   