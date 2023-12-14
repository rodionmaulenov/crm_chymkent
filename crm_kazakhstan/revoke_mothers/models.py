from mothers.models import Mother


class RevokeMother(Mother):
    class Meta:
        proxy = True
