from datetime import datetime

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import MorningMessageService

def format_date(date):
    return datetime.strftime(date, '%Y-%m-%d')

def parse_date(day):
    try:
        dt = datetime.strptime(day, '%Y-%m-%d').astimezone(pytz.UTC)
        return date(dt.year, dt.month, dt.day)
    except:
        raise Http404()

def check_valid_date(user, date):
    dt = datetime(date.year, date.month, date.day).astimezone(pytz.UTC)
    if dt < user.date_joined:
        raise Http404()

class MorningMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, day):
        date = parse_date(day)
        morning_message_service = MorningMessageService(
            user = request.user
        )
        try:
            message = morning_message_service.get(date)
        except MorningMessageService.MessageDoesNotExist:
            raise Http404()
        return Response({}, status=status.HTTP_200_OK)