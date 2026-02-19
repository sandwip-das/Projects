from django.db import models
from .models import SingletonModel

# Define Category Choices for the generic AboutMeItem model
ABOUT_CATEGORY_CHOICES = [
    ('FOCUS', 'Professional Focus'),
    ('SKILL', 'Key Skills'),
    ('ROLE', 'Current Roles'),
]

class AboutMeItem(models.Model):
    category = models.CharField(max_length=10, choices=ABOUT_CATEGORY_CHOICES)
    text = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.get_category_display()}: {self.text}"
