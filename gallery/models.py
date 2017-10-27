from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible
class ImageName(models.Model):
    name = models.CharField(max_length=255)
    md5 = models.ForeignKey('ImagePath', models.DO_NOTHING, db_column='md5')
    create_time = models.DateTimeField()
    tags = models.CharField(max_length=255)
    type = models.CharField(max_length=4)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'image_name'


class ImagePath(models.Model):
    md5 = models.CharField(primary_key=True, max_length=255)
    path = models.ImageField(upload_to=settings.IMAGE_PREFIX, default='/tmp/none.jpg')

    class Meta:
        managed = False
        db_table = 'image_path'


class ImageTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=255)
    counter = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'image_tag'


class ImageType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'image_type'



