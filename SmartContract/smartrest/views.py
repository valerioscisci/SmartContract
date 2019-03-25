from django.shortcuts import render

# Vista predisposta alla creazione e all'inizializzazione di un nuovo smartcontract

def creacontratto(request):
    if request.method == "POST":
        # prende abi, name e address di ogni contratto e li mette in un vettore
        # per ogni valore del vettore web3.eth.contract(contractAddress, abi=abi) genere un'istanza del contratto
        # salvare l'istanza del contratto
        # settare i valori iniziali
    else:
        # messaggio di errore json
    return # json