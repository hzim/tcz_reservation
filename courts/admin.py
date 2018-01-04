from django.contrib import admin

from .models import TczHour

class TczHourAdmin(admin.ModelAdmin):
  """ what should be shown in the DJANGO admin page
  """
  fields = ('tcz_date', 'tcz_user', 'tcz_court', 'tcz_hour', 'tcz_user_change', 'tcz_free')
  list_display = ('tcz_date', 'tcz_user', 'tcz_court', 'tcz_hour', 'tcz_user_change', 'tcz_free')
  # admin_order_field = 'tcz_date'

admin.site.register(TczHour, TczHourAdmin)
