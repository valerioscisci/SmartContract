pragma solidity ^0.5.0;

import "./Valore.sol";
import "./Appalto.sol";

contract Conforme {
    
    Appalto a;
    address payable indirizzoAppalto;
    Valore v;
    address payable indirizzoValore;
    
    //per verificare che un operazione venga fatta nello stato giusto
    modifier onlyStato (Appalto.stato _sta) {
        require(a.sta() == _sta, "L'operazione non pu� essere fatta in questo stato.");
         _;
    }
    
    modifier onlyAppaltoContract () {
        require(msg.sender == indirizzoAppalto, "Non puoi utilizzare la funzione.");
        _;
    }
    
    //constructor () public payable {}
    
    //function () external payable {}
    
    function setIndirizzoAppalto (address payable _indirizzo) public{
        indirizzoAppalto = _indirizzo;
        a = Appalto(indirizzoAppalto);
    }
    
    function setIndirizzoValore (address payable _indirizzo) public{
        indirizzoValore = _indirizzo;
        v = Valore(indirizzoValore);
    }
    
    //richiede che lo stato sia in fase di avanzamento per poter verificare la conformit�
    function checkConformitaLavoro() public onlyStato(Appalto.stato.avanzamento) returns (bool) {
        require (a.numero_lavori() >= 0, "Non � stato inserito alcun lavoro");
        bool conform = true;
        bool[] memory appoggio;
        for (uint256 i = 0; i < a.numero_lavori(); i++ ) {
            delete appoggio;
            appoggio = a.getRequisitiLavoro(i);
            for (uint256 j = 0; j < a.numero_requisiti(); j++) {
                if (!appoggio[j]) {
                    conform=false;
                    if (!conform) {
                        return false;
                    }
                }
            }
        }
        return conform;
    }
    
    function killContratto() public onlyAppaltoContract payable {
        selfdestruct(a.committenza());
    }
}
