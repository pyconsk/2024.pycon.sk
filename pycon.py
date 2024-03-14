import os
from datetime import date
from operator import itemgetter
from collections import OrderedDict

from flask import Flask, g, request, render_template, abort, make_response, url_for, redirect
from flask_babel import Babel, gettext, lazy_gettext

from schedule import (
    FRIDAY1, FRIDAY2,
    SATURDAY1, SATURDAY2,
    SUNDAY_A, SUNDAY_B, SUNDAY_C, SUNDAY_D, SUNDAY_E, SUNDAY_F, SUNDAY_G
)
from utils import get_news, get_speakers, get_talks, get_sponsors, encode_name, decode_name, get_jobs

EVENT = gettext('PyCon SK 2024 | Bratislava, Slovakia')
DOMAIN = 'https://2024.pycon.sk'

LANGS = ('en', 'sk')
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'

app = Flask(__name__, static_url_path='/static')  # pylint: disable=invalid-name
app.config['BABEL_DEFAULT_LOCALE'] = 'sk'
app.jinja_options = {'extensions': ['jinja2.ext.with_', 'jinja2.ext.i18n']}
babel = Babel(app)  # pylint: disable=invalid-name

CATEGORIES = {
    'tickets': lazy_gettext('Tickets'),
    'conference': lazy_gettext('Conference'),
    'media': lazy_gettext('Media'),
    'speakers': lazy_gettext('Speakers'),
}

SPEAKERS = get_speakers()
TALKS = get_talks()
SPONSORS = get_sponsors()


@app.route('/sitemap.xml')
def sitemap():
    excluded = {'static', 'sitemap'}
    pages = []

    for lang in LANGS:
        for rule in app.url_map.iter_rules():

            if 'GET' in rule.methods and rule.endpoint not in excluded:
                # `url_for` appends unknown arguments as query parameters.
                # We want to avoid that when a page isn't localized.
                values = {'lang_code': lang} if 'lang_code' in rule.arguments else {}

                if 'name' in rule.arguments:
                    for speaker in SPEAKERS:
                        values['name'] = encode_name(speaker['name'])
                        pages.append(DOMAIN + url_for(rule.endpoint, **values))
                elif 'category' in rule.arguments:
                    for category in CATEGORIES.keys():
                        values['category'] = category
                        pages.append(DOMAIN + url_for(rule.endpoint, **values))
                else:
                    pages.append(DOMAIN + url_for(rule.endpoint, **values))

    sitemap_xml = render_template('sitemap.xml', pages=pages, today=date.today())
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/')
def root():
    return redirect('sk/index.html')


@app.route('/<lang_code>/index.html')
def index():
    template_vars = _get_template_variables(li_index='active', news=get_news(get_locale(), items=3),
                                            categories=CATEGORIES, background_filename='img/about/header1.jpg',
                                            speakers=SPEAKERS, sponsors=SPONSORS)
    return render_template('index.html', **template_vars)


# @app.route('/chat.html')
# def chat():
#     template_vars = _get_template_variables(li_index='active', news=get_news(get_locale(), items=3),
#                                             categories=CATEGORIES, background_filename='img/about/header1.jpg',
#                                             speakers=SPEAKERS, sponsors=SPONSORS,
#                                             redirect="https://discord.gg/pr2cE4uT")
#     return render_template('index.html', **template_vars)

@app.route('/<lang_code>/news.html')
def news():
    template_vars = _get_template_variables(li_news='active', news=get_news(get_locale()), categories=CATEGORIES,
                                            background='bkg-news')
    return render_template('news.html', **template_vars)


@app.route('/<lang_code>/news/<category>.html')
def news_category(category):
    if category not in CATEGORIES.keys():
        abort(404)

    template_vars = _get_template_variables(li_news='active', categories=CATEGORIES, background='bkg-news')
    news = []

    for item in get_news(get_locale()):
        if category in item['categories']:
            news.append(item)

    template_vars['news'] = news
    template_vars['category'] = category
    return render_template('news.html', **template_vars)


@app.route('/<lang_code>/coc.html')
def coc():
    return render_template('coc.html', **_get_template_variables(li_coc='active', background='bkg-chillout'))


# @app.route('/<lang_code>/faq.html')
# def faq():
#     return render_template('faq.html', **_get_template_variables(li_faq='active', background='bkg-chillout'))


@app.route('/<lang_code>/venue.html')
def venue():
    return render_template('venue.html', **_get_template_variables(li_venue='active', background='bkg-chillout'))


@app.route('/<lang_code>/aboutus.html')
def aboutus():
    return render_template('aboutus.html', **_get_template_variables(li_aboutus='active', background='bkg-index'))


@app.route('/<lang_code>/tickets.html')
def tickets():
    return render_template('tickets.html', **_get_template_variables(li_tickets='active', background='bkg-index'))


@app.route('/<lang_code>/cfp.html')
def cfp():
    return render_template('cfp.html', **_get_template_variables(li_cfp='active', background='bkg-speaker'))


# @app.route('/<lang_code>/cfp_form.html')
# def cfp_form():
#     return render_template('cfp_form.html', **_get_template_variables(li_cfp='active', background='bkg-workshop'))


@app.route('/<lang_code>/recording.html')
def recording():
    return render_template('recording.html', **_get_template_variables(li_recording='active', background='bkg-snake'))


@app.route('/<lang_code>/cfv.html')
def cfv():
    return render_template('cfv.html', **_get_template_variables(li_cfv='active', background='bkg-cfv'))


@app.route('/<lang_code>/sponsors.html')
def sponsors():
    return render_template('sponsors.html',
                           **_get_sponsors_variables(li_sponsors='active', background='bkg-index', sponsors=SPONSORS))


# @app.route('/<lang_code>/thanks.html')
# def thanks():
#     return render_template('thanks.html', **_get_template_variables(li_cfp='active', background='bkg-index'))


@app.route('/<lang_code>/privacy-policy.html')
def privacy_policy():
    return render_template('privacy-policy.html', **_get_template_variables(li_privacy='active',
                                                                            background='bkg-privacy'))


# @app.route('/<lang_code>/program/index.html')
# def program():
#     # variables = _get_template_variables(li_program='active', background='bkg-speaker', speakers=SPEAKERS)
#     # variables['talks_list'] = []
#     # variables['workshops_link'] = []
#     #
#     # for talk in TALKS:
#     #     if talk['type'] == 'Talk':
#     #         variables['talks_list'].append({
#     #             'talk': talk,
#     #             'speakers': talk['speakers']
#     #         })
#     #         continue
#     #     elif talk['type'] == 'Workshop':
#     #         variables['workshops_link'].append({
#     #             'talk': talk,
#     #             'speakers': talk['speakers']
#     #         })
#     #         continue
#     #
#     # return render_template('program.html', **variables)
#     return redirect('/')


@app.route('/<lang_code>/speakers/index.html')
def speakers():
    variables = _get_template_variables(li_speakers='active', background='bkg-speaker', speakers=SPEAKERS)

    return render_template('speaker_list.html', **variables)


@app.route('/<lang_code>/talks.html')
def talks():
    variables = _get_template_variables(li_talks='active', background='bkg-speaker', talks=TALKS, speakers=SPEAKERS)

    return render_template('talk_list.html', **variables)


@app.route('/<lang_code>/virtual-swag.html')
def swag():
    virtual_swag = [
        {
            "title": "TITANS",
            "img": "swag_titans.png",
            "link": "https://join.titans.eu/en/?utm_source=banner&utm_medium=virtual+swag&utm_campaign=PyCon&utm_id=07032024&utm_term=homepage&utm_content=jointhetitans",
        },
        {
            "title": "ALITER",
            "img": "swag_aliter.jpg",
            "link": "https://www.aliter.com/sk/kariera",
        },
        {
            "title": "GOPAS",
            "img": "swag_gopas.png",
            "link": "https://www.gopas.sk/GopasAdvancedSearch/Search?q=python&AuthorizationVendor=0",
        },
        {
            "title": "IBL Software Engineering",
            "img_double": [
                "swag_ibl_1.png",
                "swag_ibl_2.png",
            ],
            "link": "https://www.iblsoft.com/",
        },
        {
            "title": "Blueprint Power",
            "img": "swag_blueprintpower.png",
            "css_tags": "col-10 col-sm-6 col-md-5",
            "link": "https://www.blueprintpower.com/",
        },
    ]
    variables = _get_template_variables(li_swag='active', background='bkg-speaker', swag=virtual_swag)
    return render_template('swag.html', **variables)

@app.route('/<lang_code>/speakers/<name>.html')
def profile(name):
    variables = _get_template_variables(li_speakers='active', background='bkg-speaker')

    for speaker in SPEAKERS:
        speaker['talks'] = []
        if speaker['name'].lower() == decode_name(name):
            for talk in TALKS:
                if speaker['name'] in talk.get('speakers', []):
                    speaker.get('talks', []).append(talk)
            variables['speaker'] = speaker
            break

    if not variables.get('speaker'):
        return abort(404)

    return render_template('speaker.html', **variables)

def _get_schedule_details(day):
    for item in day:
        matched_talks = [x for x in TALKS if x["title"] == item["title"]]
        if matched_talks:
            matched_talk = matched_talks[0]
            if not item.get('tag'):
                item['tag'] = matched_talk.get("tag", "")

            matched_speakers = [x for x in SPEAKERS if x["name"] in matched_talk["speakers"]]
            if matched_speakers:
                matched_speaker = matched_speakers[0]
                if not item.get('name'):
                    item['name'] = matched_speaker["name"]
                if not item.get('avatar'):
                    item['avatar'] = "/static/" + matched_speaker["avatar"]
                if not item.get('speaker_url'):
                    item['speaker_url'] = matched_speaker["name"]
    return day


@app.route('/<lang_code>/friday.html')
def friday():
    rooms = [
        {
            "title": "Blue room",
            "slug": "blue_room",
            "talks": _get_schedule_details(FRIDAY1),
            "active": True,
        },
        {
            "title": "Yellow room",
            "slug": "yellow_room",
            "talks": _get_schedule_details(FRIDAY2),
        },
    ]
    context = _get_template_variables(
        li_friday='active',
        rooms=rooms,
        day=gettext('Friday'),
        background='bkg-speaker',
    )
    return render_template('schedule.html', **context)

@app.route('/<lang_code>/saturday.html')
def saturday():
    rooms = [
        {
            "title": "Blue room",
            "slug": "blue_room",
            "talks": _get_schedule_details(SATURDAY1),
            "active": True,
        },
        {
            "title": "Yellow room",
            "slug": "yellow_room",
            "talks": _get_schedule_details(SATURDAY2),
        },
    ]

    context = _get_template_variables(
        li_saturday='active',
        rooms=rooms,
        day=gettext('Saturday'),
        background='bkg-speaker',
    )

    return render_template('schedule.html', **context)

@app.route('/<lang_code>/sunday.html')
def sunday():
    rooms = [
        {
            "title": "Room A",
            "slug": "workshop_a",
            "talks": _get_schedule_details(SUNDAY_A),
            "active": True,
        },
        {
            "title": "Room B",
            "slug": "workshop_b",
            "talks": _get_schedule_details(SUNDAY_B),
        },
        {
            "title": "Room C",
            "slug": "workshop_c",
            "talks": _get_schedule_details(SUNDAY_C),
        },
        {
            "title": "Room D",
            "slug": "workshop_d",
            "talks": _get_schedule_details(SUNDAY_D),
        },
        {
            "title": "Room E",
            "slug": "workshop_e",
            "talks": _get_schedule_details(SUNDAY_E),
        },
        {
            "title": "Room F",
            "slug": "workshop_f",
            "talks": _get_schedule_details(SUNDAY_F),
        },
        {
            "title": "Room G",
            "slug": "workshop_g",
            "talks": _get_schedule_details(SUNDAY_G),
        },
    ]
    context = _get_template_variables(
        li_sunday='active',
        rooms=rooms,
        day=gettext('Sunday'),
        background='bkg-speaker',
    )

    return render_template('schedule.html', **context)

# @app.route('/<lang_code>/countdown.html')
# def countdown():
#     template_vars = _get_template_variables(li_index='active', background='bkg-index')
#     return render_template('countdown.html', **template_vars)


# @app.route('/<lang_code>/jobs.html')
# def jobs():
#     job_offers = get_jobs()
#     companies = sorted(set(map(itemgetter("company"), job_offers)))
#     template_vars = _get_template_variables(
#         li_jobs='active',
#         background='bkg-chillout',
#         jobs=job_offers,
#         companies=companies
#     )
#     return render_template('jobs.html', **template_vars)


@app.route('/<lang_code>/livestream-blue-room.html')
def livestream_blue_room():
    template_vars = _get_template_variables(
        li_livestream1='active',
        background='bkg-speaker',
        room_name='Blue room',
        youtube_stream='RTr3cWEiJ24',
        slido_link='https://app.sli.do/event/mV6iVEoabpt1d4xN9F7YSS/live/questions',
    )
    return render_template('livestream.html', **template_vars)


@app.route('/<lang_code>/livestream-yellow-room.html')
def livestream_yellow_room():
    template_vars = _get_template_variables(
        li_livestream2='active',
        background='bkg-speaker',
        room_name='Yellow room',
        youtube_stream='EC4KK_Lh7GM',
        slido_link='https://app.sli.do/event/mV6iVEoabpt1d4xN9F7YSS/live/questions',
    )
    return render_template('livestream.html', **template_vars)


def get_speaker_url():
    pass

def _get_template_variables(**kwargs):
    """Collect variables for template that repeats, e.g. are in body.html template"""
    variables = {
        'title': EVENT,
        'domain': DOMAIN,
        'lang_code': get_locale(),
    }
    variables.update(kwargs)

    return variables


def _get_schedule_variables(**kwargs):
    variables = _get_template_variables(**kwargs)
    lang_code = get_locale()
    _schedule_vars = ['magna', 'minor', 'babbageovaA', 'babbageovaB', 'digilab']
    for key, spots in kwargs.items():
        if key not in _schedule_vars:
            continue
        for spot in spots:
            name = spot.get('name')
            if name is None:
                continue
            _speakers = [spkr.strip() for spkr in name.split(',')]
            spkr = _speakers and _speakers[0]   # todo fix multiple speakers
            spot['speaker'] = url_for('profile', lang_code=lang_code,
                                      name=spkr.lower().replace('-', '--').replace(' ', '-'))
            # spot['speakers'] = [url_for('profile', lang_code=lang_code,
            #                             name=spkr.lower().replace('-', '--').replace(' ', '-'))
            #                     for spkr in _speakers]
    return variables


def _get_sponsors_variables(**kwargs):
    variables = _get_template_variables(**kwargs)
    return variables


@app.before_request
def before():  # pylint: disable=inconsistent-return-statements
    if request.view_args and 'lang_code' in request.view_args:
        g.current_lang = request.view_args['lang_code']
        if request.view_args['lang_code'] not in LANGS:
            return abort(404)
        request.view_args.pop('lang_code')


@babel.localeselector
def get_locale():
    # try to guess the language from the user accept
    # header the browser transmits. The best match wins.
    # return request.accept_languages.best_match(['de', 'sk', 'en'])
    return g.get('current_lang', app.config['BABEL_DEFAULT_LOCALE'])
