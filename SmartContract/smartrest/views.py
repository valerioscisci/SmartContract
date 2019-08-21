# DJANGO IMPORTS
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from django.forms import modelformset_factory
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import JsonResponse, HttpResponse
# MODELS IMPORTS
from .models import User, Contracts, Contratto, Lavoro, Misura, Soglia, Giornale, Images
# FORMS IMPORTS
from .forms import librettoForm, ContrattoForm, LavoroForm, SogliaForm, GiornaleForm, ImageForm, RegisterForm
# OTHER IMPORTS
import json
from web3 import Web3
from solcx import compile_files
from notify.signals import notify

# Vista per la Homepage

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'home.html', context=None)

# Vista per l'Authentication System

class AuthenticationView(TemplateView):
    template_name = "login.html"

# Vista per la Contract Area

class ContractAreaView(TemplateView):
    template_name = "contract_area/contract_area.html"

# Vista per la Registrazione

def registrazione(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            group = form.cleaned_data.get('groups')
            user.set_password(raw_password) # Setta la il digest della password usando SHA2
            user.save()
            user.groups.add(group) # Aggiunge i gruppi di appartenenza delll'utente (In teoria se ne deve scegliere  solo uno)
            user = authenticate(username=username, password=raw_password)
            login(request, user) # Logga l'utente appena creato
            return redirect('contract_area') # Lo rimanda alla sua area contratti
    else:
        form = RegisterForm()
    return render(request, 'registration/registrazione.html', {'form': form})

# Vista per inserire una nuova voce nel giornale

@login_required
def nuovavocegiornale(request):
    Contratti = Contratto.objects.filter(Direttore=request.user.id) # Prendo la lista dei contratti associati al direttore dei lavori che vuole inserire una voce nel giornale

    ImageFormSet = modelformset_factory(Images, form=ImageForm, extra=3) # Crea un form multiplo che permette l'inserimento delle immagini

    if request.method == "POST":
        response_data = {}  # invieremo con questa variabile la risposta alla chiamata ajax
        voceform = GiornaleForm(request.POST) # Form della voce del giornale
        formset = ImageFormSet(request.POST, request.FILES, queryset=Images.objects.none()) # Form delle immagini

        if voceform.is_valid() and formset.is_valid(): # Controllo che entrambi siano validi
            voce = voceform.save(commit=False) # Salva la nuova voce dle giornale
            voce.save()

            for form in formset.cleaned_data: # Scorre tutte le immagini inserite e le salva
                if form:
                    immagine = form['Image'] # Prende un'immgine
                    photo = Images(Giornale=voce, Image=immagine) # Crea una nuova istanza nel db dell'immagine
                    photo.save() # Salva l'immagine

            response_data["voce"] = "Successo"
        else:
            response_data["voce"] = "Errore"

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    else:
        voceform = GiornaleForm()
        formset = ImageFormSet(queryset=Images.objects.none())
    return render(request, 'contract_area/nuova_voce_giornale.html', {'voceform': voceform, 'formset': formset, 'contratti': Contratti})

# Vista per il redirect a seguito dell'inserimento di una nuova voce nel giornale

class nuovavocegiornaleredirect(TemplateView):
    template_name = "contract_area/nuova_voce_giornale_redirect.html"

# Vista per il Giornale dei Lavori

@login_required
def giornalelavori(request):
    if request.user.groups.filter(name="DirettoreLavori").exists():
        contratti = Contratto.objects.filter(Direttore=request.user.id)
    elif request.user.groups.filter(name="DittaAppaltatrice").exists():
        contratti = Contratto.objects.filter(Ditta=request.user.id)
    else:
        contratti = Contratto.objects.filter(Utente=request.user)
    voci_giornale = Giornale.objects.filter(Contratto__in=contratti)

    context = {'contratto': "all"} # Creo un context così da inizializzare il menù a tendina per filtrare le voci

    if request.method == "POST":
        # In base alla selezione nei menù a tendina, applico un filtro diverso alla lista delle misure
        contratto = request.POST.get("Contratto")
        if contratto != "all":
            contratti_filt = contratti.filter(id=contratto)
            voci_giornale = Giornale.objects.filter(Contratto__in=contratti_filt)
            context["contratto"] = contratto

    for voce in voci_giornale:
        immagini = Images.objects.filter(Giornale=voce.id)
        voce.Immagini = immagini

    return render(request, 'contract_area/giornale_lavori.html', {'contratti': contratti, 'voci_giornale': voci_giornale, 'context':context})

# Vista per lo Stato Avanzamento Lavori

@login_required
def statoavanzamento(request):
    if request.user.groups.filter(name="DirettoreLavori").exists():
        contratti = Contratto.objects.filter(Direttore=request.user.id)
    elif request.user.groups.filter(name="DittaAppaltatrice").exists():
        contratti = Contratto.objects.filter(Ditta=request.user.id)
    else:
        contratti = Contratto.objects.filter(Utente=request.user)

    # Mi calcolo la percentuale totale attuale di ciascun contratto per visualizzarla a schermo
    for contratto in contratti:  # Per ogni contratto vediamo la percentuale attuale dei lavori
        lavori_contratto = Lavoro.objects.filter(Contratto=contratto.id)  # Prendiamo i lavori del contratto in questione
        num_lavori = lavori_contratto.count()  # Li contiamo

        percentuale_parziale = 0
        for lavoro in lavori_contratto:
            percentuale_parziale += lavoro.Percentuale  # Somma le percentuali dei lavori

        percentuale_totale = percentuale_parziale / num_lavori  # Calcoliamo la percentuale del contratto proporzionalmente al numero di lavori

        contratto.Percentuale = percentuale_totale # Assegno la percentuale totale al contratto in questione

    if request.method == "POST":
        response_data = {}  # invieremo con questa variabile la risposta alla chiamata ajax

        contratto = request.POST.get("Contratto")

        ################ FORM 1 ################
        if contratto is not None:
            lavori = Lavoro.objects.filter(Contratto=contratto).values("id", "Nome", "Percentuale", "Importo", "Codice_Tariffa")

            response_data["lavori"] = list(lavori)  # Si passa la lista di lavori che serviranno ad inizializzare la lista del form di inserimento della misura
        else:
            response_data["lavori"] = "Errore"

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    return render(request, "contract_area/stato_avanzamento.html", {'contratti':contratti})

# Funzione utilizzata per calcolare la nuova percentuale di un lavoro a seguito di approvazione di misure nel registro

@login_required
def avanza_lavori(request, lavori_contratto, misure_aggregate, azzera):
    percentuale_parziale = 0
    i = 1
    for lavoro in lavori_contratto:  # Per ogni lavoro calcoliamo la percentuale di avanzamento
        try:
            positivi_lavoro = misure_aggregate.filter(Lavoro=lavoro.id).values("Positivi")[0]['Positivi']  # Prendiamo le misure positive per quel lavoro
        except:
            positivi_lavoro = 0
        if lavoro.Costo_Unitario == 0.0:  # Se il lavoro si misura in percentuale, si aggiunge la percentuale che è stata misurata
            percentuale_parziale += lavoro.Percentuale + positivi_lavoro
        else:  # Altrimento si calcola il l'avanzamento in percentuale in base agli elementi inseriti
            elementi_misurabili = lavoro.Importo / lavoro.Costo_Unitario
            percentuale_parziale += lavoro.Percentuale + (positivi_lavoro * 100 / elementi_misurabili)

        if azzera: # Se viene passato il valore true, allora viene aggiornata la percentuale del lavoro e viene salvata la nuova percentuale in blockchain
            lavoro.Percentuale = percentuale_parziale
            lavoro.save()

            ## sezione dedicata all'aggiornamento della percentuale in blockchain
            user = request.user.username
            account = Web3.toChecksumAddress(request.user.Account)
            password = request.user.Password_Block
            contract = Contracts.objects.filter(Username=user, Contract_Type='Appalto')  # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
            w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))  # Si connette al nodo per fare il deploy
            w3.eth.defaultAccount = account  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
            istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
            w3.personal.unlockAccount(w3.eth.defaultAccount, password, 0)  # Serve per sbloccare l'account prima di poter eseguire le transazioni

            if lavoro.Costo_Unitario == 0.0:  # Se il lavoro si misura in percentuale, si aggiunge la percentuale che è stata misurata
                istanza_contratto.functions.updateLavoro(i, positivi_lavoro).transact({'gas': 100000}) # La i è il numero di lavoro
            else:  # Altrimento si calcola il l'avanzamento in percentuale in base agli elementi inseriti
                elementi_misurabili = lavoro.Importo / lavoro.Costo_Unitario
                percentuale_avanzamento = (positivi_lavoro * 100 / elementi_misurabili)
                istanza_contratto.functions.updateLavoro(i, percentuale_avanzamento).transact({'gas': 100000}) # La i è il numero di lavoro
            ## fine lavoro in blockchain
            percentuale_parziale = 0
            i += 1

    return percentuale_parziale

# Vista per il Registro Contabilità

@login_required
def registrocont(request):
    if request.user.groups.filter(name="DirettoreLavori").exists():
        contratti = Contratto.objects.filter(Direttore=request.user.id)
    elif request.user.groups.filter(name="DittaAppaltatrice").exists():
        contratti = Contratto.objects.filter(Ditta=request.user.id)
    else:
        contratti = Contratto.objects.filter(Utente=request.user)
    lavori = Lavoro.objects.filter(Contratto__in=contratti)

    try:
        misure_aggregate = Misura.objects.filter(Lavoro__in=lavori, Stato="CONFERMATO_LIBRETTO").values("Codice_Tariffa", "Lavoro").annotate(Somma_Positivi=Sum("Positivi"), Sommae_Negativi=Sum("Negativi"), latest_date=Max('Data')) # Mi ricavo la lista delle misure che sono state giù approvate nel libretto e che l'utente ha diritto a visualizzare e le aggrego per Codice Tariffa in modo da vere il valore totale
        misure_non_aggregate = Misura.objects.filter(Lavoro__in=lavori, Stato="CONFERMATO_LIBRETTO")

        # Sezione dedicata ad aggiungere dei campi alla queryset che contiene le misure aggregate
        Descrizione_Lavori = ""
        for misura in misure_aggregate: # Prendo la lista delle ultime misure per ciascun codice tariffa, così da poter inserire nel template il costo unitario, il nome del lavoro e la descrizione di ciò che è stato fatto
            misura["Lavoro_Nome"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Nome")[0]['Nome']
            misura["Prezzo_Unitario"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Costo_Unitario")[0]['Costo_Unitario']
            misura["Debito"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Debito")[0]['Debito']
            misura["Contratto"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Contratto")[0]['Contratto']
            misura["Contratto_Nome"] = Contratto.objects.filter(id=misura["Contratto"]).values("Nome")[0]['Nome']

            for misura_non_aggregata in misure_non_aggregate:
                if misura_non_aggregata.Codice_Tariffa == misura["Codice_Tariffa"] and misura_non_aggregata.Lavoro.id == misura["Lavoro"]:
                    Descrizione_Lavori += misura_non_aggregata.Designazione_Lavori + "</br>" # Costruisco la descrizione del lavoro fatto concatenando le descrizioni delle singole misure

            misura["Lavoro_Descrizione"] = mark_safe(Descrizione_Lavori) # Trasforma la stringa costruita in html per poterla inserire nel template
            Descrizione_Lavori = ""

        # Calcola il pagamento che dovrà essere effettuato se, approvando le misure elencate, ci sarà uno scatto della soglia corrente
        for contratto in contratti: # Per ogni contratto vediamo la percentuale attuale dei lavori
            lavori_contratto = Lavoro.objects.filter(Contratto=contratto.id) # Prendiamo i lavori del contratto in questione
            num_lavori = lavori_contratto.count() # Li contiamo

            percentuale_parziale = avanza_lavori(request, lavori_contratto, misure_aggregate, False) # Calcola la percentuale senza far avanzare i lavori

            percentuale_totale = percentuale_parziale / num_lavori # Calcoliamo la percentuale del contratto proporzionalmente al numero di lavori
            soglia_da_raggiungere = Soglia.objects.filter(Contratto=contratto.id, Attuale=True).values("Importo_Pagamento", "Percentuale_Da_Raggiungere").order_by("Percentuale_Da_Raggiungere") # Prendiamo le soglie e le ordiniamo in modo da sapere quale è la prossima da raggiungere
            if soglia_da_raggiungere.values("Percentuale_Da_Raggiungere")[0]['Percentuale_Da_Raggiungere'] <= percentuale_totale:
                contratto.Pagamento = soglia_da_raggiungere[0]["Importo_Pagamento"]
                if soglia_da_raggiungere.values("Percentuale_Da_Raggiungere")[0]['Percentuale_Da_Raggiungere'] == 100.0:
                    contratto.Soglia = 100.0
                else:
                    contratto.Soglia = 0
            else:
                contratto.Pagamento = 0
    except:
        misure_aggregate = {}

    # Sezione dedicata all'approvazione delle misure contenute nel registro da parte della stazione
    if request.method == "POST" and misure_aggregate != {}:
        approva = request.POST.get("Approva")

        if approva == "Approva": # Se la stazione clicca sul pulsante di approvazione delle misure, aggiornoo le soglie, le percentuali dei lavori e lo stato delle misure.

            # Se tutto è andato a buon fine, scorro la lista dei contratti per vedere se ci sono dei pagamenti che devono essere effettuati a seguito dell'approvazione delle misure
            # Inoltre aggiorna la soglia che deve essere raggiunta
            pagamenti = ""
            for contratto in contratti:
                if contratto.Pagamento != 0:
                    ## sezione dedicata al lancio della funzione di pagamento in blockchain
                    user = request.user.username
                    account = Web3.toChecksumAddress(request.user.Account)
                    password = request.user.Password_Block
                    contract = Contracts.objects.filter(Username=user, Contract_Type='Appalto')  # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))  # Si connette al nodo per fare il deploy
                    w3.eth.defaultAccount = account  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                    istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                    w3.personal.unlockAccount(account, password, 0)  # Serve per sbloccare l'account prima di poter eseguire le transazioni
                    tx_nuovo_pagamento = istanza_contratto.functions.sendPagamento().transact({'gas': 100000})
                    try:
                        w3.eth.waitForTransactionReceipt(tx_nuovo_pagamento, timeout=20)
                        pagamenti += "Per il contratto " + contratto.Nome + " è stato erogato un pagamento di " + str(contratto.Pagamento) + "€</br></br>"

                        soglia_raggiunta = Soglia.objects.filter(Contratto=contratto.id, Attuale=True).order_by("Percentuale_Da_Raggiungere")[0]  # Prendiamo la soglia raggiunta in modo da aggiornarne lo stato
                        soglia_raggiunta.Attuale = False
                        soglia_raggiunta.save()

                        # Aggiorniamo il debito dei lavori
                        pagamento = contratto.Pagamento
                        lavori_contratto = Lavoro.objects.filter(Contratto=contratto.id) # Prendiamo i lavori del contratto in questione
                        for lavoro in lavori_contratto:
                            debito = lavoro.Debito
                            if debito > 0.0 and pagamento > 0.0: # Vediamo se il debito è maggiore di 0 e se c'è ancora da scalare qualcosa dal pagamento
                                offset = debito - pagamento
                                if offset >= 0.0: # Se il pagamento copre solo una parte del debito lo scalo e poi salvo
                                    lavoro.Debito = offset
                                    pagamento = 0.0
                                else: # Altrimenti scalo al debito parte del pagamento e il resto lo scalerò dal debito di altri lavori
                                    lavoro.Debito = 0.0
                                    pagamento -= debito
                                lavoro.save()

                        avanza_lavori(request, lavori_contratto, misure_aggregate, True)  # Calcola la nuova percentuale di ogni lavoro e la salva su db e in blockchain

                        # Viene creata una notifica da mandare alla ditta
                        utente_ditta = User.objects.get(id=contratto.Ditta)
                        notify.send(request.user, recipient=utente_ditta, actor=request.user, verb='ha effettuato un pagamento di ' + str(contratto.Pagamento) + '€ relativamente al contratto ' + contratto.Nome + ".", nf_type='nuova_notifica')
                    except:
                        pagamenti += "Per il contratto " + contratto.Nome + " il pagamento non è andato a buon fine. </br></br>" # Se non si riesce a mandare la transazione in blockchain allora il pagamento non parte
                    ## fine pagamento in blockchain

                    # Se la soglia raggiunta è 100, vuol dire che il contratto è completo e viene quindi terminato in blockchain.
                    if contratto.Soglia == 100.0:
                        ## sezione dedicata al lancio della funzione che termina un contratto in blockchain
                        user = request.user.username
                        account = Web3.toChecksumAddress(request.user.Account)
                        password = request.user.Password_Block
                        contract = Contracts.objects.filter(Username=user, Contract_Type='Appalto')  # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))  # Si connette al nodo per fare il deploy
                        w3.eth.defaultAccount = account  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                        istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                        w3.personal.unlockAccount(w3.eth.defaultAccount, password, 0)  # Serve per sbloccare l'account prima di poter eseguire le transazioni
                        tx_termina_contratto = istanza_contratto.functions.killContratto().transact({'gas': 100000})
                        try:
                            w3.eth.waitForTransactionReceipt(tx_termina_contratto, timeout=20)
                            contratto.Terminato = True
                            contratto.save()
                            pagamenti = "<p class=\"text-dark text-strong\">Il contratto " + contratto.Nome + " è stato concluso con successo.</p></br></br>" + pagamenti

                            # Viene creata una notifica che indica la fine del contratto per la ditta e il direttore
                            utente_ditta = User.objects.filter(id=contratto.Ditta)
                            utente_direttore = User.objects.filter(id=contratto.Direttore)
                            lista_utenti = utente_ditta | utente_direttore
                            for utente in lista_utenti:
                                notify.send(request.user, recipient=utente, actor=request.user, verb='ha terminato il contratto ' + contratto.Nome + ".", nf_type='nuova_notifica')
                        except:
                            pagamenti += "<p class=\"text-error text-strong\">Non è stato possibile chiudere il contratto</p></br></br>" + pagamenti  # Se non si riesce a mandare la transazione in blockchain allora il contratto non viene ufficialmente chiuso
                        ## fine chiusura in blockchain


            for misura in misure_non_aggregate: # Scorro tutta la lista delle misure e aggiorno lo stato
                stato = misura.Stato
                if stato == "CONFERMATO_LIBRETTO":
                    misura.Stato = "CONFERMATO_REGISTRO"
                    misura.save()

            if pagamenti != "":
                pagamenti = "<div class=\"background-green\"><h3 class=\"text-strong\">Pagamenti Effettuati</h3></br>" + pagamenti + "</div>"
            pagamenti = mark_safe(pagamenti)
            return render(request, "contract_area/registro_cont_redirect.html", {'pagamenti': pagamenti})

    return render(request, "contract_area/registro_cont.html", {'misure_aggregate': misure_aggregate, 'contratti': contratti})

# Vista per il redirect a seguito dell'approvazione delle misure nel registro contabilità

class registrocontredirect(TemplateView):
    template_name = "contract_area/registro_cont_redirect.html"

# Vista per inserire una nuova misura

@login_required
def nuovamisura(request):
    Contratti = Contratto.objects.filter(Direttore=request.user.id) # Prendo la lista dei contratti associati al direttore dei lavori che vuole inserire una misura
    if request.method == "POST":
        response_data = {}  # invieremo con questa variabile la risposta alla chiamata ajax

        contratto = request.POST.get("Contratto")
        misura = request.POST.get("Lavoro")

        ################ FORM 1 ################
        if contratto is not None:
            lavori = Lavoro.objects.filter(Contratto=contratto).values("id", "Nome")

            response_data["lavori"] = list(lavori) # Si passa la lista di lavori che serviranno ad inizializzare la lista del form di inserimento della misura
        else:
            response_data["lavori"] = "Errore"

        ################ FORM 2 ################
        if misura is not None:
            form = librettoForm(request.POST)

            if form.is_valid():
                nuova_misura = form.save(commit=False) # Blocco il salvataggio per poter fare le dovute verifiche

                if nuova_misura.Riserva == "Si": # Se la misura è inserita con la riserva si modifica lo stato
                    nuova_misura.Stato = "INSERITO_LIBRETTO_RISERVA"

                lavoro_associato = Lavoro.objects.filter(id=nuova_misura.Lavoro.id)[0] # Prendo il lavoro associato alla nuova misura
                misure = Misura.objects.filter(Lavoro=nuova_misura.Lavoro.id, Stato__in={"INSERITO_LIBRETTO", "CONFERMATO_LIBRETTO", "CONFERMATO_REGISTRO"}) # Prendo la lista delle misure per il lavoro che stiamo verififcando
                misure_totali = 0 # Mi creo una variabile di appoggio

                for misura in misure:  # Scorro la lista delle misure
                    misure_totali += misura.Positivi  # Mi calcolo il totale delle misure fino ad ora

                misure_totali += nuova_misura.Positivi  # Aggiungo la misura appena inserita dal direttore

                if lavoro_associato.Costo_Unitario == 0.0: # Caso in cui il lavoro si misura in percentuale
                    if misure_totali > 100: # Se con la misura inserita si supera il totale del lavoro, si manda un errore
                        response_data["percentuale"] = "Errore_Percentuale"
                        response_data["percentuale_rimanente"] = 100 - (misure_totali - nuova_misura.Positivi)
                    else:
                        nuova_misura.save()
                        response_data["misura"] = "Successo_2"  # Se la misura inserita è valida si manda l'ok per far inserire una nuova misura o per terminare
                else: # Caso in cui il lavoro si misura in elementi
                    elementi_totali = lavoro_associato.Importo / lavoro_associato.Costo_Unitario # Calcolo il numero totale di elementi misurabili per il lavoro in questione

                    if misure_totali > elementi_totali: # Se con la misura inserita si supera il numero massimo di elementi misurabili, si manda un errore
                        response_data["elementi"] = "Errore_Elementi"
                        response_data["elementi_rimanenti"] = elementi_totali - misure_totali + nuova_misura.Positivi
                    else:
                        nuova_misura.save()
                        response_data["misura"] = "Successo_2"  # Se la misura inserita è valida si manda l'ok per far inserire una nuova misura o per terminare
            else:
                response_data["misura"] = "Errore"
        else:
            response_data["misura"] = "Error2"

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    else:
        form = librettoForm()
    return render(request, 'contract_area/nuova_misura.html', {'form': form, 'contratti': Contratti})

# Vista per il redirect a seguito dell'inserimento di una nuova misura

class nuovamisuraredirect(TemplateView):
    template_name = "contract_area/nuova_misura_redirect.html"

# Vista per il Libretto delle Misure

@login_required
def librettomisure(request):
    if request.user.groups.filter(name="DirettoreLavori").exists():
        contratti = Contratto.objects.filter(Direttore=request.user.id)
    elif request.user.groups.filter(name="DittaAppaltatrice").exists():
        contratti = Contratto.objects.filter(Ditta=request.user.id)
    else:
        contratti = Contratto.objects.filter(Utente=request.user)
    lavori = Lavoro.objects.filter(Contratto__in=contratti)
    misure = Misura.objects.filter(Lavoro__in=lavori) # Ricavo la lista di tutte le misure visualizzabili dall'utente in base alla sua tipologia
    context = {'contratto': "all", 'lavoro': "all", 'stato': "all"} # Creo un context così da inizializzare i menù a tendina per filtrare le misure

    if request.method == "POST":
        approva = request.POST.get("Approva")
        if approva == "Approva": # Se la stazione clicca sul pulsante di approvazione delle misure, scorro tutta la lista delle misure e aggiorno lo stato
            for misura in misure:
                stato = misura.Stato
                if stato == "INSERITO_LIBRETTO":
                    misura.Stato = "CONFERMATO_LIBRETTO"

                    # Sezione che calcola il debito aggiornato che prende in considerazione le ultime misure
                    lavoro = Lavoro.objects.get(id=misura.Lavoro.id) # Prendo il lavoro relativo a questa misura
                    positivi = misura.Positivi # Prendo la quantità misurata
                    costo_unitario = lavoro.Costo_Unitario # Prendo il costo unitario, se esiste per il lavoro in questione
                    importo = lavoro.Importo

                    if costo_unitario == 0.0: # Se il lavoro si misura in percentuale, si calcola in euro quanto vale la misura che la stazione sta approvando
                        aggiunta = (importo * positivi)/100
                    else: # Altrimento si calcola il valore della misura moltiplicando il costo unitario per quanti elementi sono stati misurati
                        aggiunta = costo_unitario * positivi

                    lavoro.Debito += aggiunta
                    lavoro.save()
                    # Fine aggiornamento debito

                    misura.save()
        else:
            # In base alla selezione nei menù a tendina, applico un filtro diverso alla lista delle misure
            lavori_filt = lavori
            contratto = request.POST.get("Contratto")
            if contratto != "all":
                contratti_filt = contratti.filter(id=contratto)
                lavori_filt = Lavoro.objects.filter(Contratto__in=contratti_filt)
                context["contratto"] = contratto
            lavoro = request.POST.get("Lavoro")
            if lavoro != "all":
                lavori_filt = lavori.filter(id=lavoro)
                context["lavoro"] = lavoro
            stato = request.POST.get("Stato")
            misure = Misura.objects.filter(Lavoro__in=lavori_filt)
            if stato != "all":
                misure = misure.filter(Stato=stato)
                context["stato"] = stato

    return render(request, 'contract_area/libretto_misure.html', {'misure': misure, 'contratti': contratti, 'lavori': lavori, 'context': context})

# Vista per un nuovo contratto

@login_required
def nuovocontratto(request):
    if request.method == "POST":
        response_data = {} # invieremo con questa variabile la risposta positiva o negativa dell'inserimento parziale/totale del contratto

        ################ FORM 1 ################
        if request.POST.get("Utente") is not None:
            form = ContrattoForm(request.POST, user=request.user)

            if form.is_valid():
                nuovo_contratto = form.save()
                response_data["msg"] = "Successo_1" # Se il contratto inserito è valido si manda l'ok per mostrare il secondo form
                response_data["contratto"] = nuovo_contratto.pk # Si passa l'id del nuovo contratto per associarci i lavori che inserirà la stazione
            else:
                response_data["msg"] = "Errore_1"
        ################ FORM 2 ################
        elif request.POST.get("Codice_Tariffa") is not None:
            form2 = LavoroForm(request.POST)

            if form2.is_valid():
                nuovo_lavoro = form2.save(commit=False) # Blocco il salvataggio per fare gli opportuni controlli
                importo_tot = Contratto.objects.filter(id=nuovo_lavoro.Contratto.id).values("Importo")[0]['Importo'] # Prendo l'importo totale del contratto. Mi servirà per verificare che la somma degli importi dei lavori è uguale ad esso
                importo_lavori = 0  # Mi creo una variabile di appoggio
                lavori = Lavoro.objects.filter(Contratto=nuovo_lavoro.Contratto.id) # Prendo la lista dei lavori di questo contratto
                codiceripetuto = False # Mi creo una variabile per verificare se per qulche lavoro l'utente ripete erroneamente il codice tariffa

                for lavoro in lavori: # Scorro la lista dei lavori
                    importo_lavori += lavoro.Importo # Sommo gli importi dei singoli lavori
                    if lavoro.Codice_Tariffa == nuovo_lavoro.Codice_Tariffa: # Se il codice tariffa è già stato inserito lo segno con la variabile booleana
                        codiceripetuto = True

                importo_lavori += nuovo_lavoro.Importo # Agli alla somma degli importi dei lavori aggiungo anche l'ultimo lavoro inserito

                if importo_lavori == importo_tot:  # Se la somma degli importi coincide con l'importo totale, termino l'inserimento degli stessi e salvo l'ultimo lavoro
                    response_data["totale"] = "completo"

                if importo_lavori > importo_tot: # Se ho inserito un importo troppo altro, mando un messaggio di errore
                    response_data["importo"] = "Errore_Importo"
                    response_data["importo_attuale"] = str(importo_lavori - nuovo_lavoro.Importo)
                elif codiceripetuto: # Se ho già inserito quel codice tariffa, mando un errore
                    response_data["codice"] = "Errore_Codice"
                else: # Se non ci sono stati errori e se bisogna inserire altri lavori, salvo l'ultimo lavoro
                    nuovo_lavoro.save()

                    ## sezione dedicata all'inserimento di ciascun lavoro in blockchain
                    user = request.user.username
                    account = Web3.toChecksumAddress(request.user.Account)
                    password = request.user.Password_Block
                    contract = Contracts.objects.filter(Username=user, Contract_Type='Appalto') # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))  # Si connette al nodo per fare il deploy
                    w3.eth.defaultAccount = account  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                    istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                    w3.personal.unlockAccount(w3.eth.defaultAccount, password, 0) # Serve per sbloccare l'account prima di poter eseguire le transazioni
                    tx_nuovo_lavoro = istanza_contratto.functions.addLavoro(nuovo_lavoro.Nome).transact({'gas': 100000})
                    try:
                        w3.eth.waitForTransactionReceipt(tx_nuovo_lavoro, timeout=20)
                        response_data["msg"] = "Successo_2"  # Se il lavoro inserito è valido si manda l'ok per far inserire un nuovo lavoro o terminare
                        response_data["contratto"] = nuovo_lavoro.Contratto.pk  # Si ripassa l'id del nuovo contratto per associarci gli altri lavori che inserirà la stazione
                    except:
                        response_data["msg"] = "Errore_Block" # Se non si riesce a mandare la transazione in blockchain allora si ha un errore
                    ## fine lavoro in blockchain

            else:
                response_data["msg"] = "Errore_2"
        ################ FORM 3 ################
        elif request.POST.get("Importo_Pagamento") is not None:
            form3 = SogliaForm(request.POST)
            if form3.is_valid():
                nuova_soglia = form3.save(commit=False) # Blocco il salvataggio della soglia così che posso fare i dovuti controlli
                soglie = Soglia.objects.filter(Contratto=nuova_soglia.Contratto.id) # Mi prendo la lista delle soglie
                importo_contratto = Contratto.objects.filter(id=nuova_soglia.Contratto.id).values("Importo")[0]['Importo'] # Prendo l'importo totale del contratto. Mi servirà per verificare che la somma degli importi delle soglie è uguale ad esso
                importo_soglie = 0 # Mi creo una variabile di appoggio

                for soglia in soglie: # Scorro la lista delle soglie
                    importo_soglie += soglia.Importo_Pagamento # Mi calcolo la somma degli importi delle soglie

                importo_soglie += nuova_soglia.Importo_Pagamento # Aggiungo anche l'importo dell'ultima soglia inserita

                if importo_soglie == importo_contratto:  # Se la somma degli importi delle soglie coincide con il totale, termino l'inserimento delle stesse e salvo l'ultima soglia
                    response_data["totale"] = "completo"

                if importo_soglie > importo_contratto: # Se l'importo delle soglie supera il totale, mando un errore
                    response_data["importo"] = "Errore_Importo"
                    response_data["importo_attuale"] = str(importo_soglie - nuova_soglia.Importo_Pagamento)
                elif nuova_soglia.Percentuale_Da_Raggiungere > 100: # Se la percentuale da raggiungere dell'ultima soglia è maggiore di 100, mando un errore
                    response_data["percentuale"] = "Errore_Percentuale"
                else:
                    nuova_soglia.save()

                    ## sezione dedicata all'inserimento di ciascuna soglia in blockchain
                    user = request.user.username
                    account = Web3.toChecksumAddress(request.user.Account)
                    password = request.user.Password_Block
                    contract = Contracts.objects.filter(Username=user, Contract_Type='Appalto')  # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))  # Si connette al nodo per fare il deploy
                    w3.eth.defaultAccount = account  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                    istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                    w3.personal.unlockAccount(account, password, 0)  # Serve per sbloccare l'account prima di poter eseguire le transazioni
                    tx_nuova_soglia = istanza_contratto.functions.addSoglia(int(nuova_soglia.Importo_Pagamento), int(nuova_soglia.Percentuale_Da_Raggiungere)).transact({'gas': 100000})
                    try:
                        w3.eth.waitForTransactionReceipt(tx_nuova_soglia, timeout=20)
                        response_data["msg"] = "Successo_3"  # Se la soglia inserita è valido si manda l'ok per far inserire una nuova soglia o terminare
                        response_data["contratto"] = nuova_soglia.Contratto.pk  # Si ripassa l'id del nuovo contratto per associarci le altre soglie che inserirà la stazione
                    except:
                        response_data["msg"] = "Errore_Block"  # Se non si riesce a mandare la transazione in blockchain allora si ha un errore
                    ## fine soglia in blockchain

            else:
                response_data["msg"] = "Errore_3"

        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    else:
        form = ContrattoForm(user=request.user) # Crea la form per inserire il contratto
        form2 = LavoroForm() # Crea la form per inserire i lavori
        form3 = SogliaForm() # Crea la form per inserire le soglie
        return render(request, 'contract_area/nuovo_contratto.html', {'form': form, 'form2': form2, 'form3': form3})

# Vista per il redirect a seguito dell'inserimento di un nuovo contratto

class nuovocontrattoredirect(TemplateView):
    template_name = "contract_area/nuovo_contratto_redirect.html"

# Vista predisposta alla creazione e all'inizializzazione di un nuovo insieme di smartcontract

def creacontratto(request):
    if request.method == "POST":
        username = request.user.username # Salviamo l'utente in una variabile. Ci servirà per quando salveremo gli indirizzi dei contratti creati
        # legge i contratti dai relativi file e li compila
        compiled_contracts = compile_files(["." + static("smartrest/contracts/Appalto.sol"), "." + static("smartrest/contracts/Conforme.sol"), "." + static("smartrest/contracts/StringUtils.sol"), "." + static("smartrest/contracts/Valore.sol")])
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:22000")) # Si connette al nodo per fare il deploy
        w3.eth.defaultAccount = w3.eth.accounts[0] # Dice alla libreria web3 che il nodo in questione è quello che farà le transazioni
        JSON_contracts = [] # Variabile che conterrà i dati dei contratti da andare a salvare nel file JSON
        for contract_name, compiled_contract in compiled_contracts.items(): # Facciamo il deploy per ogni contratto
            contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode="0x" + compiled_contract['bin']) # Instanzia il contratto in questione e lo prepara al deploy
            tx_hash = contract.constructor().transact() # Inviamo la transazione al nodo che farà il deploy del contratto. Ritornerà un valore hash
            tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash) # Aspettiamo che la transazione sia minata prima di proseguire e salviamo la risposta
            # Costruiamo il JSON contenente "contratto": "abi-address" di ogni contratto
            JSON_contracts[contract_name] = { # prende abi, name e address di ogni contratto e li mette nel dict JSON_contracts
                "abi": compiled_contract['abi'],
                "contractAddress": tx_receipt["contractAddress"]
            }
        # Costruiamo il JSON he avrà le informazioni relative ai nuovi contratti creati per lo specifico utente
        JSON_to_file = {
            "user": username,
            "contracts": JSON_contracts
        }
        with open(static("smartrest/utils/contracts.json")) as contracts_json: # Dobbiamo leggere il file per aggiugere i nuovi contratti in coda
            data = json.load(contracts_json) # carica il file in una variabile
        data.append(JSON_to_file) # Aggiunge i nuovi contratti in coda alla lista dei contratti che ci sono nel file
        with open(static("smartrest/utils/contracts.json"), 'w') as filejson: # Salva il file contenente anche i nuovi contratti su disco
            json.dump(data, filejson)
        # Qui finisce la parte per deployare i contratti e salvarli, ora bisogna  inizializzarli
        contract_instance = contract_addresses = []
        for contract in JSON_contracts: # scorre i contratti appena deployati
            # per ogni valore del dict JSON_contracts, w3.eth.contract(contractAddress, abi) genera un'istanza del relativo contratto
            contract_instance.append(w3.eth.contract(contract["contractAddress"], contract["abi"])) # Aggiunge al vettore l'istanza del contratto in questione
            contract_addresses.append(contract["contractAddress"]) # Aggiunge al vettore l'indirizzo del contratto in quetione
        # a questo punto bisogna salvare i nuovi contratti sulla blockchain e bisogna salvare i nuovi indirizzi ottenuti
        response = JsonResponse({'status': 'true', 'message': "La creazione dei nuovi contratti è andata a buon fine"})
        return response # Ritorna un messaggio di sucesso qualora la creazione dia andata bene
    else:
        response = JsonResponse({'status': 'false', 'message': "Questo endpoint può essere chiamato solo tramite una request di tipo POST"}, status=500)
        return response # Ritorna un errore se la request non usa il metodo POST

# Vista predisposta alla inizializzazione dei contratti

def setcontratti(request):
    if request.method != "POST":
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # Si connette al nodo per fare il deploy
        w3.eth.defaultAccount = w3.eth.accounts[0]  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
        contracts = Contracts.objects.filter(Username='stazione')
        i = 0
        indirizzi = [0] * 4
        istanze_contratti = [0] * 4
        for contract in contracts:
            indirizzi[i] = contract.Contract_Address
            istanze_contratti[i] = w3.eth.contract(address=contract.Contract_Address,abi=contract.Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
            i = i+1

        w3.personal.unlockAccount(w3.eth.accounts[0], 'smartcontract',0) # Serve per sbloccare l'account prima di poter eseguire le transazioni

        # la seguente sezione setta gli indirizzi per i vari contratti prima di poterli utilizzare

        ###### Appalto ######
        tx_Appalto_1 = istanze_contratti[0].functions.setIndirizzoConforme(indirizzi[1]).transact()
        w3.eth.waitForTransactionReceipt(tx_Appalto_1)
        tx_Appalto_2 = istanze_contratti[0].functions.setIndirizzoValore(indirizzi[3]).transact()
        w3.eth.waitForTransactionReceipt(tx_Appalto_2)

        ###### Valore ######
        tx_Valore_1 = istanze_contratti[3].functions.setIndirizzoAppalto(indirizzi[0]).transact()
        w3.eth.waitForTransactionReceipt(tx_Valore_1)
        tx_Valore_2 = istanze_contratti[3].functions.setIndirizzoConforme(indirizzi[1]).transact()
        w3.eth.waitForTransactionReceipt(tx_Valore_2)

        ###### Conforme ######
        tx_Conforme_1 = istanze_contratti[1].functions.setIndirizzoAppalto(indirizzi[0]).transact()
        w3.eth.waitForTransactionReceipt(tx_Conforme_1)
        tx_Conforme_2 = istanze_contratti[1].functions.setIndirizzoValore(indirizzi[3]).transact()
        w3.eth.waitForTransactionReceipt(tx_Conforme_2)

        return JsonResponse("success",
                            safe=False)
    else:
        response = JsonResponse(
        {'status': 'false', 'message': "Questo endpoint può essere chiamato solo tramite una request di tipo POST"},
        status=500)
        return response  # Ritorna un errore se la request non usa il metodo POST
