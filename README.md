# hddcoin-blockchain
 HDDcoin Blockchain

![Alt text](https://hddcoin.org/wp-content/uploads/2021/07/hdd_coin_logo_website_75.png)

HDDcoin is an eco-friendly blockchain that supports digital money, global payments and applications.

We use the Proof of Space Time consensus pioneered by Chia™, and the powerful and secure Chialisp language for Smart Contracts.

HDDcoin is not affiliated with Chia Network, Inc., but uses their open-sourced software as its foundation.

Securing the blockchain via Proof of Space Time is called farming, and instead of using specialized equipment that uses huge amounts of energy for Proof of Work consensus, the amount of storage on your Hard Disk Drives allocated to HDDcoin secures the Network.


***********************************************

**INSTALL INSTRUCTIONS:**

***********************************************

You can build from source or install using the binaries available in our [Releases page](https://github.com/HDDcoin-Network/hddcoin-blockchain/releases).

If the client does not find any connections automatically, you can add any of the following:

- introducer.hddcoin.org / Port: 28444
- dns-introducer.hddcoin.org / Port: 28444
-	node-1.hddcoin.org / Port: 28444
-	node-2.hddcoin.org / Port: 28444


***********************************************

**UPDATE/UPGRADE INSTRUCTIONS:**

***********************************************

You can update from previous version using the binaries available in our [Releases page](https://github.com/HDDcoin-Network/hddcoin-blockchain/releases), or build from source:

```
  cd hddcoin-blockchain
  . ./activate
  hddcoin stop -d all
  deactivate
  git fetch
  git checkout main
  git reset --hard FETCH_HEAD
  sh install.sh
  . ./activate
  hddcoin init
```

**GUI Update**
```
  cd hddcoin-blockchain-gui
  git fetch
  cd ..
  chmod +x ./install-gui.sh
  ./install-gui.sh
```
