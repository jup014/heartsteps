from django.test import TestCase
from django.urls import reverse

from .models import Participant
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from .views import FirebaseTokenView

class EnrollViewTests(TestCase):
    def test_enrollment_token(self):
        """
        Returns an auth token when valid 
        enrollment token is passed
        """
        Participant.objects.create(
            user = User.objects.create(username='test'),
            id = 123,
            enrollment_token = 'token'
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollment_token': 'token'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.data['participant_id'], 123)

    def test_no_matching_enrollment_token(self):
        """
        If the enrollment token doesn't match an object in the database
        the response returns an error
        """
        response = self.client.post(reverse('participants-enroll'), {
            'enrollment_token': 'doesnt-exist'
        })

        self.assertEqual(response.status_code, 400)

    def test_no_enrollment_token(self):
        response = self.client.post(reverse('participants-enroll'), {

        })

        self.assertEqual(response.status_code, 400)

class FirebaseTokenViewTests(TestCase):

    def test_save_token(self):
        participant = Participant.objects.create(
            user = User.objects.create(username='test'),
            id = 123,
            enrollment_token = 'token'
        )

        factory = APIRequestFactory()

        request = factory.post(reverse('participants-firebase-token'), {
            'token': 'sample-token'
        })
        force_authenticate(request, participant.user)

        response = FirebaseTokenView.as_view()(request)

        self.assertEqual(response.status_code, 200)
