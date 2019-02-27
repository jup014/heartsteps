from django.db import models
from django.contrib.auth.models import User

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, editable=False)
    url = models.CharField(max_length=150, editable=False)

    request_data = models.TextField(editable=False)
    request_time = models.DateTimeField(editable=False)

    response_code = models.IntegerField(null=True, editable=False)
    response_data = models.TextField(null=True, editable=False)
    response_time = models.DateTimeField(null=True, editable=False)

    @property
    def sucessful(self):
        if self.response_code < 400:
            return True
        else:
            return False

    @property
    def duration(self):
        delta = self.response_time - self.request_time
        return delta.seconds

    def __str__(self):
        return "%s (%d) %s" % (self.user, self.response_code, self.url)
