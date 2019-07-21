from django import forms
from .models import Contratto, User, Lavoro

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
            'Costo_Unitario': forms.Select(attrs={'class': 'notrequired'}),
        }

# Definisce il form che servirà per l'inserimento di un nuovo contratto da parte della stazione appaltante

class ContrattoForm(forms.ModelForm):

    # Metodo  per inizializzare il valore del campo utente in automatico

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

class librettoForm(forms.Form):
    N_Ordine = forms.IntegerField()
    Data = forms.DateField()
    Codice_Tariffa = forms.IntegerField()
    Designazione_Lavori = forms.CharField(max_length=1000)
    Parti_Uguali = forms.IntegerField()
    Larghezza = forms.FloatField()
    Lunghezza = forms.FloatField()
    Altezza_Peso = forms.IntegerField()
    Positivi = forms.CharField(max_length=10)
    Negativi = forms.CharField(max_length=10)
    Annotazioni = forms.CharField(max_length=1000)
    Stato = forms.CharField(max_length=1000)

    # Widget necessari ad assegnare la classe ai campi del form
    N_Ordine.widget.attrs['class'] = 'required'
    Data.widget.attrs['class'] = 'required'
    Codice_Tariffa.widget.attrs['class'] = 'required'
    Designazione_Lavori.widget.attrs['class'] = 'required'
    Parti_Uguali.widget.attrs['class'] = 'required'
    Larghezza.widget.attrs['class'] = 'required'
    Lunghezza.widget.attrs['class'] = 'required'
    Altezza_Peso.widget.attrs['class'] = 'required'
    Positivi.widget.attrs['class'] = 'required'
    Negativi.widget.attrs['class'] = 'required'
    Annotazioni.widget.attrs['class'] = 'notrequired'
    Stato.widget.attrs['class'] = 'required'
