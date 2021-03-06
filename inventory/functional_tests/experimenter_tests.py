'''Functional tests for an Experimenter User'''

from nose.tools import *
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django_webtest import WebTest

from inventory.user.tests.factories import UserFactory, ExperimenterFactory
from inventory.devices.tests.factories import (IpadFactory, HeadphonesFactory,
    AdapterFactory, CaseFactory)
from inventory.comments.tests.factories import (IpadCommentFactory, 
        HeadphonesCommentFactory, AdapterCommentFactory, CaseCommentFactory)
from inventory.devices.models import Device, Ipad
from inventory.user.models import Lendee

class TestAnExperimenter(WebTest):
    csrf_checks = False

    def setUp(self):
        user = UserFactory(first_name="Ellen", last_name="Experimenter")
        self.experimenter = ExperimenterFactory(user=user)

    def test_can_login(self):
        user = self.experimenter.user
        # goes to root (not logged in)
        res = self.app.get('/')
        form = res.forms['login_form']
        # fills in login info
        form['username'] = user.username
        form['password'] = 'abc'
        # submits
        res = form.submit().follow()
        # redirected to devices
        assert_equal(res.request.path, '/devices')
        assert_true(user.is_authenticated())
        # i'm an experimenter, so I can't create a user
        assert_not_in('Create user', res)

    def test_cannot_create_device(self):
        # goes to root (logged in)
        res = self.app.get('/', user=self.experimenter.user).follow()
        assert_equal(res.request.path, '/devices/')
        assert_not_in('Add device', res)
        # tries to go directly to the add device page
        res = self.app.get('/devices/add/', user=self.experimenter.user).follow()
        # sees a not authorized warning
        assert_in('Forbidden', res)

    def test_cannot_remove_device(self):
        # a device is created
        IpadFactory()
        # goes to devices page
        res = self.app.get('/', user=self.experimenter.user).follow()
        # cannot see delete device
        assert_not_in('Delete', res)

    def test_can_see_devices(self):
        # a device is already created
        device = IpadFactory()
        # goes to the device index
        res = self.app.get('/', user=self.experimenter.user).follow()
        # sees the device name
        res.mustcontain(device.name, 
                        device.get_status_display(), 
                        device.get_condition_display(),
                        device.serial_number)

    def test_cannot_create_users(self):
        # logs in 
        res = self.app.get('/', user=self.experimenter.user).follow()
        assert_not_in('Create user', res)

    def test_can_see_device_detail(self):
        # a device is created
        device = IpadFactory()
        # goes to its detail page
        res = self.app.get('/devices/ipads/{pk}/'.format(pk=device.pk))
        res.mustcontain(device.name,
                        device.get_verbose_status(),
                        device.get_condition_display(),
                        device.serial_number)
        assert_in('Check-in Comments', res)

    def test_can_edit_ipad(self):
        # an ipad is created
        device = IpadFactory(name="iPad", 
                            make="iPad 4",
                            status=Device.CHECKED_IN_NOT_READY)
        # goes to edit page
        res = self.app.get('/devices/ipads/{pk}/edit/'.format(pk=device.pk))
        # there's a form for editing
        form = res.forms['id-edit_form']
        form['status'] = Device.CHECKED_IN_READY
        # submits
        res = form.submit().follow()
        assert_equal(res.request.path, '/devices/ipads/')
        # device is updated in db
        device = Ipad.objects.get(pk=device.pk)
        assert_equal(device.status, Device.CHECKED_IN_READY)

    def test_can_edit_ipad_comment(self):
        # A device is created
        device = IpadFactory()
        # It has a check-in comment
        comment = IpadCommentFactory(text="Just a bigger iPhone", 
                                    device=device,
                                    user=self.experimenter.user)
        # goes to the detail page
        res = self.app.get('/devices/ipads/{pk}/'.format(pk=device.pk), 
                                            user=self.experimenter.user)
        # can see the comment
        assert_in(comment.text, res)
        # clicks the edit link
        res = res.click('Edit')
        # sees a form
        assert_in('Edit comment', res)
        form = res.forms['id-edit_comment_form']
        # changes the comment text
        form['text'] = 'Or a flat MacBook Air'
        # submits the form
        res = form.submit().follow()
        # back at the detail page
        assert_equal(res.request.path, 
                    '/devices/ipads/{pk}/'.format(pk=device.pk))
        # sees the new comment text
        assert_in('Or a flat MacBook Air', res)

    def test_can_edit_headphones_comment(self):
        # a device is created
        device = HeadphonesFactory()
        # it has a comment
        comment = HeadphonesCommentFactory(device=device,
                                        user=self.experimenter.user)
        # goes to detail page
        res = self.app.get('/devices/headphones/{pk}/'.format(pk=device.pk),
                                                    user=self.experimenter.user)
        # can see the comment
        assert_in(comment.text, res)
        # clicks the edit link
        res = res.click('Edit')
        # sees a form
        assert_in('Edit comment', res)
        form = res.forms['id-edit_comment_form']
        # changes the comment text
        form['text'] = 'new text'
        # submits the form
        res = form.submit().follow()
        # back at the detail page
        assert_equal(res.request.path, 
                    '/devices/headphones/{pk}/'.format(pk=device.pk))
        # sees the new comment text
        assert_in('new text', res)

    def _test_delete_comment(self, device, comment,
                            detail_url, delete_url):

        # The initial count of comments (should be 1)
        comment_class = comment.__class__
        init_count = comment_class.objects.count()
        # goes to detail page
        res = self.app.get(detail_url,
                        user=self.experimenter.user)
        # can see the comment
        assert_in(comment.text, res)
        # clicks the delete button
        res = self.app.post(delete_url,
                            user=self.experimenter.user)
        # device was deleted from db
        assert_equal(comment_class.objects.count(), init_count - 1)
        # goes to the device detail page
        res = self.app.get(detail_url,
                            user=self.experimenter.user)
        # the comment isn't there anymore
        assert_not_in(comment.text, res)

    def test_can_delete_ipad_comment(self):
        device = IpadFactory()
        comment = IpadCommentFactory(device=device, 
                                    user=self.experimenter.user)
        self._test_delete_comment(device, comment,
                    detail_url='/devices/ipads/{pk}/'.format(pk=device.pk),
                    delete_url=reverse('comments:ipad_delete',
                                    args=(device.pk, comment.pk))
        )

    def test_can_delete_headphones_comment(self):
        device = HeadphonesFactory()
        comment = HeadphonesCommentFactory(device=device, 
                                    user=self.experimenter.user)
        self._test_delete_comment(device, comment,
                    detail_url='/devices/headphones/{pk}/'.format(pk=device.pk),
                    delete_url=reverse('comments:headphones_delete',
                                    args=(device.pk, comment.pk))
        )

    def test_can_delete_adapter_comment(self):
        device = AdapterFactory()
        comment = AdapterCommentFactory(device=device,
                                    user=self.experimenter.user)
        self._test_delete_comment(device, comment,
                    detail_url='/devices/adapters/{pk}/'.format(pk=device.pk),
                    delete_url=reverse('comments:adapter_delete',
                                    args=(device.pk, comment.pk))
        )

    def test_can_delete_case_comment(self):
        device = CaseFactory()
        comment = CaseCommentFactory(device=device,
                                    user=self.experimenter.user)
        self._test_delete_comment(device, comment,
                    detail_url='/devices/cases/{pk}/'.format(pk=device.pk),
                    delete_url=reverse('comments:case_delete',
                                    args=(device.pk, comment.pk))
        )

    def _checkin(self, device, condition='excellent', expected_status=Device.CHECKED_IN):

        checkin_url = reverse('devices:checkin', args=(device.get_cname(), 
                                                        device.pk))
        # goes to checkin url
        res = self.app.get(checkin_url, user=self.experimenter.user)
        form = res.forms['id-checkin_form']
        # enters a comment
        form['condition'] = condition
        form['comment'] = "looks good!"
        # submits
        res = form.submit().follow()
        # back at the ipad index
        assert_equal(res.request.path, '/devices/{0}/'.format(device.get_cname()))
        # assert_in("Checked in", res)
        # the device status and condition is changed in the db
        device_class = device.__class__
        device = device_class.objects.get(pk=device.pk)
        assert_equal(device.status, expected_status)
        # the device has a checkin comment
        assert_equal(device.comments.count(), 1)

    def test_can_checkin_ipad(self):
        # an ipad is created
        device = IpadFactory(status=Device.CHECKED_OUT)
        # checks it in
        self._checkin(device, expected_status=Device.CHECKED_IN_NOT_READY)

    def test_can_checkin_screatched_ipad(self):
        # an ipad is created
        device = IpadFactory(status=Device.CHECKED_OUT)
        # checks it in (sets condition to 'Scratched')
        self._checkin(device, condition='scratched', 
                            expected_status=Device.CHECKED_IN_NOT_READY)
        # devices condition is updated
        device = device.__class__.objects.get(pk=device.pk)
        assert_equal(device.condition, Device.SCRATCHED)

    def test_can_checkin_headphones(self):
        # headphones are creted
        device = HeadphonesFactory(status=Device.CHECKED_OUT)
        # checks it in
        self._checkin(device, expected_status=Device.CHECKED_IN)

    def test_can_checkin_adapter(self):
        # adapter is created
        device = AdapterFactory(status=Device.CHECKED_OUT)
        # checks it in
        self._checkin(device, expected_status=Device.CHECKED_IN)

    def test_can_checkin_case(self):
        # case is created
        device = CaseFactory(status=Device.CHECKED_OUT)
        # checks it in
        self._checkin(device, expected_status=Device.CHECKED_IN)

    def _checkout(self, device, lendee_str):
        device_type = device.get_cname(plural=True)  # e.g. 'ipads'
        checkout_url = reverse('devices:checkout', 
                        args=(device_type, device.pk))
        # goes to the checkout url
        self.app.post(checkout_url,
                        {'lendee' : lendee_str})
        checkout_confirm_url = reverse('devices:checkout_confirm', 
                                args=(device_type, device.pk))
        # goes to checkout confirm url
        self.app.post(checkout_confirm_url,
                    {'device_type': device_type,
                    'lendee': lendee_str},
                     user=self.experimenter.user)

        # reload device
        device = device.__class__.objects.get(pk=device.pk)
        # status was changed in db
        assert_equal(device.status, Device.CHECKED_OUT)
        # the lendee and lender are correct
        lender = self.experimenter.user
        try:
            # lendee is a user
            lendee = Lendee.objects.get(user__username=lendee_str)
        except ObjectDoesNotExist:
            # lendee is a subject
            subject_id = int(lendee_str.replace('-', ''))
            lendee = Lendee.objects.get(subject__subject_id=subject_id)
        assert_equal(device.lender, lender)
        assert_equal(device.lendee, lendee)

    def test_can_checkout_ipad_to_user(self):
        # an ipad is created
        device = IpadFactory(status=Device.CHECKED_IN_READY)
        # a user is created
        user = UserFactory()
        # checks out the device to the user
        self._checkout(device, user.username)

    def test_can_checkout_to_subject_with_dashes(self):
        # an ipad is created
        device = IpadFactory(status=Device.CHECKED_IN_READY)
        # checks out the device to a subject by entering their subject id
        self._checkout(device, '1-23-451')

    def test_can_checkout_to_subject_without_dashes(self):
        # an ipad is created
        device = IpadFactory(status=Device.CHECKED_IN_READY)
        # checks out the device to a subject by entering their subject id
        self._checkout(device, '123451')

    def test_can_checkout_headphones_to_user(self):
        # headphones are created
        device = HeadphonesFactory(status=Device.CHECKED_IN)
        # user is created
        user = UserFactory()
        # checks out to user
        self._checkout(device, user.username)

    def test_can_checkout_headphones_to_subject(self):
        # headphones are created
        device = HeadphonesFactory(status=Device.CHECKED_IN)
        # checks out to subject
        self._checkout(device, '123451')
