# DJANGO IMPORTS
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import JsonResponse
# MODELS IMPORTS
from .models import Contracts
# FORMS IMPORTS
from .forms import librettoForm, ContrattoForm
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

# Vista per lo Stato Avanzamento Lavori

class statoavanzamento(TemplateView):
    template_name = "contract_area/stato_avanzamento.html"

# Vista per il Registro Contabilità

class registrocont(TemplateView):
    template_name = "contract_area/registro_cont.html"

# Vista per il Giornale dei Lavori

class giornalelavori(TemplateView):
    template_name = "contract_area/giornale_lavori.html"

# Vista per il Libretto delle Misure

def librettomisure(request):
    if request.method == "POST":
        template_name = "contract_area/libretto_misure.html"
    else:
        form = librettoForm()
    return render(request, 'contract_area/libretto_misure.html', {'form': form})

# Vista per il Libretto delle Misure

def nuovocontratto(request):
    if request.method == "POST":
        template_name = "contract_area/nuovo_contratto.html"
    else:
        form = ContrattoForm()
    return render(request, 'contract_area/nuovo_contratto.html', {'form': form})

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
        w3.eth.defaultAccount = w3.eth.accounts[0]  # Dice alla libreria web3 che l'acount della stazione è quello che farà le transazioni
        contracts = Contracts.objects.filter(Username='stazione')
        i = 0
        indirizzi = [0] * 4
        istanze_contratti = [0] * 4
        for contract in contracts:
            indirizzi[i] = contract.Contract_Address
            istanze_contratti[i] = w3.eth.contract(address=contract.Contract_Address,abi=contract.Contract_Abi.Abi_Value)  # Cre un'istanza del contratto per porte eseguire i metodi
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
        #    contract_instance[0].functions.setIndirizzoValore(contract_addresses[3], "{gas: 0x99999}").transact()
    else:
        response = JsonResponse(
        {'status': 'false', 'message': "Questo endpoint può essere chiamato solo tramite una request di tipo POST"},
        status=500)
        return response  # Ritorna un errore se la request non usa il metodo POST
