from django.http import HttpResponse,JsonResponse
from .models import SchoolClass, Replacement, Notification, LastCheck
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import date as dtdate
from dateutil.parser import parse
from django.shortcuts import render

def index_view(request):
    return render(request,'vpapp/index.html')

def api_v2_replacements(request, date = None, schoolclass = None):
    _date = date
    date = parse_user_date(date)

    _replacements = Replacement.objects.filter(date=date)

    if schoolclass and not schoolclass == 'alle':
        _replacements = _replacements.filter(schoolclass__name__like = '%' + schoolclass + '%')

    _replacements = _replacements.prefetch_related('schoolclass')

    replacements = []
    week = None
    for r in _replacements:
        replacements.append(r.api_dict)
        week = r.week

    if not replacements:
        _week = Replacement.objects.filter(date=date).only('week').first()
        if _week:
            week = _week.week

    if not week:
        week = ''

    return _api_v2_base(request, 'replacements', replacements, date, _date, schoolclass, week)

def api_v2_notifications(request, date = None):
    _date = date
    date = parse_user_date(date)
    _notifications = Notification.objects.filter(date=date)
    notifications = []

    for n in _notifications:
        notifications.append(n.content)

    return _api_v2_base(request, 'notifications', notifications, date, _date)

def _api_v2_base(request, method = None, data = None, date = None, req_date = None, schoolclass = None, week = ''):
    if method not in ['replacements', 'notifications']:
        raise ValueError('method mus either be replacements or notifications')

    state = LastCheck.objects.filter(date=date)

    code = 200
    if not state:
        state = LastCheck(date=date)
        success = False
        code = 404
    else:
        success = True
        state = state.get()

    response = {
        'success': success,
        'code': code,
        'request': {
            'method': method,
            'class': schoolclass,
            'date': req_date,
        },
        'versions': {'api': 'v2.1.0'},
        'query': {
            'date': format_localtime(date, '%Y-%m-%d'),
            'class': schoolclass
        },
    }

    response[method] = data

    if method == 'replacements':
        response['week'] = week

    response['amount'] = len(data)
    response['meta'] = state.meta_dict
    response['copyright'] = ['(c) Moritz Fromm', '(c) Noah Seefried']

    return JsonResponse(response)


def parse_user_date(date = None):
    if not date or date == 'next':
        return get_applicable_default_day(date == 'next')

    return parse(date)

def get_applicable_default_day(skip=False):
    offset = int(timezone.now().hour > 13 and timezone.now().isoweekday() <= 5)
    offset += int(skip)
    return find_next_biz_day(offset)

def find_next_biz_day(offset = 1, start = None):

    if start is None:
        start = datetime.combine(
                dtdate.today(),
                datetime.min.time()
            )
    elif isinstance(start, int):
        start = datetime.combine(
                dtdate.today(),
                datetime.min.time()
            ) + timedelta(days=start)
    elif isinstance(start, datetime):
        pass
    else:
        raise ValueError('start mus either be a int or a datetime object.')

    date = start
    delta = timedelta(days=1 if offset >= 0 else -1)

    def _is_biz_day(test_date):
        return test_date.isoweekday() <= 5

    n = 0

    while True:
        if not _is_biz_day(date):
            date += delta
            continue

        if n >= abs(offset):
            break

        date += delta
        n += 1

    return date

def format_localtime(date, fmt = None):
    if not fmt:
        fmt = '%Y-%m-%d %H:%M:%S'
    try:
        return timezone.localtime(date).strftime(fmt)
    except ValueError:
        return date.strftime(fmt)
