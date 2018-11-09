from django.db import models
from django.contrib.auth.models import User

class Participant(models.Model):
    """
    Represents a study participant

    When the participant is enrolled, a user is created.
    """
    heartsteps_id = models.CharField(primary_key=True, unique=True, max_length=25)
    enrollment_token = models.CharField(max_length=10, unique=True)
    birth_year = models.CharField(max_length=4, null=True, blank=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def enroll(self):
        user, _ = User.objects.get_or_create(
            username = self.heartsteps_id
        )
        self.user = user
        self.save()

    def __str__(self):
            if self.user:
                return "%s (enrolled)" % (self.heartsteps_id)
            return self.heartsteps_id