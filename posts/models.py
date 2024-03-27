from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


CATEGORY_CHOICES = [
    ('blog', 'Blog'),
    ('seminar', 'Seminar'),
    ('news_letter', 'News Letter')
]


class Post(models.Model):
    title = models.CharField(max_length=255, unique=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=12)
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    slug = models.SlugField(blank=True, max_length=300)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [models.Index(fields=['slug'])]
