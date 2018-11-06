import uuid, random
from datetime import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.contrib.auth.models import User
from behavioral_messages.models import ContextTag as MessageTag, MessageTemplate
from push_messages.models import Message as PushMessage
from push_messages.services import PushMessageService

class ContextTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=25)

    name = models.CharField(max_length=50, null=True, blank=True)
    dashboard = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.tag

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)

    time = models.DateTimeField()

    a_it = models.NullBooleanField(null=True, blank=True)
    pi_it = models.FloatField(null=True, blank=True)

    tags = models.ManyToManyField(ContextTag)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time']

    def decide(self):
        if not hasattr(settings, 'RANDOMIZATION_FIXED_PROBABILITY'):
            raise ImproperlyConfigured("No RANDOMIZATION_FIXED_PROBABILITY")
        self.pi_it = settings.RANDOMIZATION_FIXED_PROBABILITY
        self.a_it = random.random() < self.pi_it
        self.save()
        return self.a_it

    def get_context(self):
        return [tag.tag for tag in self.tags.all()]

    def add_context(self, tag_text):
        tag, _ = ContextTag.objects.get_or_create(
            tag = tag_text
        )
        self.tags.add(tag)

    def is_complete(self):
        if self.a_it is not None:
            return True
        else:
            return False

    def __str__(self):
        formatted_time = self.time.strftime("%Y-%m-%d at %H:%m")
        if self.a_it is None:
            return "On %s for %s (undecided)" % (formatted_time, self.user)
        else:
            return "On %s for %s (decided)" % (formatted_time, self.user)

class DecisionContext(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.ForeignKey(Decision)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decision = models.OneToOneField(Decision)

    message_template = models.ForeignKey(MessageTemplate)
    sent_message = models.OneToOneField(PushMessage, null=True, blank=True, related_name="randomization_message")
