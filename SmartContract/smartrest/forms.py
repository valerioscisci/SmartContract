from django import forms
from django.contrib.auth.models import Group

from .models import Contratto, User, Lavoro, Misura, Soglia, Giornale, Images

# Definisce il form dove per la registrazione dell'utente

class RegisterForm(forms.ModelForm):
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'required'}),
    )
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'groups', 'Account', 'Password_Block',)
        labels = {
            'Account': ('Account Blockchain'),
            'Password_Block': ('Password Blockchain'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'required'}),
            'password': forms.PasswordInput(attrs={'class': 'required'}),
            'first_name': forms.TextInput(attrs={'class': 'notrequired'}),
            'last_name': forms.TextInput(attrs={'class': 'notrequired'}),
            'email': forms.EmailInput(attrs={'class': 'notrequired'}),
            'Account': forms.TextInput(attrs={'class': 'required'}),
            'Password_Block': forms.PasswordInput(attrs={'class': 'required'}),
        }

# Definisce il form che servirà per l'inserimento di una nuova voce nel Giornale dei Lavori

class GiornaleForm(forms.ModelForm):
    class Meta:
        model = Giornale
        fields = '__all__'
        widgets = {
            'Contratto': forms.HiddenInput(),
            'Data': forms.DateInput(attrs={'class': 'required'}),
            'Meteo': forms.TextInput(attrs={'class': 'notrequired'}),
            'Annotazioni_Generali': forms.Textarea(attrs={'class': 'required'}),
        }

# Definisce il form dove l'utente potrà inserire le immagini

class ImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ('Image',)
        widgets = {
            'Image': forms.FileInput(attrs={'class': 'notrequired', 'accept': 'image/gif, image/jpeg, image/jpg, image/png'}),
        }

# Definisce il form che servirà per l'inserimento di una nuova soglia da parte della stazione appaltante

class SogliaForm(forms.ModelForm):

    class Meta:
        model = Soglia
        fields = '__all__'
        widgets = {
            'Contratto': forms.HiddenInput(),
            'Importo_Pagamento': forms.NumberInput(attrs={'class': 'required'}),
            'Percentuale_Da_Raggiungere': forms.NumberInput(attrs={'class': 'required'}),
            'Attuale': forms.HiddenInput(),
        }

# Definisce il form che servirà per l'inserimento di un nuovo lavoro da parte della stazione appaltante

class LavoroForm(forms.ModelForm):

    class Meta:
        model = Lavoro
        fields = '__all__'
        widgets = {
            'Contratto': forms.HiddenInput(),
            'Codice_Tariffa': forms.TextInput(attrs={'class': 'required'}),
            'Nome': forms.TextInput(attrs={'class': 'required'}),
            'Importo': forms.NumberInput(attrs={'class': 'required'}),
            'Costo_Unitario': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Debito': forms.HiddenInput(),
            'Percentuale': forms.HiddenInput(),
        }

# Definisce il form che servirà per l'inserimento di un nuovo contratto da parte della stazione appaltante

class ContrattoForm(forms.ModelForm):

    # Metodo  per inizializzare il valore del campo utente e altri campi in automatico

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # if dict kwargs has no key 'user', user is assigned None
        super().__init__(*args, **kwargs)
        if user:
            self.fields['Ditta'].widget = forms.Select(choices=( (x.id, x.username) for x in User.objects.filter(groups__name='DittaAppaltatrice')))
            self.fields['Direttore'].widget = forms.Select(choices=( (x.id, x.username) for x in User.objects.filter(groups__name='DirettoreLavori')))
            self.fields['Utente'].initial = user.id  # Foreing Key dell'utente loggato che sta creando il contratto

    class Meta:
        model = Contratto
        fields = '__all__'
        widgets = {
            'Utente': forms.HiddenInput(),
            'Nome': forms.TextInput(attrs={'class': 'required'}),
            'Importo': forms.NumberInput(attrs={'class': 'required'}),
            'Ditta': forms.Select(attrs={'class': 'required'}),
            'Direttore': forms.Select(attrs={'class': 'required'}),
            'Terminato': forms.HiddenInput(),
        }

# Definisce il form che servirà per l'inserimento di nuove misure nel libretto delle misure

class librettoForm(forms.ModelForm):

    class Meta:
        model = Misura
        fields = '__all__'
        widgets = {
            'Lavoro': forms.Select(attrs={'class': 'required'}),
            'Codice_Tariffa': forms.HiddenInput(),
            'Data': forms.DateInput(attrs={'class': 'required'}),
            'Designazione_Lavori': forms.Textarea(attrs={'class': 'notrequired'}),
            'Parti_Uguali': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Larghezza': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Lunghezza': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Altezza_Peso': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Positivi': forms.NumberInput(attrs={'class': 'required'}),
            'Negativi': forms.NumberInput(attrs={'class': 'notrequired'}),
            'Riserva': forms.Select(attrs={'class': 'required'}),
            'Annotazioni': forms.Textarea(attrs={'class': 'notrequired'}),
            'Stato': forms.HiddenInput(),
        }
