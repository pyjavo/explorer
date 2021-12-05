from django.contrib import admin

from .models import Register, AWSConstants


class RegisterAdmin(admin.ModelAdmin):
    list_display = (
        'file_name',
        'category',
        'owner',
        'created',
        'modified',
        'active'
    )
    list_filter = ('owner', 'category')


admin.site.register(Register, RegisterAdmin)


class AWSConstantsAdmin(admin.ModelAdmin):
    list_display = (
        'album_bucket_name',
        'bucket_region',
        'created',
        'modified',
    )

    def has_add_permission(self, request):
        return False


admin.site.register(AWSConstants, AWSConstantsAdmin)
