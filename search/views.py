from collections import OrderedDict
from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from functools import reduce
from itertools import chain

import json
import operator

from .utils import filter_list, query_list, state_list
from campaign.models import Campaign
from page.models import Page


def search(request):
    if request.method == "POST":
        query_from_search = request.POST.get('q')
    else:
        query_from_search = None
    categories = OrderedDict(Page._meta.get_field('category').choices)
    states = OrderedDict(Page._meta.get_field('state').choices)

    return render(request, 'search/search.html', {
        'categories': categories,
        'states': states,
        'query_from_search': query_from_search,
    })

def create_search_result_html(r, sponsored, trending):
    html = (
        "<div class='row mb-4'>"
        "<div class='col-md-auto search-result-picture-container'>"
    )

    if r.profile_picture():
        src = r.profile_picture().image.url
    else:
        src = "/static/img/campaign_default.svg"

    if isinstance(r, Page):
        html += "<img class='search-result-picture-page' src='{}' />".format(src)
    elif isinstance(r, Campaign):
        html += "<img class='search-result-picture-campaign' src='{}' />".format(src)

    html += (
        "</div>"
        "<div class='col-md-10 mb-4'>"
        "<div class='row justify-content-between'>"
        "<div class='col-md-auto'>"
    )

    if isinstance(r, Page):
        html += "<h3><a class='purple' href='/{}/'>{}</a></h3>".format(r.page_slug, r.name)
    elif isinstance(r, Campaign):
        html += "<h3><a class='teal' href='/{}/{}/{}/'>{}</a></h3>".format(r.page.page_slug, r.pk, r.campaign_slug, r.name)

    html += (
        "</div>"
        "<div class='col d-flex align-items-center h100'>"
    )

    if sponsored == True:
        html += "<span class='badge badge-success mr-4'>Sponsored</span>"

    if trending == True:
        html += "<span class='badge badge-primary mr-4'>Trending</span>"

    html += (
        "<span class='small'>"
        "<i class='fal fa-compass mr-2'></i>"
    )

    if r.city:
        html += "{}, {}".format(r.city, r.state)
    elif r.state:
        html += r.get_state_display()

    html += (
        "</span>"
        "</div>"
        "<div class='col-md-3 vote-amount'>"
    )

    if isinstance(r, Page):
        html += "<span class='purple font-weight-bold font-size-175'>${}</span>".format(int(r.donation_money() / 100))
    elif isinstance(r, Campaign):
        html += "<span class='teal font-weight-bold font-size-175'>${}</span>".format(int(r.donation_money() / 100))

    html += (
        "</div>"
        "</div>"
        "<span class='comment-content'><p>{}</p></span>"
        "</div>"
        "</div>"
    ).format(r.search_description())

    return html

def results(request):
    if request.method == "POST":
        q = request.POST.get('q')
        f = request.POST.get('f')
        s = request.POST.get('s')
        a = request.POST.get('a')

        if a == "false":
            if f:
                f = f.replace('"', '')
                f = f.replace('[', '')
                f = f.replace(']', '')

            if q == "0":
                q = False
            elif f == "0":
                f = False

            if all([q, f]):
                results = []
                sponsored = []
                pages, sponsored_pages = query_list(q, s)
                f = f.split(",")
                for x in f:
                    p = [n for n in pages if n.category == x]
                    for y in p:
                        results.append(y)
                    s = [t for t in sponsored_pages if t.category == x]
                    for y in s:
                        sponsored.append(y)
            elif q:
                results, sponsored = query_list(q, s)
            elif f:
                results, sponsored = filter_list(f, s)
            elif s:
                results, sponsored = state_list(s)
            else:
                results = None
                sponsored = None
        elif a == "pages":
            results = Page.objects.filter(is_sponsored=False, deleted=False).order_by('name')
            sponsored = Page.objects.filter(is_sponsored=True, deleted=False).order_by('name')
        elif a == "campaigns":
            results = Campaign.objects.filter(page__is_sponsored=False, deleted=False, is_active=True).order_by('name')
            sponsored = Campaign.objects.filter(page__is_sponsored=True, deleted=False, is_active=True).order_by('name')

        trending_pages = Page.objects.filter(deleted=False).order_by('-trending_score')[:10]
        trending_campaigns = Campaign.objects.filter(deleted=False, is_active=True).order_by('-trending_score')[:10]

        response_data = []
        if sponsored:
            for s in sponsored:
                if s in trending_pages or s in trending_campaigns:
                    response_data.append(create_search_result_html(s, True, True))
                else:
                    response_data.append(create_search_result_html(s, True, False))

        if results:
            for r in results:
                if r in trending_pages or r in trending_campaigns:
                    response_data.append(create_search_result_html(r, False, True))
                else:
                    response_data.append(create_search_result_html(r, False, False))

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
