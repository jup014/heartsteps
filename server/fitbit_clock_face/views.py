from datetime import datetime
import pytz
import random

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from watch_app.models import StepCount
from watch_app.signals import step_count_updated

from .models import ClockFace, User

class CreateClockFace(APIView):

    def post(self, request):
        clock_face = ClockFace.objects.create()
        return Response({
            'pin': clock_face.pin,
            'token': clock_face.token
        })

class ClockFaceStatus(APIView):

    def get(self, request):
        if 'HTTP_CLOCK_FACE_PIN' in request.META and 'HTTP_CLOCK_FACE_TOKEN' in request.META:
            try:
                clock_face = ClockFace.objects.get(
                    pin = request.META['HTTP_CLOCK_FACE_PIN'],
                    token = request.META['HTTP_CLOCK_FACE_TOKEN']
                )
                username = None
                if clock_face.user:
                    username = clock_face.user.username
                username = clock_face.user
                return Response({
                    'paired': clock_face.paired,
                    'pin': clock_face.pin,
                    'token': clock_face.token,
                    'username': clock_face.username
                })
            except ClockFace.DoesNotExist:
                pass
        return Response('Pin and Token Invalid', status=status.HTTP_401_UNAUTHORIZED)

class ClockFacePair(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            clock_face = ClockFace.objects.get(
                user = request.user
            )
            return Response({
                'pin': clock_face.pin,
                'created': clock_face.created
            })
        except ClockFace.DoesNotExist:
            return Response('No matching clock face', status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if 'pin' in request.data:
            try:
                clock_face = ClockFace.objects.get(
                    pin = request.data['pin']
                )
                if clock_face.user is not None:
                    if clock_face.user.id == request.user.id:
                        return Response({
                            'pin': clock_face.pin,
                            'token': clock_face.token
                        })
                    else:
                        return Response('Clock face not available', status=status.HTTP_400_BAD_REQUEST)
                else:
                    ClockFace.objects.filter(user = request.user).delete()
                clock_face.user = request.user
                clock_face.save()
                return Response({
                    'pin': clock_face.pin,
                    'created': clock_face.created
                }, status=status.HTTP_201_CREATED)
            except ClockFace.DoesNotExist:
                return Response('Clock Face Pin Not Found', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Need pin', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            clock_face = ClockFace.objects.get(
                user = request.user
            )
            clock_face.delete()
            return Response('Deleted', status=HTTP_200_OK)
        except ClockFace.DoesNotExist:
            return Response('Not found', status=status.HTTP_404_NOT_FOUND)



class ClockFaceStepCounts(APIView):

    def get(self, request):

        if request.user.is_authenticated():
            step_counts = []
            for step_count in StepCount.objects.filter(user=request.user).order_by('-end')[:10]:
                step_counts.append({
                    'start': step_count.start.isoformat(),
                    'end': step_count.end.isoformat(),
                    'steps': step_count.steps
                })
            return Response({
                'step_counts': step_counts
            })

        else:
            return Response('Not authorized', status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if 'HTTP_CLOCK_FACE_PIN' in request.META and 'HTTP_CLOCK_FACE_TOKEN' in request.META:
            try:
                clock_face = ClockFace.objects.get(
                    pin = request.META['HTTP_CLOCK_FACE_PIN'],
                    token = request.META['HTTP_CLOCK_FACE_TOKEN']
                )
                username = None
                if clock_face.user:
                    if 'step_counts' in request.data and isinstance(request.data['step_counts'], list):
                        last_step_count = None
                        step_counts = []
                        for step_count in request.data['step_counts']:
                            time = datetime.utcfromtimestamp(step_count['time']/1000).astimezone(pytz.UTC)
                            if last_step_count:
                                start_time = datetime.utcfromtimestamp(last_step_count['time']/1000).astimezone(pytz.UTC)
                                step_count_difference = step_count['steps'] - last_step_count['steps']
                                if step_count_difference < 0:
                                    step_count_difference = step_count['steps']
                                step_counts.append({
                                    'start': start_time,
                                    'end': time,
                                    'steps': step_count_difference
                                })
                            last_step_count = step_count
                        for step_count in step_counts:
                            StepCount.objects.update_or_create(
                                user = clock_face.user,
                                start = step_count['start'],
                                end = step_count['end'],
                                defaults = {
                                    'steps': step_count['steps']
                                }
                            )
                        step_count_updated.send(User, username=clock_face.user.username)
                        return Response('', status=status.HTTP_201_CREATED)
                    return Response('step_counts not included', status=status.HTTP_400_BAD_REQUEST)

            except ClockFace.DoesNotExist:
                pass
        return Response('Pin and Token Invalid', status=status.HTTP_401_UNAUTHORIZED)
