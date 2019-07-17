from datetime import date
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from participants.signals import initialize_participant
from page_views.models import PageView

from .models import AdherenceAlert
from .models import AdherenceMessage
from .models import AdherenceMetric
from .models import Configuration
from .models import User
from .services import AdherenceService
from .signals import send_adherence_message as send_adherence_message_signal
from .signals import update_adherence as update_adherence_signal
from .tasks import initialize_adherence as initialize_adherence_task
from .tasks import send_adherence_message as send_adherence_message_task
from .tasks import update_adherence as update_adherence_task

@override_settings(ADHERENCE_MESSAGE_TIME='13:22')
class AdherenceConfigurationTests(TestCase):

    def setUp(self):
        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

    def test_participant_initialization_enables_configuration(self):
        user = User.objects.create(
            username = 'test'
        )

        initialize_participant.send(
            sender = User,
            user = user
        )

        configuration = Configuration.objects.get(
            user = user
        )
        self.assertTrue(configuration.enabled)
        self.assertTrue(configuration.daily_task.enabled)
        self.assertEqual(configuration.daily_task.hour, 13)
        self.assertEqual(configuration.daily_task.minute, 22)

    def test_participant_initialize_reenables_configuration(self):
        user = User.objects.create(
            username = 'test'
        )
        Configuration.objects.create(
            user = user,
            enabled = False
        )

        initialize_participant.send(
            sender = User,
            user = user
        )

        configuration = Configuration.objects.get(user = user)
        self.assertTrue(configuration.enabled)

    def test_configuration_gets_disabled(self):
        user = User.objects.create(
            username = 'test'
        )
        configuration = Configuration.objects.create(
            user = user
        )

        self.assertTrue(configuration.enabled)
        self.assertTrue(configuration.daily_task.enabled)

        configuration.enabled = False
        configuration.save()

        self.assertFalse(configuration.enabled)
        self.assertFalse(configuration.daily_task.enabled)

class AdherenceTaskTestBase(TestCase):
    
    def setUp(self):
        message_send_patch = patch.object(AdherenceMessage, 'send')
        send_patch = message_send_patch.start()
        send_patch.return_value = 'test-1234'
        self.addCleanup(message_send_patch.stop)

        initialize_adherence_patch = patch.object(initialize_adherence_task, 'apply_async')
        self.initialize_adherence_task = initialize_adherence_patch.start()
        self.addCleanup(initialize_adherence_patch.stop)

        self.user = User.objects.create(username='test')
        self.configuration = Configuration.objects.create(
            user = self.user,
            enabled = True
        )

class AdherenceInitializationTests(AdherenceTaskTestBase):

    def test_new_configuration_initializes_adherence(self):
        configuration = Configuration.objects.create(
            user = User.objects.create(username='participant'),
            enabled = False
        )

        self.initialize_adherence_task.assert_called_with(
            kwargs = {
                'username': 'participant'
            }
        )
        # First call is from setup, second is from test
        self.assertEqual(self.initialize_adherence_task.call_count, 2)

        configuration.enabled = True
        configuration.save()

        # Ensureing initialize is only called when configuration is created
        self.assertEqual(self.initialize_adherence_task.call_count, 2)

    def test_recreates_adherence(self):
        self.user.date_joined = timezone.now() - timedelta(days=3)
        self.user.save()

        initialize_adherence_task(username='test')

        dates_with_adherence = []
        for metric in AdherenceMetric.objects.order_by('-date').all():
            if metric.date not in dates_with_adherence:
                dates_with_adherence.append(metric.date)
        self.assertEqual(dates_with_adherence, [date.today() - timedelta(days=offset) for offset in range(3)])

def just_send_adherence_message(sender, adherence_alert, *args, **kwargs):
    try:
        adherence_alert.create_message('Example message')
    except AdherenceAlert.AdherenceMessageRecentlySent:
        pass

@override_settings(ADHERENCE_MESSAGE_BUFFER_HOURS=2)
class AdherenceAlertMessagesTests(AdherenceTaskTestBase):

    def setUp(self):
        super().setUp()
        send_adherence_message_signal.connect(just_send_adherence_message, sender=AdherenceAlert)
    
    def test_sends_adherence_alert(self):
        alert = AdherenceAlert.objects.create(
            user = self.user,
            category = 'test-category',
            start = timezone.now()
        )
        service = AdherenceService(configuration = self.configuration)

        service.send_adherence_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.adherence_alert, alert)
        self.assertEqual(message.body, 'Example message')

    def test_does_not_send_if_message_recently_sent(self):
        alert = AdherenceAlert.objects.create(
            user = self.user,
            category = 'test-category',
            start = timezone.now()
        )
        AdherenceMessage.objects.create(
            adherence_alert = alert,
            body = 'Previously sent message'
        )
        service = AdherenceService(configuration = self.configuration)

        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 1)

    def test_will_send_if_no_message_recently_sent(self):
        alert = AdherenceAlert.objects.create(
            user = self.user,
            category = 'test-category',
            start = timezone.now()
        )
        message = AdherenceMessage.objects.create(
            adherence_alert = alert,
            body = 'Previously sent message'
        )
        message.created = timezone.now() - timedelta(hours=3)
        message.save()
        service = AdherenceService(configuration = self.configuration)

        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 2)

    def test_sends_messages_in_alert_start_order(self):
        AdherenceAlert.objects.create(
            user = self.user,
            category = 'test-category',
            start = timezone.now()
        )
        AdherenceAlert.objects.create(
            user = self.user,
            category = 'other-category',
            start = timezone.now() - timedelta(hours=1)
        )
        service = AdherenceService(configuration = self.configuration)

        service.send_adherence_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.adherence_alert.category, 'other-category')


class AdherenceTaskTests(AdherenceTaskTestBase):

    @patch.object(update_adherence_signal, 'send')
    def test_update_adherence(self, update_adherence_signal):

        update_adherence_task(
            username = self.user.username
        )

        update_adherence_signal.assert_called_with(
            sender = User,
            user = self.user,
            date = date.today()
        )

    @patch.object(AdherenceService, 'send_adherence_message')
    @patch.object(update_adherence_signal, 'send')
    def test_send_adherence_message(self, update_adherence_signal, send_adherence_message):

        send_adherence_message_task(
            username = self.user.username
        )

        send_adherence_message.assert_called()
        update_adherence_signal.assert_called_with(
            sender = User,
            user = self.user,
            date = date.today()
        )


class AppInstallationAdherenceTests(AdherenceTaskTestBase):

    def test_app_installation_checked_with_update(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        update_adherence_task(
            username = self.user.username
        )

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_INSTALLED
        )
        self.assertEqual(metric.date, date.today())
        self.assertTrue(metric.value)

    @patch.object(AdherenceService, 'get_message_text_for', return_value='Example text')
    def test_send_adherence_message_if_7_days_fitbit_and_no_install(self, get_message_text_for):
        for offset in range(7):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today(),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today(),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        message = AdherenceMessage.objects.get()
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.category, 'app-installed')
        self.assertEqual(message.body, 'Example text')
        get_message_text_for.assert_called_with('app-installed')

    def test_does_not_send_adherence_message_if_installed(self):
        for offset in range(7):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )
        AdherenceMetric.objects.update_or_create(
            user = self.user,
            date = date.today(),
            category = AdherenceMetric.APP_INSTALLED,
            defaults = {
                'value': True
            }
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 0)       

    def test_send_adherence_message_sends_only_3_messages(self):
        for offset in range(9):
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.APP_INSTALLED,
                value = False
            )
            AdherenceMetric.objects.create(
                user = self.user,
                date = date.today() - timedelta(days=offset),
                category = AdherenceMetric.WORE_FITBIT,
                value = True
            )
        AdherenceMessage.objects.create(
            user = self.user,
            date = date.today() - timedelta(2),
            category = 'app-installed',
            body = 'first message'
        )
        AdherenceMessage.objects.create(
            user = self.user,
            date = date.today() - timedelta(1),
            category = 'app-installed',
            body = 'second message'
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 3)

        service.send_message()

        self.assertEqual(AdherenceMessage.objects.count(), 3)

class AppUsedAdherenceTests(AdherenceTaskTestBase):

    def test_app_used_checked_nightly(self):
        PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now()
        )

        update_adherence_task(
            username = self.user.username
        )

        metric = AdherenceMetric.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_USED    
        )
        self.assertEqual(metric.date, date.today())

    def test_app_used_adherence_alert_created_after_4_days(self):
        page_view = PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(days=4)
        )

        update_adherence_task(
            username = self.user.username
        )

        alert = AdherenceAlert.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_USED
        )
        self.assertEqual(alert.start, page_view.time)

    def test_app_used_adherence_alert_closed_if_new_page_view(self):
        AdherenceAlert.objects.create(
            user = self.user,
            category = AdherenceMetric.APP_USED,
            start = timezone.now() - timedelta(days=7)
        )
        page_view = PageView.objects.create(
            user = self.user,
            uri = 'foo',
            time = timezone.now() - timedelta(hours=7)
        )

        update_adherence_task(
            username = self.user.username
        )

        alert = AdherenceAlert.objects.get(
            user = self.user,
            category = AdherenceMetric.APP_USED
        )
        self.assertEqual(alert.end, page_view.time)


    @override_settings(STUDY_PHONE_NUMBER='(555) 555-5555')
    @patch('adherence_messages.receivers.render_to_string', return_value='Example text')
    def test_adherence_message_sent_no_use_4_days(self, render_to_string):
        AdherenceAlert.objects.create(
            user = self.user,
            category = AdherenceMetric.APP_USED,
            start = timezone.now() - timedelta(days=4)
        )

        service = AdherenceService(configuration = self.configuration)
        service.send_adherence_message()

        message = AdherenceMessage.objects.get(
            adherence_alert__user = self.user,
            adherence_alert__category = 'app-used'
        )
        self.assertEqual(message.body, 'Example text')
        render_to_string.assert_called_with(
            template_name = 'adherence_messages/app-used.txt',
            context = {
                'study_phone_number': '(555) 555-5555'
            }
        )

    def test_adherence_message_sent_once(self):
        alert = AdherenceAlert.objects.create(
            user = self.user,
            category = AdherenceMetric.APP_USED,
            start = timezone.now() - timedelta(days=6)
        )
        message = AdherenceMessage.objects.create(
            adherence_alert = alert,
            body = 'foo bar'
        )
        message.created = timezone.now() - timedelta(days=5)
        message.save()

        service = AdherenceService(configuration = self.configuration)
        service.send_adherence_message()

        self.assertEqual(AdherenceMessage.objects.count(), 1)
