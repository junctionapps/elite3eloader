from django.db import models
from django.utils.text import slugify


class Server(models.Model):
    HTTP = 'http'
    HTTPS = 'https'

    PROTOCOL_CHOICES = (
        (HTTP, 'http'),
        (HTTPS, 'https')
    )
    name = models.CharField(max_length=256, help_text="Common name for the server", unique=True)
    protocol = models.CharField(max_length=64, help_text="The protocol in use for this server", choices=PROTOCOL_CHOICES, default=HTTP)
    wapi = models.CharField(max_length=64, verbose_name="WAPI", help_text="The wapi or load balancer to use")
    instance = models.CharField(max_length=64, help_text="DB Instance 'TE_3E_UAT' as example")
    custom_wsdl = models.CharField(max_length=512, verbose_name="Custom WSDL", help_text="Full path to the wsdl if not in the typical location", blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Uncheck to remove this server from active listing")
    domain = models.CharField(verbose_name="User Domain", max_length=255, blank=True, null=True, help_text="Optional. If set will override current user credentials (must be set with user/pass fields")
    username = models.CharField(verbose_name="User Name", max_length=255, blank=True, null=True, help_text="Optional. If set will override current user credentials (must be set with domain/pass fields")
    password = models.CharField(verbose_name="User Password",max_length=255, blank=True, null=True, help_text="Optional. If set will override current user credentials (must be set with domain/user fields")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.name}"

    def credentials(self):
        if all([self.username, self.password, self.domain]):
            return f"{self.domain}/{self.username}"
        else:
            return "Current User"

    @property
    def has_custom_wsdl(self):
        return True if self.custom_wsdl else False

    @property
    def url(self):
        """ The typical path to the Transaction Services """
        # http://elt11a/te_3e_uat9/WebUI/Transactionservice.asmx
        return f'{self.protocol}://{self.wapi}/{self.instance}/WebUI/Transactionservice.asmx'

    @property
    def wsdl(self):
        """ Use the custom wsdl if is it provided, otherwise look to the standard location """
        if self.custom_wsdl:
            return self.custom_wsdl
        else:
            return f'{self.url}?wsdl'

    def save(self, *args, **kwargs):
        # create a unique slug for this server
        # if not self.slug:
        suffix = 0
        potential = base = slugify(f'{self.name}-{self.wapi}-{self.instance}')
        self.slug = None
        while not self.slug:
            if suffix:
                potential = f'{base}-{suffix}'
            if not Server.objects.filter(slug=potential).exists():
                self.slug = potential
            suffix += 1

        super(Server, self).save(*args, **kwargs)