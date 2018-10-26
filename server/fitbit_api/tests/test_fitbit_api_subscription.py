from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from fitbit_api.models import FitbitSubscription, FitbitSubscriptionUpdate, FitbitAccount
from fitbit_api.services import FitbitClient
from fitbit_api.tasks import subscribe_to_fitbit

def make_fitbit_account(username='test'):
    return FitbitAccount.objects.create(
        user = User.objects.create(username=username),
        fitbit_user = 'fake-%s' % (username),
        access_token = 'access-token',
        refresh_token = 'refresh-token',
        expires_at = 1234
    )

class FitbitApiSubscriptionTest(TestCase):

    @patch.object(FitbitClient, 'is_subscribed', return_value=False)
    @patch.object(FitbitClient, 'subscribe', return_value=True)
    def test_creates_subscription(self, subscribe, is_subscribed):
        fitbit_account = make_fitbit_account()

        subscribe_to_fitbit(fitbit_account.user.username)

        subscribe.assert_called()

    @patch.object(FitbitClient, 'is_subscribed', return_value=True)
    @patch.object(FitbitClient, 'subscribe', return_value=True)
    def test_subscription_does_not_create_if_exists(self, subscribe, is_subscribed):
        fitbit_account = make_fitbit_account()

        subscribe_to_fitbit(fitbit_account.user.username)

        subscribe.assert_not_called()

class FitbitApiSubscriptionVerify(APITestCase):

    @patch.object(FitbitClient, 'verify_subscription_code', return_value=True)
    def test_responds_to_verify(self, verify_subscription_code):
        response = self.client.get(reverse('fitbit-subscription'), {
            'verify': 'successful-code'
        })
        self.assertEqual(response.status_code, 204)
        verify_subscription_code.assert_called_with('successful-code')

    @patch.object(FitbitClient, 'verify_subscription_code', return_value=False)
    def test_responds_to_incorrect_verify(self, verify_subscription_code):
        response = self.client.get(reverse('fitbit-subscription'), {
            'verify': 'incorrect-code'
        })
        self.assertEqual(response.status_code, 404)
        verify_subscription_code.assert_called_with('incorrect-code')

class SubscriptionUpdate(APITestCase):

    def setUp(self):
        self.patcher = patch('fitbit_api.tasks.update_fitbit_data.apply_async')
        self.mock_update_fitbit = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_subscription_update(self):
        subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account()
        )
        
        response = self.client.post(reverse('fitbit-subscription'), [{
            'ownerId': subscription.fitbit_account.fitbit_user,
            'subscriptionId': str(subscription.uuid),
            'date': '2018-08-17'
        }], format="json")

        self.assertEqual(response.status_code, 204)
        updates = FitbitSubscriptionUpdate.objects.all()
        self.assertEqual(len(updates), 1)
        self.mock_update_fitbit.assert_called()

    def test_subscription_updates_with_multiple_subscriptions(self):
        subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account()
        )
        other_subscription = FitbitSubscription.objects.create(
            fitbit_account = make_fitbit_account('other_account')
        )

        response = self.client.post(reverse('fitbit-subscription'), [
            {
                'ownerId': subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(subscription.uuid),
                'date': '2018-09-18'
            }, {
                'ownerId': subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(subscription.uuid),
                'date': '2018-09-20'
            }, {
                'ownerId': other_subscription.fitbit_account.fitbit_user,
                'subscriptionId': str(other_subscription.uuid),
                'date': '2018-09-20'
            }
        ], format="json")

        self.assertEqual(response.status_code, 204)
        updates = FitbitSubscriptionUpdate.objects.all()
        self.assertEqual(len(updates), 3)
        self.assertEqual(self.mock_update_fitbit.call_count, 3)
        self.mock_update_fitbit.assert_any_call(kwargs={
            'username': subscription.fitbit_account.user.username,
            'date_string': '2018-09-18'
        })
        self.mock_update_fitbit.assert_any_call(kwargs={
            'username': subscription.fitbit_account.user.username,
            'date_string': '2018-09-20'
        })
        self.mock_update_fitbit.assert_any_call(kwargs={
            'username': other_subscription.fitbit_account.user.username,
            'date_string': '2018-09-20'
        })
