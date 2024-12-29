from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class TerminalCommand(TimeStampedModel):
    objects = models.Manager()
    command = models.CharField(max_length=100)
    prompt = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    favorite = models.BooleanField(default=False)
    execution_count = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["command", "prompt"], name="unique_command_prompt"
            ),
        ]
        verbose_name = "Terminal Command"
        verbose_name_plural = "Terminal Commands"

    def __str__(self):
        return str(self.command)
