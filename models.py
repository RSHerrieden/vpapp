from django.db import models
from django.utils import timezone
from django.db.models import Lookup
from django.db.models import CharField

@CharField.register_lookup
class LikeLookup(Lookup):
    lookup_name = 'like'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s LIKE %s' % (lhs, rhs), params

class LastCheck(models.Model):
    date = models.DateField(unique=True)
    last_check = models.DateTimeField(auto_now=True)
    last_change = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    state = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=True)

    @property
    def timestamp(self):
        return self.last_check

    @property
    def meta_dict(self):
        fmt = '%Y-%m-%d %H:%M:%S'
        return {
            'state': timezone.localtime(self.state).strftime(fmt),
            'date': self.date.strftime('%Y-%m-%d'),
            'timestamp': timezone.localtime(self.timestamp).strftime(fmt),
            'lastCheck': timezone.localtime(self.last_check).strftime(fmt)
        }

class Notification(models.Model):
    date = models.DateField()
    content = models.CharField(max_length=255)

    def __str__(self):
        return '{} @{}: {}'.format(self.date, self.state, self.content)

class SchoolClass(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)

class Replacement(models.Model):
    date = models.DateField()

    schoolclass = models.ForeignKey(
            'SchoolClass',
            on_delete = models.PROTECT
        )

    schoolhour = models.PositiveIntegerField(null=True, blank=True)
    schoolsubject = models.CharField(max_length=15, null=True, blank=True)
    schoolroom = models.CharField(max_length=15, null=True, blank=True)
    week = models.CharField(
            max_length=1,
            null=True,
            blank=True,
            choices=[
                ('A', 'A Woche'), ('B', 'B WocheB Woche')
            ]
        )

    dropped = models.BooleanField(default=False)

    def __str__(self):
        return '{}/{} @{}: {} {}->{} ({})'.format(
                    self.date,
                    self.schoolhour,
                    self.state,
                    self.schoolclass.name,
                    self.schoolsubject,
                    self.schoolroom if not self.dropped else 'x',
                    self.id
                )

    @property
    def dropped_int(self):
        return int(self.dropped)

    @property
    def api_dict(self):
        return {
            'schoolclass': self.schoolclass.name,
            'schoolhour': str(self.schoolhour),
            'schoolsubject': self.schoolsubject,
            'schoolroom': self.schoolroom,
            'dropped': self.dropped
        }

    class Meta:
        ordering = ('schoolclass__name', 'date')
