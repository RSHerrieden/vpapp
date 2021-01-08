from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from vpapp.models import *
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import date as dtdate
from bs4 import BeautifulSoup, element

import requests

class Command(BaseCommand):
    help = 'Load the replacementplan from the Realschule Herrieden'

    def add_arguments(self, parser):
        parser.add_argument(
            'dates', nargs='?',
            help='Dates to import in the form YYYY-MM-DD seperated by spcaes.'
        )

    def handle(self, *args, **options):
        if not settings.VPAPP_RSH_URL:
            CommandError('VPAPP_RSH_URL is not defined or empty')

        dates = options['dates']
        if dates == None:
            dates = self.get_next_business_days(0,2)
        elif dates == 'all':
            dates = self.get_next_business_days(-1000,100)
        else:
            _dates = dates.split(' ')
            dates = []
            for _date in _dates:
                if not _date:
                    continue

                date = timezone.make_aware(datetime.strptime(
                        _date,
                        '%Y-%m-%d'
                    ))

                dates.append(date)

        for date in dates:
            self.stdout.write('{:%Y-%m-%d}'.format(date), ending='... ')

            if not self.ensure_dely(date):
                self.stdout.write(self.style.NOTICE(' Wait'))
                continue

            plan = self.fetch_plan(date)

            if plan[2] == False:
                self.stdout.write(self.style.WARNING(plan[1]))
                continue

            self.import_plan(date, plan[0])
            self.stdout.write(self.style.SUCCESS('OK'))

    def ensure_dely(self, date, delay = None):
        if not delay:
            delay = settings.VPAPP_SCRAPE_DELAY

        qs = LastCheck.objects.filter(date=date)
        if not qs.exists():
            return True

        state = qs.first()
        now = timezone.now()
        difference = now - state.last_check
        difference_sec = difference.days * 24 * 60 * 60 + difference.seconds
        return difference_sec >= delay

    @staticmethod
    def get_next_business_days(start, end, steps=1):
        i = start
        date = datetime.combine(
                dtdate.today(),
                datetime.min.time()
            ) + timedelta(days=start)

        dates = []

        while i<=end:
            weekday = date.weekday() <= 4
            while not weekday:
                date += timedelta(days=1)
                weekday = date.weekday() <= 5

            if start <= i <= end and i % steps == 0:
                dates.append(timezone.make_aware(date))

            i += 1
            date += timedelta(days=1)

        return dates

    def fetch_plan(self, date, url_template = None):
        if url_template == None:
            url_template = settings.VPAPP_RSH_URL

        url = url_template.format(date)
        r = requests.get(url)
        success = r.status_code == requests.codes.ok

        check = LastCheck.objects.filter(date=date)
        if not check.exists():
            check = LastCheck.objects.create(date=date)
        else:
            check = check.get()

        if success != check.success:
            check.last_change = timezone.now()
            check.success = success

        check.last_check = timezone.now()
        check.save()

        return (r.text, r.status_code, success)

    def import_plan(self, date, plan):
        changes = 0

        plan = BeautifulSoup(plan, 'xml').Plan
        _state = timezone.make_aware(datetime.strptime(
                plan.Erstellungsdatum.string[3:],
                '%d.%m.%Y %H:%M'
            ))

        state, created = LastCheck.objects.update_or_create(
                date=date,
                defaults={
                    'state': _state
                }
            )

        if created:
            state.last_change = timezone.now()

        notifications = plan.SchuelerMitteilung['Text'].split('  ')

        pks = []

        for notification in notifications:
            if not notification:
                continue

            obj,changed = Notification.objects.get_or_create(
                date = date,
                content = notification
            )

            changes += int(changed)

            pks.append(obj.id)

        (Notification.objects
            .exclude(pk__in=pks)
            .filter(date=date)
            .delete())

        week = plan.Woche.string

        replacements = []

        for replacement in plan.Vertretungen.contents:
            if not isinstance(replacement, element.Tag):
                continue

            schoolclass_str = replacement.Klasse.string
            subject = replacement.Fach.string
            hour = replacement.Std.string
            room = replacement.Raum.string
            dropped = not replacement.Entfaellt.string == 'false'

            schoolclass, created = SchoolClass.objects.get_or_create(
                    name=schoolclass_str
                )

            obj, created = Replacement.objects.update_or_create(
                date=date,
                schoolclass=schoolclass,
                schoolsubject=subject,
                schoolhour=hour,
                defaults = {
                    'schoolroom': room,
                    'dropped': dropped,
                    'week': week
                }
            )

            changes += int(created)

            replacements.append(obj.id)

        (Replacement.objects
                .exclude(pk__in=replacements)
                .filter(date=date)
                .delete())

        if changes:
            state.last_change  = timezone.now()

        state.save()
