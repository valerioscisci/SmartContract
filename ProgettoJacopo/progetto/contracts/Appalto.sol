pragma solidity ^0.5.0;

import "./Conforme.sol";
import "./Valore.sol";
import "./StringUtils.sol";

contract Appalto {
    using StringUtils for string;
    
    struct Soglia {
        uint256 costo; //prezzo da pagare per ogni soglia
        uint256 percentuale; //percentuale di completamento della soglia
    }
    
    struct RequisitoConformita {
        //int num;
        string nome;
        bool si_no;
    }
    
    struct Lavoro {
        string nome;
        uint256 percentuale_completamento;
        uint256 percentuale_controllata;
        RequisitoConformita[] conformi;
    }
    
    mapping (uint256 => Soglia) soglie;
    mapping (uint256 => RequisitoConformita) requisiti;
    mapping (uint256 => Lavoro) public lavori;
    
    //sono tutte variabili salvate nello storadge del contratto
    uint256 public totale;
    uint256 public valore;
    uint256 public numero_soglie = 0;
    uint256 public soglia_corrente = 0;
    uint256 public numero_requisiti = 0; //numero di requisiti settati inizialmente
    uint256 public numero_lavori = 0;
    
    bool[] public conf;
    
    address payable public committenza;
    address payable public ditta;
    address payable public direttore_lavori;
    
    address payable indirizzoConforme;
    address payable indirizzoValore;
    Conforme c;
    Valore v;

    enum stato {inizio, lavorazione, avanzamento,liquidazione,fine}
    stato public sta;
    
    modifier onlyDirettoreLavori {
        require(
            msg.sender == direttore_lavori,
            "Solo il Direttore dei Lavori pu� utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    } 
    
    modifier onlyCommittenza {
        require(
            msg.sender == committenza,
            "Solo il committente pu� utilizzare questa funzione!"
        );
        _; //indica dove deve essere posta la funzione chiamata
    }  
    
    //per verificare che un operazione venga fatta nello stato giusto
    modifier onlyStato (stato _sta) {
        require(sta == _sta, "L'operazione non pu� essere fatta in questo stato.");
         _;
    }
    
    modifier onlyConformeContract {
        require(msg.sender == indirizzoConforme, "Non puoi modificare lo stato.");
        _;
    }
    
    modifier onlyValoreContract {
        require(msg.sender == indirizzoValore, "Solamente il contratto Valore pu� utilizzare la funzione");
        _;
    }
    
    constructor() public payable {
        totale = 100;
        valore = 0;
        sta = stato.inizio;
        committenza = msg.sender;
        
        //MODIFICA accounts
        ditta=0x1e48E466739ffC526318a0c7CF284A821D5ef566;
        direttore_lavori=0x93AC1AdEF950f31b9e302271F82DF6aDC7934379;
        
        requisiti[0].nome="Materiali innovativi";
        requisiti[0].si_no=false;
        requisiti[1].nome="Qualit� servizio";
        requisiti[1].si_no=false;
        requisiti[2].nome="Risparmio energetico";
        requisiti[2].si_no=false;
        requisiti[3].nome="Normativa sicurezza";
        requisiti[3].si_no=false;
        requisiti[4].nome="Normativa tracciabilit� flussi finanziari";
        requisiti[4].si_no=false;
        requisiti[5].nome="Normativa ambientale";
        requisiti[5].si_no=false;
        requisiti[6].nome="Normativa salute dei lavoratori";
        requisiti[6].si_no=false;
        requisiti[7].nome="Adeguata reportistica";
        requisiti[7].si_no=false;
        requisiti[8].nome="Vincoli architettonici, storicoartistici, conservativi";
        requisiti[8].si_no=false;
        numero_requisiti=9;
    }
    
    function () external payable {} //invia l'ether specificato nel value della transazione al contratto
    
    
    function setIndirizzoConforme (address payable _indirizzo) public {
        indirizzoConforme = _indirizzo;
        c = Conforme(indirizzoConforme);
    }
    
    function setIndirizzoValore (address payable _indirizzo) public {
        indirizzoValore = _indirizzo;
        v = Valore(indirizzoValore);
    }
    
    function addLavoro (string memory _nome) public onlyDirettoreLavori {
        Lavoro storage lavoro = lavori[numero_lavori];
        for (uint256 i = 0; i < numero_lavori; i++) {
            //controllo per impedire di inserire un lavoro precedentemente inserito
            require(
                !StringUtils.equal(lavori[i].nome, _nome) , 
                "E' gi� stato inserito un lavoro con questo nome");
        }
        lavoro.nome = _nome;
        //suppongo che la percentuale_controllata e di completamento sia 0 all'aggiunta di un lavoro
        lavoro.percentuale_completamento = 0;
        lavoro.percentuale_controllata = 0;
        //quando viene aggiunto un lavoro si pongono tutti i requisiti di conformita a false
        setRequisiti(numero_lavori);
        numero_lavori = numero_lavori + 1;
        sta = stato.lavorazione;
    }
    
    //nel caso in cui si voglia implementare un overriding di funzioni,
    //in cui � possibile anche specificare la percentuale di completamento del lavoro
    /*
    function addLavoro (string _nome, uint256 _percentuale_completamento) public onlyDirettoreLavori payable {
        var lavoro = lavori[numero_lavori];
        for (uint256 i = 0; i < numero_lavori; i++) {
            //controllo per impedire di inserire un lavoro precedentemente inserito
            require(
                !StringUtils.equal(lavori[i].nome, _nome) , 
                "E' gi� stato inserito un lavoro con questo nome");
        }
        require(_percentuale_completamento >= 0, "Non pu� essere inserita una percentuale di completamento negativa.");
        require(_percentuale_completamento <= 100, "La percentuale di completamento massima � 100.");
        lavoro.nome = _nome;
        //suppongo che la percentuale_controllata sia 0 all'aggiunta di un lavoro
        //ma la percentuale_completamento pu� non essere nulla nel caso di un lavoro gi� iniziato
        lavoro.percentuale_completamento = _percentuale_completamento;
        lavoro.percentuale_controllata = 0;
        //quando viene aggiunto un lavoro si pongono tutti i requisiti di conformita a false
        setRequisiti(numero_lavori);
        numero_lavori = numero_lavori + 1;
        if (sta!= stato.lavorazione) {
            sta= stato.lavorazione;
        }
    }
    */
    
    function setRequisiti(uint256 i) private {
        lavori[i].conformi.push(requisiti[0]);
        lavori[i].conformi.push(requisiti[1]);
        lavori[i].conformi.push(requisiti[2]);
        lavori[i].conformi.push(requisiti[3]);
        lavori[i].conformi.push(requisiti[4]);
        lavori[i].conformi.push(requisiti[5]);
        lavori[i].conformi.push(requisiti[6]);
        lavori[i].conformi.push(requisiti[7]);
        lavori[i].conformi.push(requisiti[8]);
    }
    
    function addSoglia (uint256 _costo, uint256 _percentuale) public onlyDirettoreLavori {
        require(_costo >= 0, "Non pu� essere inserito un pagamento negativo.");
        require(_percentuale > 0, "Non pu� essere inserita una soglia nulla o negativa.");
        require(_percentuale <= 100, "Non pu� essere inserita una percentuale superiore a 100.");
        Soglia storage soglia = soglie[numero_soglie];
        soglia.costo = _costo;
        soglia.percentuale = _percentuale;
        numero_soglie = numero_soglie + 1;
        sta = stato.lavorazione;
    }
    
    function setUgualePercentuale (uint256 i) public onlyValoreContract {
        lavori[i].percentuale_controllata = lavori[i].percentuale_completamento;
    }
    
    function updateValore (uint256 _valore) public onlyValoreContract {
        valore += _valore;
    }
    
    function checkValore() public onlyDirettoreLavori returns (bool) {
        if (valore < soglie[soglia_corrente].percentuale) {
            return false;
        } else if (valore >= soglie[soglia_corrente].percentuale){
            sta = stato.avanzamento;
            //require((soglia_corrente + 1) <= numero_soglie, "Non ci sono pi� soglie fissate." );
            soglia_corrente = soglia_corrente + 1;
            return true;
        }
    }
    
    function sendPagamento() public payable{
        require (sta == stato.avanzamento, "Non si � ancora arrivati alla soglia prestabilita.");
        require (c.checkConformitaLavoro(), "I lavori non sono tutti conformi.");
        require (msg.sender.balance >= soglie[soglia_corrente - 1].costo, "Non si hanno soglie a sufficienza per il pagamento.");
        ditta.transfer(soglie[soglia_corrente - 1].costo); //-1 perch� con checkValore viene incrementata la soglia corrente
        sta = stato.liquidazione;
    }
    
    function checkRimanente () public onlyStato(stato.liquidazione) returns (bool) {
        if (totale-valore > 0) {
            sta = stato.lavorazione;
            return false;
        } else if (totale-valore == 0) {
            sta = stato.fine;
            killContratto();
            return true;
        }
    }
    
    function ritiraFondi() public onlyCommittenza payable {
        msg.sender.transfer(address(this).balance);
    }
    
    function getBilancio() view public returns (uint256) {
         return address(this).balance;
    }
    
    function updateLavoro (uint256 _numero, uint256 _percentuale_completamento) public onlyDirettoreLavori {
        require(_numero >= 0, "Non esistono lavori con un numero negativo.");
        require(_numero <= numero_lavori, "Non � ancora stato inserito un lavoro con questo numero.");
        require(_percentuale_completamento >= 0, "Non pu� essere inserita una percentuale di completamento negativa.");
        require(_percentuale_completamento <= 100, "Non pu� essere inserita una percentuale_completamento superiore a 100.");
        require(lavori[_numero].percentuale_completamento + _percentuale_completamento <= 100, "La percentuale di completamento inserita porterebbe ad una percentuale superiore al 100%");
        //se il lavoro viene modificato, si deve ricontrollare se sia conforme
        lavori[_numero].percentuale_completamento += _percentuale_completamento;
        setRequisitiFalse(_numero);
        checkValore();
    }
    
    function setRequisitiFalse (uint256 _numero) private onlyDirettoreLavori{
        for (uint256 i = 0; i < numero_requisiti; i++) {
            lavori[_numero].conformi[i].si_no=false;
        }
    }
    
    function setRequisitoConformitaLavoro(uint256 _numerolavoro, bool _zero, bool _uno, bool _due, bool _tre, bool _quattro, bool _cinque, bool _sei, bool _sette, bool _otto) 
    public onlyDirettoreLavori{
        require(sta==stato.avanzamento, "Non si � ancora arrivati alla soglia per poter valutare la conformit�.");
        require(numero_lavori != 0, "Non � ancora stato inserito alcun lavoro.");
        require(_numerolavoro >= 0, "Non esiste un lavoro con questo numero.");
        require(_numerolavoro <= numero_lavori, "Non esiste un lavoro con questo numero.");
        require(_zero == false || _zero == true, "Il secondo campo pu� assumere come valori 0 o 1.");
        require(_uno == false || _uno == true, "Il terzo campo pu� assumere come valori 0 o 1.");
        require(_due == false || _due == true, "Il quarto campo pu� assumere come valori 0 o 1.");
        require(_tre == false || _tre == true, "Il quinto campo pu� assumere come valori 0 o 1.");
        require(_quattro == false || _quattro == true, "Il sesto campo pu� assumere come valori 0 o 1.");
        require(_cinque == false || _cinque == true, "Il settimo campo pu� assumere come valori 0 o 1.");
        require(_sei == false || _sei == true, "Il ottavo campo pu� assumere come valori 0 o 1.");
        require(_sette == false || _sette == true, "Il nono campo pu� assumere come valori 0 o 1.");
        require(_otto == false || _otto == true, "Il decimo campo pu� assumere come valori 0 o 1.");
        
        lavori[_numerolavoro].conformi[0].si_no=_zero;
        lavori[_numerolavoro].conformi[1].si_no=_uno;
        lavori[_numerolavoro].conformi[2].si_no=_due;
        lavori[_numerolavoro].conformi[3].si_no=_tre;
        lavori[_numerolavoro].conformi[4].si_no=_quattro;
        lavori[_numerolavoro].conformi[5].si_no=_cinque;
        lavori[_numerolavoro].conformi[6].si_no=_sei;
        lavori[_numerolavoro].conformi[7].si_no=_sette;
        lavori[_numerolavoro].conformi[8].si_no=_otto;
    }
    
    function getRequisitiLavoro (uint256 _numerolavoro) public returns (bool[] memory) {
        delete conf;
        //conf.length = 0;
        for (uint256 i = 0; i < numero_requisiti; i++) {
            conf.push(lavori[_numerolavoro].conformi[i].si_no);
        }
        return conf;
    }
    
    function killContratto() public payable {
        c.killContratto();
        v.killContratto();
        selfdestruct(committenza);
    }
}






