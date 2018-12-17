import json
import os
import xml.etree.ElementTree as ET

from django.http import HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from junction.core.models import License
from junction.core.utils import Elite3eServices
from junction.loaders.forms import LoaderForm, AttributeForm, HistoryForm, LoaderXOQLForm
from junction.loaders.models import Loader, Attribute, LoaderXOQL, History


def build_credentials(server=None):
    credentials = {'domain': None,
                    'username': None,
                    'password': None,}
    if all([server.domain,
            server.username,
            server.password]):
        credentials.update({'domain': server.domain,
                            'username': server.username,
                            'password': server.password, })
    return credentials

def history_raw(request, loader_slug=None, pk=None):
    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)
    history = get_object_or_404(History, loader__slug=loader_slug, pk=pk)
    context = {'main_content_card_title': 'Loaders',
               'main_content_card_subtitle': 'History Item',
               'main_content_card_footer': '',
               'active_side_bar': 'loaders',
               'history': history,
               }
    return render(request, 'loaders/history_raw.html', context)


def loader_list(request):
    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    loaders = Loader.objects.filter(active=True)
    context = {'main_content_card_title': 'Loaders',
               'main_content_card_subtitle': 'A list of available loaders. Add a new loader by touching the button to the right, or pick one of the available loaders to configure or run.',
               'main_content_card_footer': '',
               'active_side_bar': 'loaders',
               'loaders': loaders,
               }
    return render(request, 'loaders/list.html', context)


def loader_edit(request, loader_slug=None, attribute_slug=None, loaderxoql_slug=None, active_tab=None):
    """ Handles initial create and subsequent updates to loader and attributes. Bit of a
    non traditional way to handle two different sets of crud, but in lieu of dealing with
    the ajax calls we'd normally use we're doing it this way. """

    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    # raise ValueError(active_tab)
    if not active_tab:
        active_tab = 'Run'

    if loader_slug:
        loader = get_object_or_404(Loader, slug=loader_slug, active=True)
        form_action = reverse('loaders:loader_edit',
                              kwargs={'loader_slug': loader_slug, })
        if attribute_slug:
            attribute = get_object_or_404(Attribute, loader=loader, slug=attribute_slug, active=True)
            active_tab = "Attributes"
            attribute_form_action = reverse('loaders:attribute_edit',
                                            kwargs={'loader_slug': loader_slug,
                                                    'attribute_slug': attribute_slug,})
        else:
            attribute = Attribute()
            attribute.loader = loader
            # suggest the next sort number
            try:
                current_max_sort = Attribute.objects.filter(loader=loader, active=True).exclude(
                    sort__isnull=True).latest('sort').sort
            except Attribute.DoesNotExist:
                current_max_sort = 0

            attribute.sort = current_max_sort + 1
            attribute_form_action = reverse('loaders:loader_edit',
                                            kwargs={'loader_slug': loader_slug, })

        if loaderxoql_slug:
            loaderxoql = get_object_or_404(LoaderXOQL, loader=loader, slug=loaderxoql_slug)
            active_tab = "Advanced"
            loaderxoql_form_action = reverse('loaders:loaderxoql_edit',
                                            kwargs={'loader_slug': loader_slug,
                                                    'loaderxoql_slug': loaderxoql_slug,})
        else:
            loaderxoql = LoaderXOQL()
            loaderxoql.loader = loader
            loaderxoql_form_action = reverse('loaders:loader_edit',
                                             kwargs={'loader_slug': loader_slug, })

        context = {'main_content_card_title': loader.name,
                   'main_content_card_subtitle': loader.description,
                   'current_loader': loader,
                   }
    else:
        loader = Loader()
        attribute = Attribute()
        loaderxoql = LoaderXOQL()
        active_tab = "Configure"
        form_action = reverse('loaders:loader_edit')
        attribute_form_action = reverse('loaders:loader_edit')
        loaderxoql_form_action = reverse('loaders:loader_edit')

        context = {'main_content_card_title': 'Create New Loader',
                   'main_content_card_subtitle': 'Enter the information below and touch Add to create this new loader. After creation, you will be able to select the fields to include.',
                   'current_loader': None,
                   }

    # todo need to check the appropriate request.POST sets (loader or attribute)
    # handle form submissions
    if 'btn-loader-submit' in request.POST or \
       'btn-archive' in request.POST or \
       'btn-cancel' in request.POST:

        if 'btn-cancel' in request.POST:
            redirect_url = reverse('loaders:loader_list')
            return redirect(redirect_url)

        loader_form = LoaderForm(request.POST or None, instance=loader)
        if loader_form.is_valid():

            loader = loader_form.save(commit=False)

            if 'btn-archive' in request.POST:
                loader.active = False
            loader.save()

            redirect_url = reverse('loaders:loader_list')
            return redirect(redirect_url)
    else:
        loader_form = LoaderForm(None, instance=loader)

    # this should probably be in the else above, but we get into a mess with the blank forms.
    if 'btn-attribute-submit' in request.POST or \
       'btn-attribute-remove' in request.POST or \
       'btn-attribute-cancel' in request.POST:

        if 'btn-attribute-cancel' in request.POST:
            redirect_url = reverse('loaders:loader_attribute_active', kwargs={'loader_slug': loader.slug, })
            return redirect(redirect_url)

        attribute_form = AttributeForm(request.POST or None, instance=attribute, loader=loader)

        if attribute_form.is_valid():
            attribute = attribute_form.save(commit=False)

            if 'btn-attribute-remove' in request.POST:
                attribute.delete()
                redirect_url = reverse('loaders:loader_attribute_active', kwargs={'loader_slug': loader.slug, })
                return redirect(redirect_url)

            attribute.loader = loader
            attribute.save()
            # redirect to editing this loader
            redirect_url = reverse('loaders:loader_attribute_active', kwargs={'loader_slug': loader_slug, })
            return redirect(redirect_url)
    else:
        attribute_form = AttributeForm(None, instance=attribute)

    # handle the advanced tab
    if 'btn-loaderxoql-submit' in request.POST or \
       'btn-loaderxoql-remove' in request.POST or \
       'btn-loaderxoql-cancel' in request.POST:

        if 'btn-loaderxoql-cancel' in request.POST:
            redirect_url = reverse('loaders:loader_advanced_active', kwargs={'loader_slug': loader.slug, })
            return redirect(redirect_url)

        loaderxoql_form = LoaderXOQLForm(request.POST or None, instance=loaderxoql, loader=loader)

        if loaderxoql_form.is_valid():
            loaderxoql = loaderxoql_form.save(commit=False)

            if 'btn-loaderxoql-remove' in request.POST:
                loaderxoql.delete()
                redirect_url = reverse('loaders:loader_advanced_active', kwargs={'loader_slug': loader.slug, })
                return redirect(redirect_url)
            loaderxoql.loader = loader
            loaderxoql.save()
            redirect_url = reverse('loaders:loader_advanced_active', kwargs={'loader_slug': loader_slug, })
            return redirect(redirect_url)
    else:
        loaderxoql_form = LoaderXOQLForm(None, instance=loaderxoql  )
    # get the full list of loaders. Remember the templates lazy load these by default
    # We'll get the attributes list through the template .all feature for a current_loader
    # which is placed in the context way up at the beginning of this view.
    loaders = Loader.objects.filter(active=True)
    context.update({
               'main_content_card_footer': '',
               'active_side_bar': 'loaders',
               'form_action': form_action,
               'selected_loader': loader.pk,
               'current_attribute': attribute,
               'current_loaderxoql': loaderxoql,
               'loaders': loaders,
               'loader_form': loader_form,
               'history_form': HistoryForm(loader=loader),
               'attribute_form': attribute_form,
               'attribute_form_action': attribute_form_action,
               'loaderxoql_form': loaderxoql_form,
               'loaderxqol_form_action': loaderxoql_form_action,
               'active_tab': active_tab,
               })
    return render(request, 'loaders/edit.html', context)


def run_xoql(request, loader_slug=None):
    """ Attempts to run a report query and return the results as a json object ready
    to be put into the Handsontable.
    """
    data = []
    if request.method == "POST":
        loader = get_object_or_404(Loader, slug=loader_slug)
        # xoql = get_object_or_404(LoaderXOQL, id=request.POST.get('xoql', None))
        # posted_vars = request.POST.copy()
        # posted_vars.update({'loader': loader, })
        # request.POST = posted_vars
        history_form = HistoryForm(request.POST, loader=loader)
        if history_form.is_valid():
            # some housekeeping in advance, get the loader attributes
            loader_attributes = Attribute.objects.filter(loader=loader).values('name')
            # go get the data
            server = history_form.cleaned_data['server']
            credentials = build_credentials(server)
            with Elite3eServices(wapi=server.wapi,
                                 protocol=server.protocol,
                                 instance=server.instance,
                                 **credentials) as e3:
                try:
                    loaderxoql = LoaderXOQL.objects.get(pk=history_form.cleaned_data['xoql'])
                except ValueError:
                    data = ['No xoql specified',]
                    return JsonResponse({'errors': data})
                results = e3.get_archetype_data(select_xml=loaderxoql.xoql)
                # so now we have something like:
                # <Data>
                #  <ParentObject>
                #   <Attribute>Value</Attribute>
                #   <Attribute1>Value</Attribute1>
                #  </ParentObject>
                # </Data>
                root = ET.fromstring(results)
                for parent_object in root:
                    if parent_object.tag == loader.parent_object:
                        row_data = []
                        for attribute in parent_object:
                            if loader_attributes.filter(name=attribute.tag).exists():
                                row_data.append(attribute.text)
                        data.append(row_data)
        else:
            data = [f"Form is missing information {history_form.errors}", ]
            return JsonResponse({'errors': data})
    return JsonResponse({'data': data})


def loader_run(request, loader_slug=None):
    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    if loader_slug:
        loader = get_object_or_404(Loader, slug=loader_slug, active=True)
    else:
        return HttpResponseBadRequest(content="No loader specified.")

    if request.method == "POST":
        history_form = HistoryForm(request.POST, loader=loader)
    else:
        history_form = HistoryForm(loader=loader)
    if history_form.is_valid():
        history = history_form.save(commit=False)
        history.loader = loader

        # take the hf.data and convert to process_xml
        parent_action_af = ''   # set the alias field string to blank
        if loader.parent_action != loader.ADD:
            # get the attribute with the key field with parent type
            parent_action_key = Attribute.objects.filter(loader=loader, active=True, is_key=True, type=Attribute.PARENT)
            if parent_action_key:
                # so we have at least one key, we'll take the first one
                if parent_action_key[0].alias_field:
                    parent_action_af = f" AliasField='{parent_action_key[0].alias_field}' "

        # get the column names into a dictionary with their position as the value for easy look up later
        columns = dict()
        ch = history.column_headers

        for idx, c in enumerate(ch.split(',')):
            columns[c] = idx

        child_attributes = Attribute.objects.filter(loader=loader, active=True, type=Attribute.CHILD)
        parent_attributes = Attribute.objects.filter(loader=loader, active=True, type=Attribute.PARENT, is_key=False)

        process_xml = list()
        process_xml.append(f'<{loader.process} xmlns="http://elite.com/schemas/transaction/process/write/{loader.process}">')
        process_xml.append(f'<Initialize xmlns="http://elite.com/schemas/transaction/object/write/{loader.parent_object}">')

        # f'{parent_action_node}'
        # now loop through the data
        # if there is a key field, we need to know which position of the data line it is in and
        # we'll have the column headers, so find the position in that list of the key string
        # put its value in here

        # convert json serialized to python object
        table = json.loads(history.data)
        for row in table['data']:
            # only look at rows with data in at least one element
            row_contains_data = False
            for cell in row:
                if not row_contains_data:
                    if type(cell) == str:
                        if not cell.strip() == '':
                            row_contains_data = True
            # the row.count(None) doesn't work for the empty string.
            # if row.count(None) != len(row):
            if row_contains_data:
                process_xml.append(f'<{loader.parent_action}>')

                if loader.parent_action == Loader.ADD:
                    process_xml.append(f"<{loader.parent_object}{parent_action_af} >")
                else:
                    process_xml.append(f"<{loader.parent_object}{parent_action_af} KeyValue='{row[columns[parent_action_key[0].name]]}'>")
                # todo handle parent level attributes here
                if parent_attributes.exists():    # if there are parent attributes:
                    process_xml.append("<Attributes>")
                    for parent_attribute in parent_attributes:
                        if row[columns[parent_attribute.name]]:
                            if parent_attribute.alias_field:
                                af = f" AliasField='{parent_attribute.alias_field}'"
                            else:
                                af = ''

                            process_xml.append(f"<{parent_attribute.name} {af}>{row[columns[parent_attribute.name]]}</{parent_attribute.name}>")
                        else:
                            # undecided if we want a self closing tag, or omit it completely
                            pass
                    process_xml.append("</Attributes>")

                if child_attributes.exists():    # if there are children:
                    process_xml.append("<Children>")
                    process_xml.append(f"<{loader.child_object}><{loader.child_action}><{loader.child_object}><Attributes>")
                    # then for each child type of attribute -
                    # hopefully by now we have a dictionary of the fields and positions as values
                    for child_attribute in child_attributes:
                        if row[columns[child_attribute.name]]:
                            process_xml.append(f"<{child_attribute.name}>{row[columns[child_attribute.name]]}</{child_attribute.name}>")
                        else:
                            # undecided if we want a self closing tag, or omit it completely
                            pass
                            # process_xml.append(f"<{child_attribute.name}/>")
                    process_xml.append(f"</Attributes></{loader.child_object}></{loader.child_action}></{loader.child_object}>")
                    process_xml.append("</Children>")

                process_xml.append(f'</{loader.parent_object}>')
                process_xml.append(f'</{loader.parent_action}>')
        process_xml.append(f'</Initialize></{loader.process}>')

        history.process_xml = '\n'.join(process_xml)

        # call the Elite execute process (using Zeep)
        # this should call with the current user, without need for transport
        credentials = build_credentials(history.server)
        try:
            with Elite3eServices(wapi=history.server.wapi,
                                 protocol=history.server.protocol,
                                 instance=history.server.instance,
                                 **credentials
                                 ) as e3:
                # record the response from Elite in history.response
                history.response = e3.execute_process(process_xml=history.process_xml)
        except ConnectionRefusedError:
            return HttpResponseServerError()
        history.save()

    # todo: redirect to the loader with the history tab active
    redirect_url = reverse('loaders:loader_edit', kwargs={'loader_slug': loader.slug, })
    return redirect(redirect_url)
