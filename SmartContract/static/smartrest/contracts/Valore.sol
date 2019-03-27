pragma solidity ^0.5.0;

import "./Conforme.sol";
import "./Appalto.sol";

contract Valore {
    
    Appalto a;
    Conforme c;
    address payable indirizzoAppalto;
    address payable indirizzoConforme;
    
    modifier onlyCommittenza {
        require(
            msg.sender == a.committenza(),
            "Solo il committente pu� utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    }  
    
    modifier onlyDirettoreLavori {
        require(
            msg.sender == a.direttore_lavori(),
            "Solo il direttore dei lavori pu� utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    }  
    
    modifier onlyAppaltoContract {
        require(msg.sender == indirizzoAppalto, "Non puoi eseguire la funzione.");
        _;
    }
    
    //function() external payable {}
    
    function setIndirizzoAppalto (address payable _indirizzo) public{
        indirizzoAppalto = _indirizzo;
        a = Appalto(indirizzoAppalto);
    }
    
    function setIndirizzoConforme (address payable _indirizzo) public{
        indirizzoConforme = _indirizzo;
        c = Conforme(indirizzoConforme);
    }
    
    function calcolaValore() public onlyDirettoreLavori {
        uint256 val = 0; //varaibile in cui salvo la nuova percentuale di completamento ad ogni chiamata 
        for (uint256 i = 0; i < a.numero_lavori(); i++ ) {
            //aggiungo a val solo la percentuale di completamento che non � stata gi� controllata
            (string memory x, uint256 y, uint256 z)=readLavori(i); //y=perc complet, z=perc controllata
            val += (y - z);
            a.setUgualePercentuale(i);
        }
        val = (val/a.numero_lavori()); //supponendo che ogni lavoro abbia stessa complessit�
        a.updateValore(val);
    }
    
    function readLavori (uint256 i) public view returns (string memory, uint256, uint256) {
        (string memory name, uint256 perc_compl, uint256 perc_contr) = a.lavori(i);
        return (name, perc_compl, perc_contr);
    }
    
    function killContratto() public onlyAppaltoContract payable {
        selfdestruct(a.committenza());
    }
}

