from django.db import models
from django.contrib.auth.models import User


def user_datasets_path(instance, filename):
    return 'datasets/{0}/{1}'.format(instance.user.username, filename)


class Dataset(models.Model):
    user         = models.ForeignKey(User)
    title        = models.CharField(max_length=64)
    description  = models.TextField()
    dataset      = models.FileField(upload_to=user_datasets_path)
    content_type = models.CharField(max_length=512)

