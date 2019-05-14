from django import forms

# Definisce il form che servirà per l'inserimento di nuove misure nel libretto delle misure

class librettoForm(forms.Form):
    N_Ordine = forms.IntegerField()

    class Meta:
        widgets = {
            # Project Identification
            'N_Ordine': forms.NumberInput(attrs={'class': 'required'})
        }