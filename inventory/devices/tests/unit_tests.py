'''Unit tests for the devices models.'''

from nose.tools import *
from django.test import TestCase

from inventory.devices.models import *
from inventory.comments.models import *
from inventory.devices.tests.factories import (IpadFactory,
    HeadphonesFactory, create_device_factories)


class IpadTest(TestCase):
    def setUp(self):
        self.ipad = IpadFactory()
    def test_model(self):
        ipad = IpadFactory()
        assert_true(ipad.pk)
        assert_true(ipad.status)
        assert_true(ipad.created_at)
        assert_true(ipad.updated_at)
        assert_false(ipad.lendee)
        assert_false(ipad.lender)

    def test_saving_to_database(self):
        init_count = Ipad.objects.count()
        IpadFactory()
        assert_equal(Ipad.objects.count(), init_count + 1)

    def test_check_in(self):
        self.ipad.check_in(condition='excellent')
        assert_equal(self.ipad.status, Device.CHECKED_IN_NOT_READY)

        self.ipad.check_in(condition='scratched')
        assert_equal(self.ipad.status, Device.CHECKED_IN_NOT_READY)
        assert_equal(self.ipad.condition, Device.SCRATCHED)

        self.ipad.check_in(condition='broken')
        assert_equal(self.ipad.status, Device.BROKEN)
        assert_equal(self.ipad.condition, Device.BROKEN)

        self.ipad.check_in(condition='missing')
        assert_equal(self.ipad.status, Device.MISSING)
        assert_equal(self.ipad.condition, Device.MISSING)

    def test_checkout_with_other_devices(self):
        assert False, 'finish me'


class HeadphonesTest(TestCase):
    def setUp(self):
        self.headphones = HeadphonesFactory()

    def test_model(self):
        headphones = HeadphonesFactory()
        assert_true(headphones.pk)
        assert_true(headphones.status)
        assert_true(headphones.created_at)
        assert_true(headphones.updated_at)
        assert_false(headphones.lendee)
        assert_false(headphones.lender)

    def test_display_status(self):
        headphones = HeadphonesFactory(status=Device.CHECKED_IN)
        assert_equal(headphones.get_verbose_status(),
                    'Checked in')

    def test_check_in(self):
        self.headphones.check_in(condition='excellent')
        assert_equal(self.headphones.status, Device.CHECKED_IN)

        self.headphones.check_in(condition='scratched')
        assert_equal(self.headphones.status, Device.CHECKED_IN)
        assert_equal(self.headphones.condition, Device.SCRATCHED)

        self.headphones.check_in(condition='broken')
        assert_equal(self.headphones.status, Device.BROKEN)
        assert_equal(self.headphones.condition, Device.BROKEN)

        self.headphones.check_in(condition='missing')
        assert_equal(self.headphones.status, Device.MISSING)
        assert_equal(self.headphones.condition, Device.MISSING)

class FactoryTest(TestCase):
    def test_create_device_factories(self):
        ipad, headphones, adapter, case = create_device_factories()
        assert_in('ipad', ipad.make.lower())
        assert_in('headphones', headphones.make.lower())
        assert_in('adapter', adapter.make.lower())
        assert_in('case', case.make.lower())

