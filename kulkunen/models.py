from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model

from resources.models.utils import format_dt_range

User = get_user_model()

DRIVERS = (
    ('sipass', 'Siemens SiPass'),
)


class AccessControlUser(models.Model):
    system = models.ForeignKey('AccessControlSystem', related_name='users', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='access_control_users')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    driver_data = JSONField(null=True, blank=True)

    def __str__(self) -> str:
        name = ' '.join([x for x in (self.first_name, self.last_name) if x])
        user_uuid = str(self.user.uuid) if self.user.uuid else _("[No identifier]")
        if name:
            return _("User {uuid}: {name}").format(uuid=user_uuid, name=name)
        else:
            return _("User {uuid}").format(uuid=user_uuid)


class AccessControlGrant(models.Model):
    user = models.ForeignKey(AccessControlUser, related_name='grants')
    resource = models.ForeignKey('AccessControlResource', related_name='grants')

    # If a Respa reservation is deleted, it will be marked as None here.
    # AccessControlReservation with reservation == None should be deleted.
    reservation = models.ForeignKey(
        'resources.Reservation', on_delete=models.SET_NULL, null=True, related_name='access_control_grants'
    )
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_code = models.CharField(verbose_name=_('access code'), max_length=32, null=True, blank=True)

    driver_data = JSONField(null=True, blank=True)

    def __str__(self) -> str:
        time_range = format_dt_range(settings.LANGUAGES[0][0], self.starts_at, self.ends_at)
        return _("Grant for {user} {time_range} created at {created_at}").format(
            user=self.user, time_range=time_range, created_at=self.created_at
        )

    def revoke(self):
        pass


class AccessControlResource(models.Model):
    system = models.ForeignKey(
        'AccessControlSystem', related_name='resources', on_delete=models.CASCADE,
        verbose_name=_('system')
    )
    # If a Respa resource is deleted, it will be marked as None here.
    # AccessControlResources with resource == None should be deleted.
    resource = models.ForeignKey(
        'resources.Resource', related_name='access_control_resources', on_delete=models.SET_NULL,
        verbose_name=_('resource'), null=True
    )
    identifier = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_('identifier'),
        help_text=_('Identifier of resource in the access control system (if any)')
    )

    driver_data = JSONField(null=True, blank=True)

    class Meta:
        unique_together = (('system', 'resource'),)
    # - SiPass cardholder credential profile is an attribute of Resource

    def __str__(self) -> str:
        return str(self.uuid) if self.uuid else _("[No identifier]")

    def grant_access(self, user: AccessControlUser, start_time, end_time) -> AccessControlGrant:
        pass


class AccessControlSystem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    driver = models.CharField(max_length=30, choices=DRIVERS)

    reservation_leeway = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_('reservation leeway'),
        help_text=_('How many minutes before and after the reservation the access will be allowed')
    )

    # - SiPass default credential profile is an attribute of System
    # - SiPass cardholder workgroup is an attribute of System
    # - SiPass URL
    # - SiPass username, password
    driver_config = JSONField(null=True, blank=True, help_text=_('Driver-specific configuration'))
    driver_data = JSONField(null=True, editable=False, help_text=_('Internal driver data'))

    def __str__(self) -> str:
        return "{name} ({driver})".format(name=self.name, driver=self.driver)

    def _get_driver(self):
        pass

    def get_resources(self):
        pass

    def revoke_access(self, grant: AccessControlGrant):
        pass
