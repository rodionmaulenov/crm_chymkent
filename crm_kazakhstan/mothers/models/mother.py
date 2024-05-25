from django.db import models


class Mother(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    program = models.CharField(max_length=100, blank=True, null=True)
    residence = models.CharField(max_length=100, blank=True, null=True)
    height_and_weight = models.CharField(max_length=100, blank=True, null=True)
    bad_habits = models.CharField(max_length=100, blank=True, null=True)
    caesarean = models.CharField(max_length=100, blank=True, null=True)
    children_age = models.CharField(max_length=100, blank=True, null=True)
    age = models.CharField(max_length=100, blank=True, null=True)
    citizenship = models.CharField(max_length=100, blank=True, null=True)
    blood = models.CharField(max_length=100, blank=True, null=True)
    maried = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # if self is None must return '' because if add new document from inline without '' the error raise
        return self.name if self.name else ''

    @property
    def plan(self):
        return self.planned_set.filter(finished=False)

    @property
    def state(self):
        return self.state_set.filter(finished=False)

    @property
    def ban(self):
        return self.ban_set.filter(banned=False)
