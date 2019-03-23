// File: `truffle.js`
module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 22000, // was 8545
      network_id: "*", // Match any network id
      gasPrice: 0,
      gas: 4500000
    },
    node2:  {
      host: "127.0.0.1",
      port: 22001,
      network_id: "*", // Match any network id
      gasPrice: 0,
      gas: 4500000
    },
    node3:  {
      host: "127.0.0.1",
      port: 22002,
      network_id: "*", // Match any network id
      gasPrice: 0,
      gas: 4500000
    }
  }
};