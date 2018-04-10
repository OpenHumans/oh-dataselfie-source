from django.test import TestCase, RequestFactory
import vcr
from django.conf import settings
from django.core.management import call_command
from open_humans.models import OpenHumansMember
import requests_mock


class ManagementTestCase(TestCase):
    """
    test that files are parsed correctly
    """

    def setUp(self):
        """
        Set up the app for following tests
        """
        settings.DEBUG = True
        call_command('init_proj_config')
        self.factory = RequestFactory()
        data = {"access_token": 'myaccesstoken',
                "refresh_token": 'bar',
                "expires_in": 36000}
        self.oh_member = OpenHumansMember.create(oh_id='1234',
                                                 data=data)
        self.oh_member.save()
        self.user = self.oh_member.user
        self.user.save()

    @vcr.use_cassette('main/tests/fixtures/import_test_file.yaml',
                      record_mode='none')
    def test_management_import_user(self):
        self.assertEqual(len(OpenHumansMember.objects.all()),
                         1)
        call_command('import_users',
                     infile='main/tests/fixtures/test_import.csv',
                     delimiter=',')
        old_oh_member = OpenHumansMember.objects.get(oh_id='1234')
        self.assertEqual(old_oh_member.refresh_token,
                         'bar')
        new_oh_member = OpenHumansMember.objects.get(oh_id='2345')
        self.assertEqual(new_oh_member.refresh_token,
                         'new_refresh')
