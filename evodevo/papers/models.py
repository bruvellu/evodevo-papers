from django.db import models
from feeds.models import Post


class Status(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(blank=True)
    response = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    publication_id = models.CharField(blank=True, max_length=50)
    url = models.URLField(blank=True)

    def generate_status_text(self):
        template = f'{self.post.title} {self.post.link} #EvoDevo #Papers'
        self.text = template
        return self.text

    def __str__(self):
        return self.text
