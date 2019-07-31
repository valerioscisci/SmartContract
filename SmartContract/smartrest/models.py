from django.db import models
from django.contrib.auth.models import AbstractUser

# Modello per contenere gli abi dei contratti

class Contracts_Abis(models.Model):
    Abi_ID = models.AutoField(primary_key=True) # ID del relativo Abi
    Abi_Value = models.TextField(max_length=6000) # Abi del contratto

# Modello per contenere informazioni relative ai contratti deployati sulla blockchain

class Contracts(models.Model):
    class Meta:
        unique_together = (('Contract_ID', 'Username'),)

    Contract_ID = models.IntegerField(default=1)  # Id per identificare il contratto
    Username = models.CharField(max_length=75, default='', blank=True)  # Nome Utente del creatore del contratto
    Contract_Type = models.CharField(max_length=50) # Indica il tipo di contratto (Appalto, Valore, Conforme, StringUtils)
    Contract_Address = models.CharField(max_length=100) # Indirizzo dove è deployato il contratto sulla blockchain
    Contract_Abi = models.ForeignKey(Contracts_Abis, on_delete=models.CASCADE) # Riferimento al relativo Abi

# Estendiamo il modello base dell'utente per poter aggiungere l'indirizzo dell'account associato sulla blockchain

class User(AbstractUser):
    Account = models.CharField(max_length=100)

# Modello contenente un contratto creato dalla stazione appaltante

class Contratto(models.Model):
    Utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Chiave esterna utente stazione
    Nome = models.CharField(max_length=100)  # Nome del contratto
    Importo = models.FloatField()  # Valore del cotratto in euro
    Ditta = models.CharField(max_length=100) # Ditta appaltatrice
    Direttore = models.CharField(max_length=100) # Direttore dei lavori

# Modello contenente i lavori dei contratti creati dalla stazione appaltante

class Lavoro(models.Model):
    Contratto = models.ForeignKey(Contratto, on_delete=models.CASCADE) # Riferimento al relativo Contratto
    Codice_Tariffa = models.CharField(max_length=50)  # Codice di Tariffa del lavoro
    Nome = models.CharField(max_length=100)  # Nome del lavoro
    Importo = models.FloatField()  # Valore totale del lavoro in euro
    Costo_Unitario = models.FloatField(default=0.0) # Costo unitario di ogni componente del lavoro, che sarà 0 per lavori non divisibili

# Modello contenente le misure relative ai lavori inserite dal direttore dei lavori

class Misura(models.Model):
    Lavoro = models.ForeignKey(Lavoro, on_delete=models.CASCADE) # Riferimento al relativo Lavoro
    Codice_Tariffa = models.CharField(max_length=50, blank=True) # Codice di Tariffa del lavoro
    Data = models.DateField() # Data della misurazione
    Designazione_Lavori = models.TextField(max_length=1000, blank=True) # Descrizione libera della misura
    Parti_Uguali = models.IntegerField(blank=True, null=True) # Numero parti misurazione se è possibile contarle
    Larghezza = models.FloatField(blank=True, null=True) # Dimensioni
    Lunghezza = models.FloatField(blank=True, null=True) # Dimensioni
    Altezza_Peso = models.FloatField(blank=True, null=True) # Dimensioni
    Positivi = models.IntegerField() # Numero/percentuale misurazioni positive
    Negativi = models.IntegerField(blank=True, null=True) # Numero/percentuale misurazioni negative (di solito a zero)
    Stati_Riserva = (
        ('NO', 'No'),
        ('Si', 'Si'),
    )
    Riserva =  models.CharField(max_length=10, choices=Stati_Riserva, default="NO") # Campo di tipo booleano per indicare la riserva o meno da parte del direttore
    Annotazioni = models.TextField(max_length=1000, blank=True) # Commenti aggiuntivi del direttore dei lavori
    Stati_Possibili = (
        ('INSERITO_LIBRETTO', 'Inserita nel Libretto'),
        ('INSERITO_LIBRETTO_RISERVA', 'Inserita nel Libretto con Riserva'),
        ('CONFERMATO_LIBRETTO', 'Confermata nel Libretto'),
        ('CONFERMATO_REGISTRO', 'Confermata nel Registro di Contabilità'),
    )
    Stato = models.CharField(max_length=100, choices=Stati_Possibili, default = 'INSERITO_LIBRETTO') # Indica lo stato attuale della misura
