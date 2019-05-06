# SmartContract
Progetto Ingegneria del Software. Applicazione web che visualizza e modifica SmartContact scritti in una BlockChain

GUIDA PER IMPOSTARE L'AMBIENTE DI SVILUPPO

a) Seguire il file di README del progetto di jacopo per avere gli smartcontract attivi sul proprio pc con i seguenti accorgimenti:</br>
    Le versioni utilizzate sono:</br>
        -Geth: 1.8.12</br>
        -Quorum: 2.2.1</br>
        -Go: 1.9.3</br>
        -Solidity 0.5.0</br>
        -Truffle 5.0.9</br>

    Quando si configura Quorum:
        -al punto 9, se da un errore strano quando si fa vagrant ssh, andare in C:\Users\NomeUtente ed eliminare la cartella .vagrant.d .
            In seguito rieseguire vagrant up
        -al punto 13 eseguire sudo ./istanbul-init.sh invece di ./raft-init.sh
        -al punto 14 eseguire sudo ./istanbul-start.sh invece di ./raft-start.sh
    Una volta eseguito il truffle.cmd migrate i contratti sono stati deployati, possiamo dunque eseguire truffle.cmd networks per sapere gli indirizzi degli stessi

b) Installare python https://www.python.org/downloads/ </br>
    ...

c) Da Terminale:</br>
    pip install django</br>
    pip install web3</br>
    pip install py-solc-x</br>