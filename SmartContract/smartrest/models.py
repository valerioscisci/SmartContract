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
