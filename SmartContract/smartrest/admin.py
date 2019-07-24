from django.contrib import admin
from smartrest.models import Contracts_Abis, Contracts, User, Contratto, Lavoro, Misura

# Registra i modelli nell'interfaccia dell'admin così da poterli modificare e interagirci

admin.site.register(Contracts_Abis)
admin.site.register(Contracts)
admin.site.register(Contratto)
admin.site.register(Lavoro)
admin.site.register(Misura)

# Classe che impedisce all'amministratore di cambiare le password degli utenti

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    fields = ['username', 'password', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_superuser', 'is_active',"Account"]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # when editing an object
            return ['username', 'password']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        form.save()
        username = form.cleaned_data.get('username')
        if (username):
            user = User.objects.get(username=username)
            raw_password = form.cleaned_data.get('password')
            user.set_password(raw_password)
            user.save()

admin.site.register(User, UserAdmin) # Permette all'admi di editare gli utenti a meno della password
