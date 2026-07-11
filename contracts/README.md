# Chameleon Token (CHAM) - ERC-20 Smart Contract

## Overview

The Chameleon Token (CHAM) is an ERC-20 compliant token designed for the Chameleon Chain ecosystem. This smart contract includes advanced features for presale management, vesting schedules, and security controls.

## Token Details

- **Name:** Chameleon Token
- **Symbol:** CHAM
- **Decimals:** 18
- **Total Supply:** 1,000,000,000 CHAM (1 billion tokens)
- **Standard:** ERC-20

## Features

### Core ERC-20 Functionality
- ✅ Standard ERC-20 transfer, approve, and transferFrom functions
- ✅ Full compliance with ERC-20 specification
- ✅ Events for all state changes

### Presale Management
- **Multi-Phase Presale:** 4 phases with different pricing
  - Phase 1: $0.08/CHAM - 25M tokens
  - Phase 2: $0.10/CHAM - 25M tokens
  - Phase 3: $0.12/CHAM - 25M tokens
  - Phase 4: $0.15/CHAM - 25M tokens
- **Automatic Token Purchase:** ETH sent to contract automatically buys tokens
- **Phase Control:** Owner can activate/deactivate phases

### Vesting System
- **TGE Unlock:** 25% of purchased tokens unlocked at Token Generation Event
- **Linear Vesting:** Remaining 75% vested linearly over 6 months
- **Claim Function:** Users can claim vested tokens at any time
- **View Functions:** Check releasable amount before claiming

### Security Features
- **Pausable:** Emergency pause for transfers
- **Blacklist:** Prevent malicious addresses from transacting
- **Max Transaction Limit:** Prevent whale dumps
- **Trading Control:** Trading can be enabled/disabled
- **Ownership:** Secure owner-only functions

### Anti-Bot Protection
- Trading disabled until explicitly enabled by owner
- Maximum transaction amount limits (initially 1% of supply)
- Blacklist functionality for identified bad actors

## Smart Contract Architecture

```
ChameleonToken
├── IERC20 (Standard Interface)
├── Ownable (Access Control)
└── Pausable (Emergency Controls)
```

## Contract Functions

### Public Functions

#### `buyTokens()`
Purchase tokens during presale by sending ETH to the contract.

```solidity
function buyTokens() external payable
```

#### `claimVestedTokens()`
Claim all currently vested tokens.

```solidity
function claimVestedTokens() external
```

#### `getReleasableAmount(address beneficiary)`
View how many tokens are currently releasable for an address.

```solidity
function getReleasableAmount(address beneficiary) external view returns (uint256)
```

### Owner Functions

#### `setPresalePhase(uint256 phase)`
Change the active presale phase.

```solidity
function setPresalePhase(uint256 phase) external onlyOwner
```

#### `togglePresale()`
Enable or disable the presale.

```solidity
function togglePresale() external onlyOwner
```

#### `setTGE()`
Set the Token Generation Event timestamp and enable vesting.

```solidity
function setTGE() external onlyOwner
```

#### `enableTrading()`
Enable token trading for all users.

```solidity
function enableTrading() external onlyOwner
```

#### `updateBlacklist(address account, bool status)`
Add or remove an address from the blacklist.

```solidity
function updateBlacklist(address account, bool status) external onlyOwner
```

#### `pause() / unpause()`
Emergency pause/unpause all token transfers.

```solidity
function pause() external onlyOwner
function unpause() external onlyOwner
```

#### `withdrawETH()`
Withdraw collected ETH from presale.

```solidity
function withdrawETH() external onlyOwner
```

## Deployment Instructions

### Prerequisites

1. Install dependencies:
```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

2. Create hardhat.config.js:
```javascript
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {},
    goerli: {
      url: process.env.GOERLI_RPC_URL,
      accounts: [process.env.PRIVATE_KEY]
    },
    mainnet: {
      url: process.env.MAINNET_RPC_URL,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

### Deployment Script

Create `scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const ChameleonToken = await hre.ethers.getContractFactory("ChameleonToken");
  const token = await ChameleonToken.deploy();
  await token.deployed();

  console.log("ChameleonToken deployed to:", token.address);
  
  // Wait for block confirmations
  await token.deployTransaction.wait(5);
  
  // Verify contract
  await hre.run("verify:verify", {
    address: token.address,
    constructorArguments: [],
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

### Deploy to Network

```bash
# Deploy to testnet
npx hardhat run scripts/deploy.js --network goerli

# Deploy to mainnet (after audit)
npx hardhat run scripts/deploy.js --network mainnet
```

## Testing

### Run Tests

```bash
npx hardhat test
```

### Test Coverage

The contract should include tests for:
- ✅ ERC-20 standard compliance
- ✅ Presale functionality
- ✅ Vesting mechanisms
- ✅ Access control
- ✅ Security features
- ✅ Edge cases and error conditions

## Security Considerations

### Pre-Deployment
- [ ] Complete professional security audit
- [ ] Run automated security analysis (Slither, Mythril)
- [ ] Test on testnet with real users
- [ ] Verify all owner functions are protected
- [ ] Ensure no reentrancy vulnerabilities
- [ ] Check for integer overflow/underflow (Solidity 0.8+ has built-in protection)

### Post-Deployment
- [ ] Verify contract on Etherscan
- [ ] Set up monitoring and alerts
- [ ] Establish bug bounty program
- [ ] Document all owner keys and security procedures
- [ ] Consider multi-sig wallet for owner functions
- [ ] Regular security reviews

## Audit Recommendations

### Recommended Auditors
1. **OpenZeppelin** - Industry leader in smart contract security
2. **CertiK** - Comprehensive blockchain security
3. **Trail of Bits** - Expert security researchers

### Audit Checklist
- [ ] Access control verification
- [ ] Reentrancy protection
- [ ] Integer overflow/underflow checks
- [ ] Gas optimization review
- [ ] Logic correctness
- [ ] Edge case handling
- [ ] Emergency procedures

## Gas Optimization

The contract is optimized for gas efficiency:
- Uses `unchecked` blocks where overflow is impossible
- Efficient storage packing
- Minimal external calls
- Batch operations where possible

Estimated gas costs:
- Deploy: ~2,500,000 gas
- Transfer: ~50,000 gas
- Buy tokens: ~120,000 gas
- Claim vested: ~80,000 gas

## Integration Guide

### Web3.js Example

```javascript
const Web3 = require('web3');
const web3 = new Web3('https://mainnet.infura.io/v3/YOUR_KEY');

const contractAddress = '0x...'; // Deployed contract address
const abi = [...]; // Contract ABI

const contract = new web3.eth.Contract(abi, contractAddress);

// Buy tokens
await contract.methods.buyTokens().send({
  from: userAddress,
  value: web3.utils.toWei('1', 'ether')
});

// Check vested amount
const releasable = await contract.methods.getReleasableAmount(userAddress).call();

// Claim tokens
await contract.methods.claimVestedTokens().send({ from: userAddress });
```

### Ethers.js Example

```javascript
const ethers = require('ethers');
const provider = new ethers.providers.JsonRpcProvider('https://mainnet.infura.io/v3/YOUR_KEY');
const signer = provider.getSigner();

const contract = new ethers.Contract(contractAddress, abi, signer);

// Buy tokens
await contract.buyTokens({ value: ethers.utils.parseEther('1.0') });

// Check balance
const balance = await contract.balanceOf(userAddress);

// Claim vested tokens
await contract.claimVestedTokens();
```

## Tokenomics

### Allocation
- 10% - Presale (100M CHAM)
- 15% - Public Sale (150M CHAM)
- 20% - Development (200M CHAM)
- 15% - Team (150M CHAM)
- 10% - Marketing (100M CHAM)
- 15% - Liquidity (150M CHAM)
- 10% - Ecosystem (100M CHAM)
- 5% - Staking Rewards (50M CHAM)

### Vesting Schedule
- **Presale:** 25% at TGE, 75% over 6 months
- **Team:** 12-month cliff, 4-year vesting
- **Development:** 2-year lock, 3-year vesting
- **Marketing:** 25% immediate, 75% over 12 months

## Roadmap

### Phase 1: Token Launch (Q1 2026)
- Deploy token contract
- Complete security audit
- Launch presale

### Phase 2: Exchange Listings (Q2 2026)
- DEX listings (Uniswap, SushiSwap)
- CEX listings (target Tier 1 exchanges)
- Enable trading

### Phase 3: Ecosystem Development (Q3-Q4 2026)
- Launch Chameleon Chain mainnet
- Deploy bridge contracts
- Ecosystem grants program

## Support & Documentation

- **Website:** https://chameleonchain.io
- **Documentation:** https://docs.chameleonchain.io
- **GitHub:** https://github.com/chameleonchain
- **Discord:** https://discord.gg/chameleonchain
- **Telegram:** https://t.me/chameleonchain

## License

MIT License - See LICENSE file for details

## Disclaimer

This smart contract is provided as-is. Users should conduct their own research and due diligence before interacting with any smart contract. Cryptocurrency investments carry risk.

---

**Version:** 1.0.0
**Solidity Version:** ^0.8.20
**Last Updated:** December 2025
