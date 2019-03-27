# DJANGO IMPORTS
from django.contrib.staticfiles.templatetags.staticfiles import static
# OTHER IMPORTS
import json
from web3 import Web3
from solc import compile_files

# Vista predisposta alla creazione e all'inizializzazione di un nuovo insieme di smartcontract

def creacontratto(request):
    if request.method == "POST":
        user = request.user # Salviamo l'utente in una variabile. Ci servirà per quando salveremo gli indirizzi dei contratti creati
        # legge i contratti dai relativi file e li compila
        compiled_contracts = compile_files([static("smartrest/contracts/Appalto.sol"), static("smartrest/contracts/Conforme.sol"), static("smartrest/contracts/StringUtils.sol"), static("smartrest/contracts/Valore.sol")])
        nodes = ["http://127.0.0.1:22000", "http://127.0.0.1:22001", "http://127.0.0.1:22002"] # Dobbiamo deployare i contratti su tutti e tre i nodi
        for node in nodes:
            w3 = Web3(Web3.HTTPProvider(node)) # Si connette al nodo in questione
            w3.eth.defaultAccount = w3.eth.accounts[0] # Dice alla libreria web3 che il nodo in questione è quello che farà le transazioni for compiled_contract in compiled_contracts:
            for compiled_contract in compiled_contracts: # Facciamo il deploy per ogni contratto
                contract = w3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin']) # Instanzia il contratto in questione e lo prepara al deploy
                tx_hash = contract.constructor().transact() # Inviamo la transazione al nodo che farà il deploy del contratto. Ritornerà un valore hash
                tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash) # Aspettiamo che la transazione sia minata prima di proseguire
                #TODO salvare il contratto nel file JSON
            # prende abi, name e address di ogni contratto e li mette in un vettore
            with open(static("smartrest/utils/contracts.json")) as contracts_json: # Ricordarsi di aggiornare gli address dei contratti nel file
                data = json.load(contracts_json) # carica il file in una variabile
            contract_instance = contract_addresses = []
            for contract in data['contracts']: # scorre i contratti
                # per ogni valore del vettore w3.eth.contract(contractAddress, abi) genera un'istanza del relativo contratto
                contract_instance.append(w3.eth.contract(contract["contractAddress"], contract["abi"])) # Aggiunge al vettore l'istanza del contratto in questione
                contract_addresses.append(contract["contractAddress"]) # Aggiunge al vettore l'indirizzo del contratto in quetione
            # la seguente sezione setta i valori iniziali per i vari contratti prima di poterli salvare
            tx_Appalto_1 = contract_instance[0].functions.setIndirizzoConforme(contract_addresses[1], "{gas: 0x99999}").transact()
            contract_instance[0].functions.setIndirizzoValore(contract_addresses[3], "{gas: 0x99999}").transact()
            contract_instance[1].functions.setIndirizzoAppalto(contract_addresses[0], "{gas: 0x99999}").transact()
            contract_instance[1].functions.setIndirizzoValore(contract_addresses[3], "{gas: 0x99999}").transact()
            contract_instance[3].functions.setIndirizzoAppalto(contract_addresses[0], "{gas: 0x99999}").transact()
            contract_instance[3].functions.setIndirizzoConforme(contract_addresses[1], "{gas: 0x99999}").transact()
            # a questo punto bisogna salvare i nuovi contratti sulla blockchain e bisogna salvare i nuovi indirizzi ottenuti
            w3.eth.waitForTransactionReceipt(tx_Appalto_1)
    else:
        # messaggio di errore json
    return # json