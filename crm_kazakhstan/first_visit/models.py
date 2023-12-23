from mothers.models import Mother


class FirstVisit(Mother):
    class Meta:
        proxy = True
