from django.shortcuts import render

from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from .models import StepGoals

def insertSteps():
    daily_step_goal_log = StepGoals()

    daily_step_goal_log.step_goal = getNewGoal()
    daily_step_goal_log.date = datetime.today()
    daily_step_goal_log.save()

def getNewGoal():
    last_ten = StepGoals.objects.all().order_by('-id')[:10]
    last_ten_in_ascending_order = reversed(last_ten)

    new_goal = last_ten_in_ascending_order[5]

    return new_goal

class DailyStepGoalsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        step_goals = StepGoals.objects.filter(
            user = request.user
        ).order_by('date') \
        .all()

        if step_goals:
            serialized_step_goals = []
            for step_goal in step_goals:
                serialized_step_goals.append({
                    'date': step_goal.date.strftime('%Y-%m-%d'),
                    'step_goal': step_goal.step_goal
                })
            return Response(serialized_step_goals)
        else:
            return Response('No step goals', status=status.HTTP_404_NOT_FOUND)
