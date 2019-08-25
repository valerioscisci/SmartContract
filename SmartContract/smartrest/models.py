from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Modello per contenere gli abi dei contratti

class Contracts_Abis(models.Model):
    Abi_ID = models.AutoField(primary_key=True) # ID del relativo Abi
    Abi_Value = models.TextField(max_length=6000) # Abi del contratto

# Modello per contenere informazioni relative ai contratti deployati sulla blockchain

class Contracts(models.Model):
    Tipi_Contratto = (
        ('Appalto', 'Appalto'),
        ('Valore', 'Valore'),
        ('Conforme', 'Conforme'),
        ('StringUtils', 'StringUtils'),
    )
    Contract_Type = models.CharField(max_length=50, choices=Tipi_Contratto) # Indica il tipo di contratto (Appalto, Valore, Conforme, StringUtils)
    Contract_Address = models.CharField(max_length=100) # Indirizzo dove è deployato il contratto sulla blockchain
    Contract_Abi = models.ForeignKey(Contracts_Abis, on_delete=models.CASCADE) # Riferimento al relativo Abi

# Estendiamo il modello base dell'utente per poter aggiungere l'indirizzo dell'account associato sulla blockchain

class User(AbstractUser):
    Account = models.CharField(max_length=100)
    Password_Block = models.CharField(max_length=50)

# Modello contenente un contratto creato dalla stazione appaltante

class Contratto(models.Model):
    Utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Chiave esterna utente stazione
    Nome = models.CharField(max_length=100)  # Nome del contratto
    Importo = models.FloatField()  # Valore del cotratto in euro
    Ditta = models.CharField(max_length=100) # Ditta appaltatrice
    Direttore = models.CharField(max_length=100) # Direttore dei lavori
    Terminato = models.BooleanField(default=False) # Campo booleano che ci dice se un contratto è completo al 100%

# Modello contenente i lavori dei contratti creati dalla stazione appaltante

class Lavoro(models.Model):
    Contratto = models.ForeignKey(Contratto, on_delete=models.CASCADE) # Riferimento al relativo Contratto
    Codice_Tariffa = models.CharField(max_length=50)  # Codice di Tariffa del lavoro
    Nome = models.CharField(max_length=100)  # Nome del lavoro
    Importo = models.FloatField()  # Valore totale del lavoro in euro
    Aliquota = models.FloatField()  # Indica il valore dell'aliquota per il lavoro specifico
    Costo_Unitario = models.FloatField(default=0.0) # Costo unitario di ogni componente del lavoro, che sarà 0 per lavori non divisibili
    Debito = models.FloatField(default=0.0) # Quantità di denaro che la ditta deve ricevere in un dato istante. Viene scalato se la quantità di denaro è erogata dalla stazione
    Percentuale = models.IntegerField(default=0.0) # Percentuale di completamente di un lavoro in un certo istante

# Modello contenente le soglie dei contratti creati dalla stazione appaltante

class Soglia(models.Model):
    Contratto = models.ForeignKey(Contratto, on_delete=models.CASCADE) # Riferimento al relativo Contratto
    Importo_Pagamento = models.FloatField()  # Valore in euro che verrà erogato al momento del raggiungimento della soglia
    Percentuale_Da_Raggiungere = models.FloatField() # Percentuale da raggiungere per scatenare il pagamento
    Attuale = models.BooleanField(default=True) # Campo booleano che ci dice qual'è la soglia attuale da raggiungere per il pagamento

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
    Firma_Direttore = models.CharField(max_length=200, default="", blank=True) # Contiene la firma applicata dal direttore
    Firma_Stazione = models.CharField(max_length=200, default="", blank=True)  # Contiene la firma applicata dalla stazione

# Modello contenente le voci inserite nel giornale dei lavori

class Giornale(models.Model):
    Contratto = models.ForeignKey(Contratto, on_delete=models.CASCADE) # Riferimento al relativo Contratto
    Data = models.DateField() # Data di inserimento della voce
    Meteo = models.CharField(max_length=150, blank=True) # Meteo osservato nel giorno indicato
    Annotazioni_Generali = models.TextField(max_length=2000) # Annotazioni e avvenimenti particolari osservati dal direttore

# Modello Usato per contenere le immagini inserite nelle voci del giornale dei lavori

class Images(models.Model):

    # Metodo usato per definire il path dell'immagine caricata -- MEDIA_ROOT/contratto/filename.xxx
    def contract_directory_path(self, filename):

        return 'giornale_{0}/{1}/{2}'.format(self.Giornale.Contratto.id, self.Giornale.id, filename)

    # Metodo usato per validare l'estensione dell'immagine caricate
    def validate_file_extension(fieldfile_obj):
        import os
        ext = os.path.splitext(fieldfile_obj.name)[1]
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if ext not in valid_extensions:
            raise ValidationError(u'Invalid File Extension!')

    # Metodo usato per verificare se l'immagine inserita ha dimensione minore di 10 MB
    def validate_file_size(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 10
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    Giornale = models.ForeignKey(Giornale, on_delete=models.CASCADE) # Riferimento al giornale dei lavori a cui appartiene l'immagine
    Image = models.ImageField(validators=[validate_file_extension, validate_file_size], upload_to=contract_directory_path, verbose_name='Image') # File immagine

# Modello usato per contenere i riferimenti alle transazioni in blockchain in modo da poterle verificare in qualsiasi momento

class Transazione(models.Model):
    Descrizione = models.TextField(max_length=500) # Descrizione del contenuto della transazione
    Hash_Transazione = models.CharField(max_length=100) # Hash della transazione
    Numero_Blocco = models.IntegerField() # Numero del blocco in cui si trova la transazione
    Mittente = models.CharField(max_length=100) # Indirizzo hex dell'account del mittente
    Destinatario = models.CharField(max_length=100) # Indirizzo hex dell'account del destinatario