from mothers.models import Stage
from .manager import Manager


class PrimaryStageManager(Manager):
    """Designate user just from primary stage."""

    @staticmethod
    def get_stage():
        return Stage.StageChoices.PRIMARY
