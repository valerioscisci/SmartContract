pragma solidity ^0.5.0;

import "./Conforme.sol";
import "./Valore.sol";
import "./StringUtils.sol";

contract Misure{

     using StringUtils for string;

      struct misurazioni {     //Andiamo a definire un'insieme di misurazioni associate ad un lavoro
        string nome;
        uint256 misura_completata;
        uint256 misura_controllata;
    }

    //TODO metodo AddMisura che permette di inserire all'interno della BlockChain (bisogna capire come collegare la misura al lavoro)
    


    mapping (uint256 => Lavoro) public lavori;









}