# hddcoin-blockchain

![Alt text](https://hddcoin.org/images/hdd_coin_logo_website_75.png)

HDDcoin is an eco-friendly blockchain that supports digital money, global payments and applications.

We use the Proof of Space Time consensus pioneered by Chia™, and the powerful and secure Chialisp language for Smart Contracts.

HDDcoin is not affiliated with Chia Network, Inc., but uses their open-sourced software as its foundation.

Securing the blockchain via Proof of Space Time is called farming, and instead of using specialized equipment that uses huge amounts of energy for Proof of Work consensus, the amount of storage on your Hard Disk Drives allocated to HDDcoin secures the Network.

- Website: https://hddcoin.org/
- Discord: https://discord.gg/AZdGSFnqAR
- Twitter: https://twitter.com/hddcoin
- Explorer: https://alltheblocks.net/hddcoin
- Calculator: https://chiaforkscalculator.com/hddcoin
- HDDcoin DB: https://hddcoin.org/downloads/blockchain_v1_mainnet.sqlite
- Launch date: July 8th 2021
- Block Reward: 2 HDD
- Blocks Per Day: 4,608 (halved every 3 years).

***********************************************
**INSTALL INSTRUCTIONS:**
***********************************************

You can install HDDcoin by building from source, or by using the latest binaries for your operating system.

(A.) To **install from available binaries**, download executables from the correct **Releases page**:

   - for pool farming with FoxyPool (OG), get them here ->
   https://github.com/felixbrucker/hddcoin-blockchain/releases
   - for solo farming, get them here ->
   https://github.com/HDDcoin-Network/hddcoin-blockchain/releases


(B.) To **build from source**, do the following:

```
# Update / Upgrade OS

   sudo apt-get update
   sudo apt-get upgrade -y

# Install Git

   sudo apt install git -y

# Checkout the correct source (either for pool or solo farming)

   ## for pool farming with FoxyPool (OG), use this source ## ->
   git clone https://github.com/felixbrucker/hddcoin-blockchain.git

   ## for solo farming, use this source ## ->
   git clone https://github.com/HDDcoin-Network/hddcoin-blockchain.git
   
# Install the Blockchain

   cd hddcoin-blockchain
   sh install.sh
   . ./activate
   hddcoin init

# Install and run the GUI

   sh install-gui.sh
   cd hddcoin-blockchain-gui
   npm run electron &
```

If the client does not find any connections automatically, you can add any of the following:

- introducer.hddcoin.org / Port: 28444
- dns-introducer.hddcoin.org / Port: 28444
- node-1.hddcoin.org / Port: 28444
- node-2.hddcoin.org / Port: 28444


***********************************************
**UPDATE/UPGRADE INSTRUCTIONS:**
***********************************************

You can update HDDcoin from a previous version by downloading and installing the latest executable for your operating system, available from the correct **Releases page**, as described above, or by building from source:

```
# Checkout the source and update

  cd hddcoin-blockchain
  . ./activate
  hddcoin stop -d all
  deactivate
  git fetch
  git checkout main
  git reset --hard FETCH_HEAD --recurse-submodules
  sh install.sh
  . ./activate
  hddcoin init

# Update the GUI

  cd hddcoin-blockchain-gui
  git fetch
  cd ..
  chmod +x ./install-gui.sh
  ./install-gui.sh
```
