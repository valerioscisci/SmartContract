from django import forms

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
