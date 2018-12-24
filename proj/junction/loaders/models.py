import json
from django.db import models
from django.utils.text import slugify

from junction.servers.models import Server
import xml.etree.ElementTree as ET


class Loader(models.Model):

    ADD = 'Add'
    EDIT = 'Edit'
    ACTION_CHOICES = (
        (ADD, 'Add'),
        (EDIT, 'Edit'),
    )
    """ The list of available loaders. """
    name = models.CharField(max_length=64, unique=True, help_text='Common name for this loader')
    description = models.TextField(blank=True, null=True, help_text="Description of this loader's purpose")
    active = models.BooleanField(default=True)
    parent_action = models.CharField(max_length=64, choices=ACTION_CHOICES, default=EDIT, help_text="The type of action this loader performs")
    parent_object = models.CharField(max_length=256, help_text="The primary object we are action upon")

    child_action = models.CharField(max_length=64, null=True, blank=True, choices=ACTION_CHOICES, default=ADD, help_text="If applicable, the child action to be performed")
    child_object = models.CharField(max_length=256, null=True, blank=True, help_text="If applicable, the child object we are acting upon")

    last_run = models.DateTimeField(blank=True, null=True)
    process = models.CharField(max_length=256, help_text='The 3E process which this loader will call')

    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # create a unique slug for this record
        suffix = 0
        potential = base = slugify(f'{self.name[:50]}')
        self.slug = None
        while not self.slug:
            if suffix:
                potential = f'{base}-{suffix}'
            if not Loader.objects.filter(slug=potential).exists():
                self.slug = potential
            suffix += 1

        super(Loader, self).save(*args, **kwargs)


class LoaderXOQL(models.Model):
    """
    An optional advanced listing of xoql to initially fill the data table with data.
    Originally used in testing, but thought to be useful in a variety of use cases.
    It is suggested to use Thomson's OQL Analyser to write the code, compile and modify the
    the resulting xoql accordingly. Fields that correspond to fields in the datatable will
    be filled in with data from 3E. Keep in mind that the results can repeating nodes with
    the same name; the responsibility lies with you to ensure uniqueness. Use the Alias attribute
    to name to match the Attributes in the Loader setup.

    In the value nodes, use the Alias attribute in the LEAF node.
    <VALUE>
      <LEAF QueryID="Description" Alias="TkprDate__Title1__Description">
        <NODE NodeID="Title1" />
      </LEAF>
    </VALUE>
    """
    loader = models.ForeignKey(Loader, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, help_text="A name for this xoql")
    description = models.TextField(blank=True, null=True, help_text="A brief description for this loader")
    xoql = models.TextField(blank=True, null=True, help_text="The xoql to populate the data table on Run tab",
                            verbose_name="XOQL")
    slug = models.SlugField()

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # create a unique slug for this record
        suffix = 0
        potential = base = slugify(f'{self.name[:50]}')
        self.slug = None
        while not self.slug:
            if suffix:
                potential = f'{base}-{suffix}'
            if not LoaderXOQL.objects.filter(slug=potential).exists():
                self.slug = potential
            suffix += 1

        super(LoaderXOQL, self).save(*args, **kwargs)


class Attribute(models.Model):
    """ The attributes on a particular load. """
    CHILD = 'Child'
    PARENT = 'Parent'
    TYPE_CHOICES = (
        (CHILD, CHILD),
        (PARENT, PARENT),
    )

    DISPLAY_ONLY = 'Display'
    LOADER_XML = 'Export'
    INCLUDE_CHOICES = ((DISPLAY_ONLY, 'Show in Display only'),
                       (LOADER_XML, 'Display and include in Loader XML'),)
    loader = models.ForeignKey(Loader, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, help_text='The name of the attribute (case sensitive)')
    type = models.CharField(max_length=64, help_text='Does this belong to the parent object or the child?', default=CHILD, choices=TYPE_CHOICES)
    sort = models.IntegerField(default=1, help_text='Numerical value to control the order of the fields')
    is_key = models.BooleanField(default=False, help_text='Select for a key field')
    include_type = models.CharField(default=LOADER_XML, max_length=64, choices=INCLUDE_CHOICES, help_text='Controls if this is a display only field, or included in the loader.')
    alias_field = models.CharField(max_length=256, blank=True, null=True, help_text='If provided, will be used as the AliasField')
    slug = models.SlugField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.loader.name} - {self.name}'

    def save(self, *args, **kwargs):
        # create a unique slug for this record on each save - simply for url friendliness
        # keep in mind that the slug is unique but can change on save
        suffix = 0
        potential = base = slugify(f'{self.name[:40]}')
        self.slug = None
        while not self.slug:
            if suffix:
                potential = f'{base}-{suffix}'
            if not Loader.objects.filter(slug=potential).exists():
                self.slug = potential
            suffix += 1

        super(Attribute, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('name', 'loader')
        ordering = ('sort', 'name')


class AvailableAttribute(models.Model):
    """ A list of available object attributes """
    name = models.CharField(max_length=64, help_text='The field or attribute id from the object')
    alias_field = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class History(models.Model):
    loader = models.ForeignKey(Loader, on_delete=models.PROTECT, help_text="Select a server to push the data")
    column_headers = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    server = models.ForeignKey(Server, on_delete=models.PROTECT)
    process_xml = models.TextField(blank=True, null=True)
    submitted = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.loader.name} - {self.submitted}"

    def number_of_records(self):
        return len(json.loads(self.data)['data'])

    def elite_attributes(self):
        # {'Process': '', 'Result': '', 'StepId': '', 'Records': '', 'User': '', 'Name': '', 'ProcessItemId': ''}
        # {'Result': "Failure", Message:"Error attempting to read data."}
        return ET.fromstring(self.response).attrib

    def elite_attribute(self, attribute):
        try:
            return self.elite_attributes()[attribute]
        except KeyError:
            return None

    def elite_process(self):
        return self.elite_attribute("Process")

    def elite_results(self):
        return self.elite_attribute("Result")

    def elite_records(self):
        return self.elite_attribute("Records")

    def elite_message(self):
        return self.elite_attribute("Message")

    def elite_data_errors(self):
        root = ET.fromstring(self.response)
        return '\n'.join([e.text for e in root.iter('E')])

    @staticmethod
    def beautify(ugly):
        from lxml import etree
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(ugly, parser)
        pretty = etree.tostring(tree, pretty_print=True,
                                xml_declaration=False,
                                encoding='unicode')
        return f"{str(pretty)}"

    def response_pretty(self):
        return self.beautify(self.response)

    def process_xml_pretty(self):
        return self.beautify(self.process_xml)

    def data_pretty(self):
        return json.dumps(self.data, sort_keys=False, indent=2)

    class Meta:
        ordering = ['-submitted',]
