from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.dateformat import format

from rest_framework.authtoken.models import Token
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule

from .models import Cohort
from .models import Participant
from .models import Study
from .services import ParticipantService

def initialize_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.initialize()

def deactivate_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.deactivate()

def update_participant(modeladmin, request, queryset):
    for participant in queryset.all():
        service = ParticipantService(participant)
        service.update()

class ParticipantAdmin(admin.ModelAdmin):
    readonly_fields = ['daily_update']

    list_display = ['__str__', '_is_enrolled', '_is_active']

    actions = [initialize_participant, deactivate_participant, update_participant]

    def daily_update(self, instance):
        if instance.daily_task:
            next_run_datetime = instance.daily_task.get_next_run_time()
            if next_run_datetime:
                return 'Next update at %s' % (format(next_run_datetime, settings.DATETIME_FORMAT))
            else:
                return 'No next run?'
        else:
            return 'No daily update'
    
    daily_update.short_description = 'Daily update'

admin.site.register(Participant, ParticipantAdmin)

class CohortAdmin(admin.ModelAdmin):
    pass

admin.site.register(Cohort, CohortAdmin)

class StudyAdmin(admin.ModelAdmin):
    pass
admin.site.register(Study, StudyAdmin)
