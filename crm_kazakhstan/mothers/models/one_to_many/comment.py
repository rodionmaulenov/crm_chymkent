from django.db import models


class Comment(models.Model):
    mother = models.ForeignKey("Mother", on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    banned = models.BooleanField(default=False)
