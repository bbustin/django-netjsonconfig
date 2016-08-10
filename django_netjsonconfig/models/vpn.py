import collections

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from django_x509.models import Cert

from ..base import TimeStampedEditableModel
from ..settings import DEFAULT_VPN_BACKENDS


@python_2_unicode_compatible
class AbstractVpn(TimeStampedEditableModel):
    """
    Abstract VPN model
    """
    name = models.CharField(max_length=64)
    notes = models.TextField(blank=True)
    ca = models.ForeignKey('django_x509.Ca', verbose_name=_('CA'))
    cert = models.ForeignKey('django_x509.Cert',
                             verbose_name=_('x509 Certificate'),
                             blank=True,
                             null=True)
    backend = models.CharField(_('VPN backend'),
                               choices=DEFAULT_VPN_BACKENDS,
                               max_length=128,
                               help_text=_('Select VPN configuration backend'))
    server_config = JSONField(_('server configuration'),
                              blank=True,
                              default=dict,
                              help_text=_('configuration in NetJSON DeviceConfiguration format'),
                              load_kwargs={'object_pairs_hook': collections.OrderedDict},
                              dump_kwargs={'indent': 4})
    client_config = JSONField(_('client configuration'),
                              blank=True,
                              default=dict,
                              help_text=_('configuration in NetJSON DeviceConfiguration format'),
                              load_kwargs={'object_pairs_hook': collections.OrderedDict},
                              dump_kwargs={'indent': 4})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Calls _auto_create_cert() if cert is not set
        """
        if not self.cert:
            self.cert = self._auto_create_cert()
        super(AbstractVpn, self).save(*args, **kwargs)

    def _auto_create_cert(self):
        """
        Automatically generates server x509 certificate
        """
        common_name = slugify(self.name)
        server_extensions = [
            {
                "name": "nsCertType",
                "value": "server",
                "critical": False
            }
        ]
        cert = Cert(name=self.name,
                    ca=self.ca,
                    key_length=self.ca.key_length,
                    digest=self.ca.digest,
                    country_code=self.ca.country_code,
                    state=self.ca.state,
                    city=self.ca.city,
                    organization=self.ca.organization,
                    email=self.ca.email,
                    common_name=common_name,
                    extensions=server_extensions)
        cert.save()
        return cert

    class Meta:
        abstract = True


class Vpn(AbstractVpn):
    """
    Abstract VPN model
    """
    class Meta:
        verbose_name = _('VPN')
        verbose_name_plural = _('VPN')