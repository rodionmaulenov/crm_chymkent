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
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def last_state(self):
        return self.state_set.filter(finished=False).exists()

    @property
    def plan(self):
        plan = self.planned_set.order_by('-created').exists()
        finished = self.planned_set.filter(finished=False).order_by('-created').exists()

        if plan:
            return finished
        return False

    @property
    def ban(self):
        ban = self.ban_set.order_by('-created').exists()
        finished = self.ban_set.filter(banned=False).order_by('-created').exists()

        if ban:
            return finished
        return False
