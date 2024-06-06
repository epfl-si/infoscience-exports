from urllib.parse import unquote

from django.conf import settings
from django.urls import reverse_lazy as django_reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import gettext as _, get_language
from django.core.cache import cache

from exports import format_version
from log_utils import LogMixin
from .models import Export
from .forms import ExportForm
from .options_notices import get_notices


class IsTheUserAccessTest(UserPassesTestMixin):
    # only allow the creator of the object or the staff to access the view
    # trigger the self.get_object()
    raise_exception = True

    def test_func(self):
        # this object's load happens before the view is shown, so we have
        # to cancel other getters
        object = self.get_object()
        return object.user == self.request.user or self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        # overload only to remove self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # overload only to remove self.get_object()
        return super().post(request, *args, **kwargs)


class ExportList(LoginRequiredMixin, LogMixin, ListView):
    model = Export
    paginate_by = 20

    def get(self, *args, **kwargs):
        to_return = super(ExportList, self).get(*args, **kwargs)
        return to_return

    def get_queryset(self):
        return Export.objects.filter(user=self.request.user)


class ExportCreate(LoginRequiredMixin, CreateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')

    def get(self, request, *args, **kwargs):
        # url in parameter is a form initial
        if request.GET.get('url'):
            self.initial.update({
                'url': unquote(request.GET['url']).replace(" ", "+")
            })

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ExportCreate, self).form_valid(form)


class ExportUpdate(LoginRequiredMixin, IsTheUserAccessTest, UpdateView):
    model = Export
    form_class = ExportForm
    success_url = django_reverse_lazy('crud:export-list')

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can edit the publication"))
            return super(ExportUpdate, self).form_invalid(form)

        return super(ExportUpdate, self).form_valid(form)


class ExportDelete(IsTheUserAccessTest, LoginRequiredMixin, DeleteView):
    model = Export
    success_url = django_reverse_lazy('crud:export-list')

    def form_valid(self, form):
        if form.instance.user != self.request.user and not self.request.user.is_staff:
            form.add_error(None, _("Only the creator can delete the publication"))
            return super(ExportDelete, self).form_invalid(form)

        return super(ExportDelete, self).form_valid(form)


class ExportView(DetailView):
    model = Export
    template_name_suffix = ''

    def get(self, request, *args, **kwargs):
        """ Warning, as we cache the view, don't use any request data"""
        self.object = self.get_object()
        # language dependant cache
        ln = get_language()
        cache_key = self.object.get_cache_key_for_view(ln)

        if cache_key in cache:
            # do we have the result in the cache?
            rendered_response = cache.get(cache_key)
        else:
            context = self.get_context_data(object=self.object)
            rendered_response = self.render_to_response(context).render()

            # save render in two caches, the temp one from Django here
            cache.set(cache_key, rendered_response)

        # the other one into the 'export.last_rendered_page' model, to get it back when things go blackout
        # this field is reserved for invenio exports only, dspace does not need this mechanism
        if self.object.server_engine == 'invenio':
            self.object.last_rendered_page = rendered_response.rendered_content
            self.object.save()
            # TODO: render it back when appropriate (when env.SERVER_ENGINE == 'dspace' maybe) with
            # self.object.last_rendered_page = django.utils.timezone.now()
            # self.object.save()
            # return HttpResponse(self.object.last_rendered_page)

        return rendered_response

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        options = {}
        options['is_extern'] = True
        options['url'] = self.object.url
        options['format'] = self.object.formats_type
        options['bullet'] = self.object.bullets_type
        options['thumb'] = self.object.show_thumbnail
        options['summary'] = self.object.show_summary
        options['link_authors'] = self.object.show_linkable_authors
        options['link_print'] = self.object.show_links_for_printing
        options['link_detailed'] = self.object.show_detailed
        options['link_fulltext'] = self.object.show_fulltext
        options['link_publisher'] = self.object.show_viewpublisher
        options['groupsby_all'] = self.object.groupsby_type
        options['groupsby_year'] = self.object.groupsby_year
        options['groupsby_doc'] = self.object.groupsby_doc
        options['pending_publications'] = self.object.show_pending_publications
        options['adv_article_volume'] = self.object.show_article_volume
        options['adv_article_volume_number'] = self.object.show_article_volume_number
        options['adv_article_volume_pages'] = self.object.show_article_volume_pages
        options['adv_thesis_directors'] = self.object.show_thesis_directors
        options['adv_thesis_pages'] = self.object.show_thesis_pages
        options['adv_report_working_papers_pages'] = self.object.show_report_working_papers_pages
        options['adv_conf_proceed_place'] = self.object.show_conf_proceed_place
        options['adv_conf_proceed_date'] = self.object.show_conf_proceed_date
        options['adv_conf_paper_journal_name'] = self.object.show_conf_paper_journal_name
        options['adv_book_isbn'] = self.object.show_book_isbn
        options['adv_book_doi'] = self.object.show_book_doi
        options['adv_book_chapter_isbn'] = self.object.show_book_chapter_isbn
        options['adv_book_chapter_doi'] = self.object.show_book_chapter_doi
        options['adv_patent_status'] = self.object.show_patent_status

        options = get_notices(options)
        context['options'] = options
        return context


def preview(request):
    params = request.GET.dict()

    options = {}
    options['is_extern'] = False
    options['url'] = params['url']
    options['format'] = params['format']
    options['bullet'] = params['bullet']
    options['thumb'] = params['thumb'] == 'true'
    options['summary'] = params['summary'] == 'true'
    options['link_authors'] = params['link_authors'] == 'true'
    options['link_print'] = params['link_print'] == 'true'
    options['link_detailed'] = params['link_detailed'] == 'true'
    options['link_fulltext'] = params['link_fulltext'] == 'true'
    options['link_publisher'] = params['link_publisher'] == 'true'
    options['groupsby_all'] = params['groupsby_all']
    options['groupsby_year'] = params['groupsby_year']
    options['groupsby_doc'] = params['groupsby_doc']
    options['pending_publications'] = params['pending_publications'] == 'true'
    options['adv_article_volume'] = params['adv_article_volume'] == 'true'
    options['adv_article_volume_number'] = params['adv_article_volume_number'] == 'true'
    options['adv_article_volume_pages'] = params['adv_article_volume_pages'] == 'true'
    options['adv_thesis_directors'] = params['adv_thesis_directors'] == 'true'
    options['adv_thesis_pages'] = params['adv_thesis_pages'] == 'true'
    options['adv_report_working_papers_pages'] = params['adv_report_working_papers_pages'] == 'true'
    options['adv_conf_proceed_place'] = params['adv_conf_proceed_place'] == 'true'
    options['adv_conf_proceed_date'] = params['adv_conf_proceed_date'] == 'true'
    options['adv_conf_paper_journal_name'] = params['adv_conf_paper_journal_name'] == 'true'
    options['adv_book_isbn'] = params['adv_book_isbn'] == 'true'
    options['adv_book_doi'] = params['adv_book_doi'] == 'true'
    options['adv_book_chapter_isbn'] = params['adv_book_chapter_isbn'] == 'true'
    options['adv_book_chapter_doi'] = params['adv_book_chapter_doi'] == 'true'
    options['adv_patent_status'] = params['adv_patent_status'] == 'true'

    options = get_notices(options)
    c = {'options': options, 'SITE_PATH': settings.SITE_PATH}

    t = loader.get_template('exports/export_complete.html')
    return HttpResponse(t.render(c))


def version(request, label='version'):
    return HttpResponse(format_version(label))
