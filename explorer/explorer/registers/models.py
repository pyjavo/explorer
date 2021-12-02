import uuid
from django.db import models
from registers import choices
from explorer.users.models import User


class Register(models.Model):
    '''
    This model will represent each instance of a dataset
    '''
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=u'Name of the csv file'
    )
    file_path = models.FileField(
        upload_to='uploads/',
        verbose_name=u'CSV file'
    )
    category = models.CharField(
        max_length=255,
        choices=choices.CATEGORIES
    )
    id_column = models.CharField(
        max_length=55, blank=True, help_text=u'*Optional'
    )
    target_column = models.CharField(
        max_length=55, help_text=u'*Opcional'
    )
    scores = models.JSONField()
    new_dataset = models.JSONField(default=dict)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # if user is delete it, so it's registers
        related_name='registers'
    )

    # TODO: aws integration
    # s3_bucket_path = models.URLField(
    #     blank=True,
    #     help_text='Escribe el enlace hacia tu página de Instagram'
    # )

    # s3_bucket_id = models.CharField(
    #     blank=True,
    #     max_length=250,
    # )

    class Meta:
        verbose_name = 'Register'
        verbose_name_plural = 'Registers'

    def __str__(self):
        return self.file_name
