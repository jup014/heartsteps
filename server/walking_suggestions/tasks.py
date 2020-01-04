import pytz
import json
import random
from celery import shared_task
from datetime import timedelta, datetime, date

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
import requests

from days.services import DayService
from participants.models import Participant

from .models import SuggestionTime
from .models import Configuration
from .models import WalkingSuggestionDecision
from .models import NightlyUpdate
from .models import PoolingServiceConfiguration
from .models import PoolingServiceRequest
from .services import WalkingSuggestionService
from .services import WalkingSuggestionDecisionService
from .services import WalkingSuggestionTimeService

@shared_task
def queue_walking_suggestion(username):
    service = WalkingSuggestionTimeService(username=username)
    category = service.suggestion_time_category_at(timezone.now())
    random_minutes = random.randint(15,30)
    create_walking_suggestion.apply_async(
        countdown = random_minutes * 60,
        kwargs = {
            'username': username
        }
    )

@shared_task
def create_walking_suggestion(username):
    try:
        WalkingSuggestionDecisionService.make_decision_now(username=username)
    except WalkingSuggestionDecisionService.RandomizationUnavailable:
        pass

@shared_task
def nightly_update(username, day_string):
    dt = datetime.strptime(day_string, '%Y-%m-%d')
    day = date(dt.year, dt.month, dt.day)
    try:
        service = WalkingSuggestionService(username=username)
        service.nightly_update(day)
    except WalkingSuggestionService.Unavailable:
        return None

@shared_task
def initialize_and_update(username):
    configuration = Configuration.objects.get(user__username = username)
    day_service = DayService(user=configuration.user)
    walking_suggestion_service = WalkingSuggestionService(configuration=configuration)
    
    date_joined = day_service.get_date_at(configuration.user.date_joined)
    today = day_service.get_current_date()
    days_to_go_back = (today - date_joined).days
    date_range = [today - timedelta(days=offset+1) for offset in range(days_to_go_back)]

    while len(date_range):
        initialize_date = date_range.pop()
        try:
            walking_suggestion_service.get_initialization_days(initialize_date)
            break
        except WalkingSuggestionService.UnableToInitialize:
            pass
    
    walking_suggestion_service.initialize(initialize_date)
    NightlyUpdate.objects.filter(user = configuration.user).delete()
    
    while len(date_range):
        update_date = date_range.pop()
        walking_suggestion_service.update(update_date)
        NightlyUpdate.objects.create(
            user = configuration.user,
            day = update_date,
            updated = True
        )

@shared_task
def update_pooling_service():
    if not hasattr(settings, 'POOLING_SERVICE_URL') or not settings.POOLING_SERVICE_URL:
        return False
    url = settings.POOLING_SERVICE_URL
    
    users = [configuration.user for configuration in PoolingServiceConfiguration.objects.all()]
    
    participants = {}
    for user in users:
        participants[user.username] = {'username':user.username}

    for participant in Participant.objects.filter(user__in=users).all():
        username = participant.user.username
        participants[username]['cohort'] = participant.cohort.name
        participants[username]['study'] = participant.cohort.study.name
    for configuration in Configuration.objects.filter(user__in=users).all():
        username = configuration.user.username
        participants[username]['start'] = configuration.service_initialized_date.strftime('%Y-%m-%d')

    data = {
        'participants': [participants[x] for x in participants.keys()]
    }

    request_record = PoolingServiceRequest.objects.create(
        name = 'Pooling service update',
        url = url,
        request_data = json.dumps(data),
        request_time = timezone.now()
    )

    response = requests.post(url, json=data)

    request_record.response_code = response.status_code
    request_record.response_data = response.text
    request_record.response_time = timezone.now()
    request_record.save()
    