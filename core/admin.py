from django.contrib import admin
from .models import Group, Membership, Activity  # Modellerinizi içe aktarın
from .models import Activity
# Modelleri admin paneline kaydedin
admin.site.register(Group)
admin.site.register(Membership)
admin.site.register(Activity)
