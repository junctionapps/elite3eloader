import os
import sys

from django.shortcuts import render
from django.core import management
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.urls import reverse

from junction.core.forms import UploadRestoreForm, LicenseForm
from junction.core.models import License


def index(request):

    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    context = {'active_side_bar': 'dashboard',
               'main_content_card_title': 'Welcome',
               'main_content_card_subtitle': 'Work in Progress - Beta Software',
               'main_content_card_footer': '', }

    return render(request, 'core/dashboard.html', context)


def junction_license(request):
    """ Shows the initial license form, and shows license without
    the form if it has already been agreed to.
    """
    if request.method == 'POST':
        license_form = LicenseForm(request.POST)
        if license_form.is_valid():
            license_form.save()
            redirect_url = reverse('index')
            return redirect(redirect_url)

    # check if the license has been agreed to
    license_check = License.objects.all().exists()

    if license_check:
        show_license_form = False
    else:
        show_license_form = True

    context = {'active_side_bar': 'license',
               'main_content_card_title': 'License',
               'main_content_card_subtitle': 'MIT License',
               'main_content_card_footer': '',
               'show_license_form': show_license_form, }

    return render(request, 'core/license.html', context)


def backup(request):
    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    error_text = False
    if request.method == 'POST':
        restore_form = UploadRestoreForm(request.POST, request.FILES)
        if restore_form.is_valid():
            f = request.FILES['restorefile']
            fs = FileSystemStorage()
            saved_as = fs.save(f.name, f)
            try:
                management.call_command('loaddata', os.path.join(fs.location, saved_as), verbosity=0)
            except management.CommandError:
                error_text = ["There was an issue restoring from that file.",
                              "The restore has failed. Verify the file is valid and try again."]
            else:
                redirect_url = reverse('loaders:loader_list')

            try:
                os.remove(os.path.join(fs.location, saved_as))
            except OSError:
                pass
            if not error_text:
                return redirect(redirect_url)
    else:
        restore_form = UploadRestoreForm()

    context = {'active_side_bar': 'backup',
               'main_content_card_title': 'Backup/Restore',
               'main_content_card_subtitle': 'Create a backup prior to update, and restore after an update',
               'main_content_card_footer': '',
               'restore_form': restore_form,
               'error_text': error_text,
               }

    return render(request, 'core/backup-restore.html', context)


def backup_create(request):
    """ Saves a copy of the server, loader, attribute and history models, saves to a file
    and should prompt user to save it somewhere. """

    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    sysout = sys.stdout
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=backup.json'
    sys.stdout = response
    management.call_command('dumpdata', 'core', 'loaders', 'servers')
    sys.stdout = sysout
    return response

