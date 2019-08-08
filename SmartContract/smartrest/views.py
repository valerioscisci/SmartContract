# DJANGO IMPORTS
from django.db.models import Sum, Max
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import JsonResponse, HttpResponse
# MODELS IMPORTS
from .models import Contracts, Contratto, Lavoro, Misura, Soglia
# FORMS IMPORTS
from .forms import librettoForm, ContrattoForm, LavoroForm, SogliaForm
# OTHER IMPORTS
import json
from web3 import Web3
from solcx import compile_files

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

# Vista per il Giornale dei Lavori

def giornalelavori(request):
    return render(request, "contract_area/giornale_lavori.html")

# Vista per lo Stato Avanzamento Lavori

def statoavanzamento(request):
    return render(request, "contract_area/stato_avanzamento.html")


def registerform(request):
    return render(request, "registration/register.html")



# Vista per il Registro Contabilità

def registrocont(request):
    if request.user.groups.filter(name="DirettoreLavori").exists():
        contratti = Contratto.objects.filter(Direttore=request.user.id)
    elif request.user.groups.filter(name="DittaAppaltatrice").exists():
        contratti = Contratto.objects.filter(Ditta=request.user.id)
    else:
        contratti = Contratto.objects.filter(Utente=request.user)
    lavori = Lavoro.objects.filter(Contratto__in=contratti)
    misure_aggregate = Misura.objects.filter(Lavoro__in=lavori, Stato="CONFERMATO_LIBRETTO").values("Codice_Tariffa", "Lavoro").annotate(Somma_Positivi=Sum("Positivi"), Sommae_Negativi=Sum("Negativi"), latest_date=Max('Data')) # Mi ricavo la lista delle misure che sono state giù approvate nel libretto e che l'utente ha diritto a visualizzare e le aggrego per Codice Tariffa in modo da vere il valore totale
    misure_non_aggregate = Misura.objects.filter(Lavoro__in=lavori, Stato="CONFERMATO_LIBRETTO")

    Descrizione_Lavori = ""
    for misura in misure_aggregate: # Prendo la lista delle ultime misure per ciascun codice tariffa, così da poter inserire nel template il costo unitario, il nome del lavoro e la descrizione di ciò che è stato fatto
        misura["Lavoro_Nome"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Nome")[0]['Nome']
        misura["Prezzo_Unitario"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Costo_Unitario")[0]['Costo_Unitario']
        misura["Debito"] = Lavoro.objects.filter(id=misura["Lavoro"]).values("Debito")[0]['Debito']

        for misura_non_aggregata in misure_non_aggregate:
            if misura_non_aggregata.Codice_Tariffa == misura["Codice_Tariffa"] and misura_non_aggregata.Lavoro.id == misura["Lavoro"]:
                Descrizione_Lavori += misura_non_aggregata.Designazione_Lavori + "</br>" # Costruisco la descrizione del lavoro fatto concatenando le descrizioni delle singole misure
        misura["Lavoro_Descrizione"] = mark_safe(Descrizione_Lavori) # Trasforma la stringa costruita in html per poterla inserire nel template
        Descrizione_Lavori = ""
    pagamento = "quanto la stazione pagherà alla conferma delle misure" # Bisogna calcolarlo andando a verificare che con le misure aggiunte ci sia il superamento della soglia e verificare di quanto sarà il pagamento

    # Sezione dedicata all'approvazione delle misure contenute nel registro da parte della stazione
    if request.method == "POST":
        approva = request.POST.get("Approva")
        if approva == "Approva": # Se la stazione clicca sul pulsante di approvazione delle misure, scorro tutta la lista delle misure e aggiorno lo stato
            for misura in misure_non_aggregate:
                stato = misura.Stato
                if stato == "CONFERMATO_LIBRETTO":
                    misura.Stato = "CONFERMATO_REGISTRO"
                    misura.save()
        # Se tutto è andato a buon fine far partire il pagamento e inviare la notifica alla ditta
        return redirect("registro_contabilita_redirect")

    return render(request, "contract_area/registro_cont.html", {'misure_aggregate': misure_aggregate, 'pagamento': pagamento})

# Vista per il redirect a seguito dell'approvazione delle misure nel registro contabilità

class registrocontredirect(TemplateView):
    template_name = "contract_area/registro_cont_redirect.html"

# Vista per inserire una nuova misura

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
                nuova_misura = form.save(commit=False)
                nuova_misura.Codice_Tariffa = nuova_misura.Lavoro.Codice_Tariffa
                if nuova_misura.Riserva == "Si":
                    nuova_misura.Stato = "INSERITO_LIBRETTO_RISERVA"
                nuova_misura.save()
                response_data["misura"] = "Successo_2" # Se la misura inserita è valida si manda l'ok per far inserire una nuova misura o per terminare
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

    return render(request, 'contract_area/libretto_misure.html', {'misure': misure, 'contratti': contratti, 'lavori': lavori, 'context':context})

# Vista per un nuovo contratto

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
                nuovo_lavoro = form2.save()

                ## sezione dedicata all'inserimento di ciascun lavoro in blockchain
                contract = Contracts.objects.filter(Username='stazione', Contract_Type='Appalto') # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # Si connette al nodo per fare il deploy
                w3.eth.defaultAccount = w3.eth.accounts[0]  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                w3.personal.unlockAccount(w3.eth.accounts[0], 'smartcontract',0) # Serve per sbloccare l'account prima di poter eseguire le transazioni
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
            response_data["test"]=request.POST.get("Importo_Pagamento")
            if form3.is_valid():
                nuova_soglia = form3.save()

                ## sezione dedicata all'inserimento di ciascuna soglia in blockchain
                contract = Contracts.objects.filter(Username='stazione', Contract_Type='Appalto')  # Seleziona il contratto così da poter crearne un'istanza e poter lanciare le sue funzioni
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # Si connette al nodo per fare il deploy
                w3.eth.defaultAccount = w3.eth.accounts[0]  # Dice alla libreria web3 che l'account della stazione è quello che farà le transazioni
                istanza_contratto = w3.eth.contract(address=contract[0].Contract_Address, abi=contract[0].Contract_Abi.Abi_Value)  # Crea un'istanza del contratto per porte eseguire i metodi
                w3.personal.unlockAccount(w3.eth.accounts[0], 'smartcontract',0)  # Serve per sbloccare l'account prima di poter eseguire le transazioni
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
