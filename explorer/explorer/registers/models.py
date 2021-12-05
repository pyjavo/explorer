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
        max_length=55, help_text=u'*Optional'
    )
    scores = models.JSONField()
    new_dataset = models.JSONField(
        default=dict, help_text=u'Generated file from the classification category'
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # if the user is delete it, so it's registers
        related_name='registers'
    )

    class Meta:
        verbose_name = 'Register'
        verbose_name_plural = 'Registers'

    def __str__(self):
        return self.file_name


class AWSConstants(models.Model):
    '''
    Keys used for the multivariate analysis

    Please refrain of adding a more objects. Just edit the current one
    '''
    album_bucket_name = models.CharField(
        max_length=100,
        help_text=u'Please refrain from adding more objects. Just edit the current one'
    )
    bucket_region = models.CharField(
        max_length=50,
    )
    identity_pool_id = models.CharField(
        max_length=150,
    )
    lambda_function_url = models.URLField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    # TODO: AWS integration need these keys to let the feature selection process
    # uploads the CSF file to the multivariate analysis by itself so the user
    # does not have to load the file by himself (to sum. avoid manual upload)
    # s3_bucket_path = models.URLField(
    #     blank=True,
    # )

    # s3_bucket_id = models.CharField(
    #     blank=True,
    #     max_length=250,
    # )

    class Meta:
        verbose_name = 'AWS Constant'
        verbose_name_plural = 'AWS Constants'

    def __str__(self):
        return self.album_bucket_name
