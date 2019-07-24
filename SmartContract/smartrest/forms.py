from django import forms
from .models import Contratto, User, Lavoro, Misura

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
        }

# Definisce il form che servirà per l'inserimento di nuove misure nel libretto delle misure

class librettoForm(forms.ModelForm):

    # Metodo  per inizializzare il valore di alcuni campi in modo automatico

    def __init__(self, *args, **kwargs):
        contratto = kwargs.pop('contratto', None)  # if dict kwargs has no key 'contratto', contratto is assigned None
        super().__init__(*args, **kwargs)
        if contratto:
            self.fields['Lavoro'].widget = forms.Select(
                choices=((x.Contratto, x.Contratto) for x in Lavoro.objects.filter(Contratto=contratto))) # Aggiungo la lista dei lavori esistenti relativi al contratto selezionato dal direttore

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
