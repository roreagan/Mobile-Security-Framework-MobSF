from django.db import models


# Create your models here.
class ManualAnalyzerAndroid(models.Model):
    MD5 = models.CharField(max_length=32)
    ENGINES = models.TextField()
    FINISHES = models.TextField()
    HARDCODED = models.TextField()
    DATABASE = models.TextField()
    CONFIG_MANIPULATION = models.TextField()
    SOURCE_MANIPULATION = models.TextField()
    DATABASE_MANIPULATION = models.TextField()
    COMMUNICATION_PLAIN = models.TextField()
    CERT_LOCKED = models.TextField()
    REPLAY = models.TextField()
    TIMEOUT = models.TextField()
    HIJACK = models.TextField()
    MSG_DOS = models.TextField()
    REGISTER = models.TextField()
    LOGIN = models.TextField()
    NETWORK = models.TextField()
    CLOUD_AUTH = models.TextField()
    DEVICE_AUTH = models.TextField()
    DEVICE_CLOUD = models.TextField()
    FIRMWARE_UPDATE = models.TextField()
    FIRMWARE_STORAGE = models.TextField()
