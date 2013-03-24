"""Tests for the views of the devices app."""
from django.test import TestCase
from django.core.urlresolvers import reverse
from nose.tools import *

from inventory.devices.tests.factories import DeviceFactory
from inventory.user.tests.factories import UserFactory

# class DevicesCheckoutViewTest(TestCase):
#     def setUp(self):
#         self.user = UserFactory()
#         self.device = DeviceFactory()
#         self.client.login(username=self.user.username,
#                             password='abc')

#     def get_view_name(self):
#         """
#         Convenience method so that if the name of this url is changed in
#         'urls.py' you would only have to change this string at this central position.
#         """
#         return 'devices:checkout'

#     def get_kwargs(self):
#         return {'pk': self.device.pk}

#     def test_view(self):
#         response = self.client.post(reverse(self.get_view_name(), 
#                                     kwargs=self.get_kwargs()),
#                                     {'action': 'checkout_selected'})
#         self.assertEqual(response.status_code, 200)

class DeviceCheckoutViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.device = DeviceFactory()
        self.client.login(username=self.user.username,
                            password='abc')

    def get_view_name(self):
        """
        Convenience method so that if the name of this url is changed in
        'urls.py' you would only have to change this string at this central position.
        """
        return 'devices:checkout'

    def get_kwargs(self):
        return {'pk': self.device.pk}

    def test_view(self):
        response = self.client.get(reverse(self.get_view_name(), 
                                    kwargs=self.get_kwargs()))
        self.assertEqual(response.status_code, 200)

class DevicesListViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username,
                            password='abc')

    def get_view_name(self):
        """
        Convenience method so that if the name of this url is changed in
         'urls.py' you would only have to change this string at this central position.
        """
        return 'devices:index'

    def test_view(self):
        response = self.client.get(reverse(self.get_view_name()))
        self.assertEqual(response.status_code, 200)

class DevicesAddViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username=self.user.username,
                            password='abc')

    def get_view_name(self):
        """
        Convenience method so that if the name of this url is changed in
         'urls.py' you would only have to change this string at this central position.
        """
        return 'devices:add'

    def test_view(self):
        response = self.client.get(reverse(self.get_view_name()))
        self.assertEqual(response.status_code, 200)

class PermissionDeniedViewTest(TestCase):
    def setUp(self):
        pass

    def get_view_name(self):
        """
        Convenience method so that if the name of this url is changed in
         'urls.py' you would only have to change this string at this central position.
        """
        return 'devices:permission_denied'

    def test_view(self):
        response = self.client.get(reverse(self.get_view_name()))
        self.assertEqual(response.status_code, 200)
