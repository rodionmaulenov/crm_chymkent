from mothers.models import Mother


class BanProxy(Mother):
    class Meta:
        app_label = 'mothers'
        verbose_name = 'MotherBan'
        verbose_name_plural = 'bans'
        proxy = True
