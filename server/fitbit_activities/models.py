import uuid, pytz, math
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ImproperlyConfigured

from fitbit_api.models import FitbitAccount

class FitbitActivityType(models.Model):
    fitbit_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class FitbitActivity(models.Model):
    account = models.ForeignKey(FitbitAccount)
    fitbit_id = models.CharField(max_length=50)

    type = models.ForeignKey(FitbitActivityType, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    average_heart_rate = models.IntegerField(null=True)

    payload = JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        unique_together = [('account', 'fitbit_id')]

    @property
    def duration(self):
        if self.start_time and self.end_time:
            difference = self.end_time - self.start_time
            return math.ceil(difference.seconds/60)
        else:
            return 0

class FitbitDay(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(FitbitAccount)
    date = models.DateField()
    _timezone = models.CharField(max_length=50, default=pytz.UTC.zone)

    step_count = models.PositiveIntegerField(default=0)
    _distance = models.DecimalField(default=0, max_digits=9, decimal_places=3)
    average_heart_rate = models.PositiveIntegerField(default=0)
    wore_fitbit = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        unique_together = ('account', 'date')

    @property
    def timezone(self):
        return self.get_timezone()

    @property
    def distance(self):
        return float(self._distance)

    @distance.setter
    def distance(self, value):
        self._distance = value

    def get_minute_level_data(self):
        data_dict = {}
        for unprocessed_data in self.unprocessed_data.all():
            if unprocessed_data.category not in ['heart rate', 'steps']:
                continue
            category = unprocessed_data.category
            for d in unprocessed_data.payload:
                _time = d['time']
                if _time not in data_dict:
                    data_dict[_time] = {}
                data_dict[_time][category] = d['value']
        
        data = []
        time = datetime(self.date.year, self.date.month, self.date.day)
        endtime = time + timedelta(days=1)
        while time < endtime:
            _time_str = time.strftime('%H:%M:%S')
            steps = None
            heart_rate = None
            if _time_str in data_dict:
                if 'steps' in data_dict[_time_str]:
                    steps = data_dict[_time_str]['steps']
                if 'heart rate' in data_dict[_time_str]:
                    heart_rate = data_dict[_time_str]['heart rate']
            data.append({
                'date': self.date.strftime('%Y-%m-%d'),
                'time': _time_str,
                'heart_rate': heart_rate,
                'steps': steps
            })
            time = time + timedelta(minutes=1)
        return data

    def get_minutes_worn(self):
        day_start = self.get_start_datetime()
        active_day_start = day_start.replace(hour=8)
        active_day_end = day_start.replace(hour=20)

        total_heart_rates = FitbitMinuteHeartRate.objects.filter(
            account = self.account,
            time__range = [
                active_day_start,
                active_day_end
            ],
            heart_rate__gt = 0
        ).count()
        return total_heart_rates

    def get_wore_fitbit(self):
        if not hasattr(settings, 'FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES'):
            raise ImproperlyConfigured('No FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES')
        minimum_wear_minutes = settings.FITBIT_ACTIVITY_DAY_MINIMUM_WEAR_DURATION_MINUTES
        minutes_worn = self.get_minutes_worn()
        if minutes_worn >= minimum_wear_minutes:
            return True
        else:
            return False
        
    def get_timezone(self):
        return pytz.timezone(self._timezone)
    
    def get_start_datetime(self):
        timezone = self.get_timezone()
        return timezone.localize(datetime(
            year = self.date.year,
            month = self.date.month,
            day = self.date.day,
            hour = 0,
            minute = 0
        ))

    def get_end_datetime(self):
        start_time = self.get_start_datetime()
        return start_time + timedelta(days=1)

    @property
    def activities(self):
        activities = FitbitActivity.objects.filter(
            account = self.account,
            start_time__range = [self.get_start_datetime(), self.get_end_datetime()]
        )
        return list(activities)

    def __str__(self):
        return "%s: %s" % (self.account, self.date.strftime('%Y-%m-%d'))

class FitbitMinuteStepCount(models.Model):
    account = models.ForeignKey(FitbitAccount)
    time = models.DateTimeField()
    steps = models.IntegerField()

class FitbitMinuteHeartRate(models.Model):
    account = models.ForeignKey(FitbitAccount)
    time = models.DateTimeField()
    heart_rate = models.IntegerField()

class FitbitDailyUnprocessedData(models.Model):
    account = models.ForeignKey(FitbitAccount)
    day = models.ForeignKey(FitbitDay, related_name='unprocessed_data')
    category = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50, null=True, blank=True)

    payload = JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('day', 'category')

