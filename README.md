# hddcoin-blockchain
 HDDcoin Blockchain

![Alt text](https://hddcoin.org/wp-content/uploads/2021/07/hdd_coin_logo_website_75.png)

HDDcoin is an eco-friendly blockchain that supports digital money, global payments and applications.

We use the Proof of Space Time consensus pioneered by Chia™, and the powerful and secure Chialisp language for Smart Contracts.

HDDcoin is not affiliated with Chia Network, Inc., but uses their open-sourced software as its foundation.

Securing the blockchain via Proof of Space Time is called farming, and instead of using specialized equipment that uses huge amounts of energy for Proof of Work consensus, the amount of storage on your Hard Disk Drives allocated to HDDcoin secures the Network.



INSTALL INSTRUCTIONS:

***********************************************

**If you are installing for the very first time, please do the following:**
-------------

Install using the binaries available in our [Releases page](https://github.com/HDDcoin-Network/hddcoin-blockchain/releases).


On Linux, you can build from source by pulling from the repository using:

- git clone https://github.com/HDDcoin-Network/hddcoin-blockchain.git


If the client does not find any connections automatically, you can add one of the following:

- dns-introducer.hddcoin.org port 28444 (recommended)
-	node-1.hddcoin.org Port 28444 (fallback)
-	node-2.hddcoin.org Port 28444 (fallback)
-	node-3.hddcoin.org Port 28444 (fallback)


***********************************************

**If you were on the old version, please do the following to get onto the new version:
**
-------------


LINUX INSTRUCTIONS FOR UPDATING TO NEW VERSION

1) Backup your config.yaml file in ~/.hddcoin/mainnet/config
2) Open Terminal and run the following commands:
   cd hddcoin-blockchain
   . ./activate
   hddcoin stop all
   hddcoin stop -d all
   deactivate
3) Delete the ".hddcoin" folder (VERY IMPORTANT -  The update will fail if you miss this step, and you will lose sync)
4) Go back to Terminal and continue running the following commands:
   git fetch
   git checkout main
   git reset --hard FETCH_HEAD
   sh install.sh
   . ./activate
   hddcoin init
5) Restore your config.yaml file back to ~/.hddcoin/mainnet/config
6) Download the latest blockchain database file from http://hddcoin.org/downloads/blockchain_v1_mainnet.sqlite
7) Restore the blockchain database to ~/.hddcoin/mainnet/db
8) Start HDDcoin and verify that you are able to sync, and that you are getting challenges.


-------------


WINDOWS INSTRUCTIONS FOR UPDATING TO NEW VERSION

1) Backup your config.yaml file in %systemdrive%\Users%username%.hddcoin\mainnet\config
2) Close the HDDCoin client and wait for it to fully close. Otherwise click close ("X") on the HDDcoin Clinet window.
3) Navigate back to C:\Users%username%\ and delete the ".hddcoin" folder (VERY IMPORTANT - The update will fail if you miss this step, and you will lose sync)
4) Download and install a fresh copy of HDDcoin from https://github.com/HDDcoin-Network/hddcoin-blockchain/releases (If HDDcoin automatically launches after the install, wait for the login screen, then exit the app)
5) Restore your previously backed up config.yaml file back to %systemdrive%\Users%username%.hddcoin\mainnet\config
6) Download the latest blockchain database file from http://hddcoin.org/downloads/blockchain_v1_mainnet.sqlite
7) Restore the blockchain database to %systemdrive%\Users%username%.hddcoin\mainnet\db
8) Start HDDcoin and verify that you are able to sync, and that you are getting challenges.

--------------
