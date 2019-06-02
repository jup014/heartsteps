import uuid
import math
from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth import get_user_model

from activity_summaries.models import Day
from days.services import DayService
from surveys.models import Survey, Question

User = get_user_model()

class WeekQuestion(Question):
    pass

class WeekSurvey(Survey):
    QUESTION_MODEL = WeekQuestion

class Week(models.Model):
    uuid = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(User)
    number = models.IntegerField(null=True)

    start_date = models.DateField()
    end_date = models.DateField()

    goal = models.IntegerField(null=True)
    confidence = models.FloatField(null=True)

    survey = models.ForeignKey(WeekSurvey, null=True)

    class Meta:
        ordering = ['start_date']

    @property
    def id(self):
        return str(self.uuid)

    @property
    def start(self):
        return self.__localize_datetime(datetime(
            year = self.start_date.year,
            month = self.start_date.month,
            day = self.start_date.day,
            hour = 0,
            minute = 0
        ))

    @property
    def end(self):
        return self.__localize_datetime(datetime(
            year = self.end_date.year,
            month = self.end_date.month,
            day = self.end_date.day,
            hour = 23,
            minute = 59
        ))

    def __localize_datetime(self, time):
        service = DayService(user=self.user)
        tz = service.get_current_timezone()
        return tz.localize(time)

    def get_default_goal(self):
        days_in_previous_week = Day.objects.filter(
            user = self.user,
            date__range = [
                self.start_date - timedelta(days=7),
                self.start_date - timedelta(days=1)
            ]
        ).all()

        total_minutes = 0
        for day in days_in_previous_week:
            total_minutes += day.total_minutes
        if total_minutes > 0:
            total_minutes += 20
        else:
            total_minutes = 90

        rounded_minutes = int(5 * math.floor(float(total_minutes)/5))

        if rounded_minutes > 150:
            rounded_minutes = 150
        return rounded_minutes

    def __str__(self):
        return "%s to %s (%s)" % (self.start_date, self.end_date, self.user)
