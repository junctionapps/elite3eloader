from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from junction.core.models import License
from junction.servers.forms import ServerForm
from junction.servers.models import Server


def list(request, server_slug=None):

    license_check = License.objects.all().exists()
    if not license_check:
        redirect_url = reverse('license')
        return redirect(redirect_url)

    if server_slug:
        server = get_object_or_404(Server, slug=server_slug, active=True)
        form_action = reverse('servers:server_edit',
                              kwargs={'server_slug': server.slug, })
    else:
        server = Server()
        form_action = reverse('servers:server_list')

    server_form = ServerForm(request.POST or None, instance=server)

    if request.POST and server_form.is_valid():

        if 'btn-cancel' in request.POST:
            redirect_url = reverse('servers:server_list')
            return redirect(redirect_url)

        server = server_form.save(commit=False)

        if 'btn-archive' in request.POST:
            server.active = False
        server.save()

        redirect_url = reverse('servers:server_list')
        return redirect(redirect_url)

    servers = Server.objects.filter(active=True)
    context = {'main_content_card_title': 'Servers',
               'main_content_card_subtitle': 'Add, edit or remove servers to have available for loading data',
               'main_content_card_footer': '',
               'active_side_bar': 'servers',
               'form_action': form_action,
               'selected_server': server.pk,
               'servers': servers,
               'server_form': server_form,
               }
    return render(request, 'servers/list.html', context)
