from django.db import models


class RecentScansDB(models.Model):
    NAME = models.TextField()
    MD5 = models.CharField(max_length=32)
    URL = models.TextField()
    TS = models.DateTimeField()


class Sample(models.Model):
    NAME = models.TextField()
    TYPE = models.TextField()
    SOURCE = models.TextField()
    EXTRA = models.TextField()
    MD5 = models.CharField(max_length=32)
    TS = models.DateTimeField()


class Task(models.Model):
    NAME = models.TextField()
    MEMBER = models.TextField()
    SAMPLEMD5 = models.CharField(max_length=32)
    ENGINES = models.TextField()
    PROGRESS = models.IntegerField()
    TS = models.DateTimeField()
