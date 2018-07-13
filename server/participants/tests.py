from django.urls import reverse

from .models import Participant
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

class EnrollViewTests(APITestCase):
    def test_enrollment_token(self):
        """
        Returns an authorization token and participant's heartsteps_id when a
        valid enrollment token is passed
        """
        Participant.objects.create(
            user = User.objects.create(username="test"),
            heartsteps_id = "sample-id",
            enrollment_token = 'token'
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'token'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response['Authorization-Token'])
        self.assertEqual(response.data['heartstepsId'], "sample-id")


    def test_enrollment_create_user(self):
        """
        Creates and authenticates a user if the participant doesn't have a user
        """
        Participant.objects.create(
            heartsteps_id = "sample-id",
            enrollment_token="token"
        )

        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'token'
        })

        self.assertEqual(response.status_code, 200)

        participant = Participant.objects.get(heartsteps_id = "sample-id")
        self.assertIsNotNone(participant.user)



    def test_no_matching_enrollment_token(self):
        """
        If the enrollment token doesn't match an object in the database
        the response returns an error
        """
        response = self.client.post(reverse('participants-enroll'), {
            'enrollmentToken': 'doesnt-exist'
        })

        self.assertEqual(response.status_code, 400)

    def test_no_enrollment_token(self):
        response = self.client.post(reverse('participants-enroll'), {})
        
        self.assertEqual(response.status_code, 400)

# class DeviceRegistration(APITestCase):

#     def test_save_token(self):
#         participant = Participant.objects.create(
#             user = User.objects.create(username='test'),
#             id = 123,
#             enrollment_token = 'token'
#         )

#         self.client.force_authenticate(participant.user)

#         response = self.client.post(reverse('participants-device'), {
#             'registration': 'sample-token',
#             'device_type': 'web'
#         })

#         self.assertEqual(response.status_code, 200)
