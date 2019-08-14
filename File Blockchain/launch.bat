start cmd.exe /k geth --datadir ./datadir --networkid 2019 --port 30301 --nodiscover --ipcdisable --rpc --rpcapi "db,personal,eth,net,web3,debug" --rpccorsdomain="*" --rpcaddr="localhost" --rpcport 8545 --allow-insecure-unlock console

start cmd.exe /k geth --datadir ./datadir_new --networkid 2019 --port 30302 --nodiscover --ipcdisable --rpc --rpcapi "db,personal,eth,net,web3,debug" --rpccorsdomain="*" --rpcaddr="localhost" --rpcport 8546 --allow-insecure-unlock console

start cmd.exe /k geth --datadir ./datadir_new2 --networkid 2019 --port 30303 --nodiscover --ipcdisable --rpc --rpcapi "db,personal,eth,net,web3,debug" --rpccorsdomain="*" --rpcaddr="localhost" --rpcport 8547 --allow-insecure-unlock console
