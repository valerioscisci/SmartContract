pragma solidity ^0.4.15;

import "./Conforme.sol";
import "./Appalto.sol";

contract Valore {
    
    Appalto a;
    Conforme c;
    address indirizzoAppalto;
    address indirizzoConforme;
    
    modifier onlyCommittenza {
        require(
            msg.sender == a.committenza(),
            "Solo il committente può utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    }  
    
    modifier onlyDirettoreLavori {
        require(
            msg.sender == a.direttore_lavori(),
            "Solo il direttore dei lavori può utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    }  
    
    modifier onlyAppaltoContract {
        require(msg.sender == indirizzoAppalto, "Non puoi eseguire la funzione.");
        _;
    }
    
    //function() external payable {}
    
    function setIndirizzoAppalto (address _indirizzo) {
        indirizzoAppalto = _indirizzo;
        a = Appalto(indirizzoAppalto);
    }
    
    function setIndirizzoConforme (address _indirizzo) {
        indirizzoConforme = _indirizzo;
        c = Conforme(indirizzoConforme);
    }
    
    function calcolaValore() public onlyDirettoreLavori {
        uint256 val = 0; //varaibile in cui salvo la nuova percentuale di completamento ad ogni chiamata 
        for (uint256 i = 0; i < a.numero_lavori(); i++ ) {
            //aggiungo a val solo la percentuale di completamento che non è stata già controllata
            var (x,y,z)=readLavori(i); //y=perc complet, z=perc controllata
            val += (y - z);
            a.setUgualePercentuale(i);
        }
        val = (val/a.numero_lavori()); //supponendo che ogni lavoro abbia stessa complessità
        a.updateValore(val);
    }
    
    function readLavori (uint256 i) public constant returns (string, uint256, uint256) {
        var (name, perc_compl, perc_contr) = a.lavori(i);
        return (name, perc_compl, perc_contr);
    }
    
    function killContratto() public onlyAppaltoContract payable {
        selfdestruct(a.committenza());
    }
}

