from mothers.models import Mother


class BanProxy(Mother):
    class Meta:
        verbose_name = 'ban'
        verbose_name_plural = 'bans'
        proxy = True
