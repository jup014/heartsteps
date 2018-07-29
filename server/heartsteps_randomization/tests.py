from django.urls import reverse

from unittest.mock import patch
from django.test import override_settings

from .models import Decision
from django.contrib.auth.models import User
from fcm_django.models import FCMDevice

from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

class DecisionView(APITestCase):
    
    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('heartsteps_randomization.tasks.make_decision.delay')
    def test_creates_decision(self, make_decision):
        user = User.objects.create(username="test")

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('heartsteps-decisions-create'))
        
        self.assertEqual(response.status_code, 201)

        decision = Decision.objects.get(user=user, a_it=None)
        
        self.assertIsNotNone(decision)
        make_decision.assert_called()

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('heartsteps_randomization.tasks.make_decision.delay')
    def test_updates_decision(self, make_decision):
        user = User.objects.create(username="test")
        device = FCMDevice.objects.create(user=user, registration_id="123", type="web", active=True)

        decision = Decision.objects.create(
            user = user
        )

        self.client.force_authenticate(user=user)
        response = self.client.post(reverse('heartsteps-decisions-update', kwargs = {
            'decision_id': decision.id
        }))

        self.assertEqual(response.status_code, 200)
        make_decision.assert_called()


