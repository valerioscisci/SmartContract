//// File: `./migrations/2_deploy_contratti.js`

var Appalto = artifacts.require("./Appalto.sol");
var Conforme = artifacts.require("./Conforme.sol");
var Valore = artifacts.require("./Valore.sol");
var StringUtils = artifacts.require("./StringUtils.sol");

module.exports = function(deployer) {
 
deployer.deploy(StringUtils).then(() => {

deployer.link(StringUtils,Appalto);
  return deployer.deploy(Appalto)
});


deployer.deploy(Conforme);

deployer.deploy(Valore);

};