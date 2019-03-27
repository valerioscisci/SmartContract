# SmartContract
Progetto Ingegneria del Software. Applicazione web che visualizza e modifica SmartContact scritti in una BlockChain

GUIDA PER IMPOSTARE L'AMBIENTE DI SVILUPPO__

a) Seguire il file di README del progetto di jacopo per avere gli smartcontract attivi sul proprio pc con i seguenti accorgimenti:
    Le versioni utilizzate sono:
        -Geth: 1.8.12
        -Quorum: 2.2.1
        -Go: 1.9.3
        -Solidity 0.5.0
        -Truffle 5.0.9

    Quando si configura Quorum:
        -al punto 9, se da un errore strano quando si fa vagrant ssh, andare in C:\Users\NomeUtente ed eliminare la cartella .vagrant.d .
            In seguito rieseguire vagrant up
        -al punto 13 eseguire sudo ./istanbul-init.sh invece di ./raft-init.sh
        -al punto 14 eseguire sudo ./istanbul-start.sh invece di ./raft-start.sh
    Una volta eseguito il truffle.cmd migrate i contratti sono stati deployati, possiamo dunque eseguire truffle.cmd networks per sapere gli indirizzi degli stessi

b) Installare python https://www.python.org/downloads/__ 
    ...

c) Da Terminale:
    npm install -g solc
    pip install django
    pip install web3
    pip install py-solc