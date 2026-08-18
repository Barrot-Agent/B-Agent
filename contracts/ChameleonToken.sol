// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ChameleonToken
 * @dev ERC-20 Token for Chameleon Chain with presale and vesting functionality
 * @author Chameleon Chain Development Team
 */

// Import OpenZeppelin contracts for security and standards compliance
interface IERC20 {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }
}

abstract contract Ownable is Context {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor() {
        _transferOwnership(_msgSender());
    }

    modifier onlyOwner() {
        require(owner() == _msgSender(), "Ownable: caller is not the owner");
        _;
    }

    function owner() public view virtual returns (address) {
        return _owner;
    }

    function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }

    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }

    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

abstract contract Pausable is Context {
    event Paused(address account);
    event Unpaused(address account);

    bool private _paused;

    constructor() {
        _paused = false;
    }

    modifier whenNotPaused() {
        require(!paused(), "Pausable: paused");
        _;
    }

    modifier whenPaused() {
        require(paused(), "Pausable: not paused");
        _;
    }

    function paused() public view virtual returns (bool) {
        return _paused;
    }

    function _pause() internal virtual whenNotPaused {
        _paused = true;
        emit Paused(_msgSender());
    }

    function _unpause() internal virtual whenPaused {
        _paused = false;
        emit Unpaused(_msgSender());
    }
}

contract ChameleonToken is IERC20, Ownable, Pausable {
    // Token details
    string public constant name = "Chameleon Token";
    string public constant symbol = "CHAM";
    uint8 public constant decimals = 18;
    uint256 private constant _totalSupply = 1_000_000_000 * 10**decimals; // 1 billion tokens

    // Balances and allowances
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    // Presale configuration
    struct PresalePhase {
        uint256 price;          // Price per token in wei
        uint256 allocation;     // Total tokens for this phase
        uint256 sold;          // Tokens sold in this phase
        bool active;           // Whether this phase is active
    }

    mapping(uint256 => PresalePhase) public presalePhases;
    uint256 public currentPhase;
    uint256 public totalPresaleAllocation = 100_000_000 * 10**decimals; // 100M tokens for presale
    uint256 public totalPresaleSold;
    bool public presaleActive;

    // Vesting configuration
    struct VestingSchedule {
        uint256 total;              // Total tokens vested
        uint256 released;           // Tokens already released
        uint256 tgeAmount;          // Amount released at TGE (25%)
        uint256 vestingStart;       // Vesting start timestamp
        uint256 vestingDuration;    // Vesting duration in seconds
        bool tgeClaimed;           // Whether TGE tokens have been claimed
    }

    mapping(address => VestingSchedule) public vestingSchedules;
    uint256 public tgeTimestamp; // Token Generation Event timestamp
    
    // Anti-bot and security features
    mapping(address => bool) public isBlacklisted;
    uint256 public maxTransactionAmount;
    uint256 public launchTimestamp;
    bool public tradingEnabled;

    // Events
    event PresalePhaseCreated(uint256 indexed phase, uint256 price, uint256 allocation);
    event TokensPurchased(address indexed buyer, uint256 amount, uint256 cost, uint256 phase);
    event VestingCreated(address indexed beneficiary, uint256 amount);
    event TokensReleased(address indexed beneficiary, uint256 amount);
    event TradingEnabled(uint256 timestamp);
    event BlacklistUpdated(address indexed account, bool status);

    /**
     * @dev Constructor initializes the token with allocations
     */
    constructor() {
        // Mint total supply to contract owner
        _balances[msg.sender] = _totalSupply;
        emit Transfer(address(0), msg.sender, _totalSupply);

        // Initialize presale phases
        _initializePresalePhases();

        // Set max transaction amount (1% of total supply initially)
        maxTransactionAmount = _totalSupply / 100;
        
        // Presale starts as active, trading disabled until TGE
        presaleActive = true;
        tradingEnabled = false;
    }

    /**
     * @dev Initialize presale phases with different pricing
     */
    function _initializePresalePhases() private {
        // Phase 1: $0.08 per token (completed in example)
        presalePhases[1] = PresalePhase({
            price: 0.08 ether / 10, // Adjusted for easier testing
            allocation: 25_000_000 * 10**decimals,
            sold: 0,
            active: false
        });

        // Phase 2: $0.10 per token (active)
        presalePhases[2] = PresalePhase({
            price: 0.10 ether / 10,
            allocation: 25_000_000 * 10**decimals,
            sold: 0,
            active: true
        });

        // Phase 3: $0.12 per token
        presalePhases[3] = PresalePhase({
            price: 0.12 ether / 10,
            allocation: 25_000_000 * 10**decimals,
            sold: 0,
            active: false
        });

        // Phase 4: $0.15 per token
        presalePhases[4] = PresalePhase({
            price: 0.15 ether / 10,
            allocation: 25_000_000 * 10**decimals,
            sold: 0,
            active: false
        });

        currentPhase = 2;
    }

    /**
     * @dev Standard ERC-20 functions
     */
    function totalSupply() external pure override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) external view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) external override whenNotPaused returns (bool) {
        _transfer(_msgSender(), to, amount);
        return true;
    }

    function allowance(address owner, address spender) external view override returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) external override returns (bool) {
        _approve(_msgSender(), spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external override whenNotPaused returns (bool) {
        _spendAllowance(from, _msgSender(), amount);
        _transfer(from, to, amount);
        return true;
    }

    /**
     * @dev Internal transfer function with security checks
     */
    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(amount > 0, "Transfer amount must be greater than zero");
        require(!isBlacklisted[from] && !isBlacklisted[to], "Address is blacklisted");
        
        // Check if trading is enabled (except for owner and presale contract)
        if (!tradingEnabled && from != owner() && to != owner()) {
            require(from == address(this), "Trading not yet enabled");
        }

        // Check max transaction amount (except for owner)
        if (from != owner() && to != owner()) {
            require(amount <= maxTransactionAmount, "Exceeds max transaction amount");
        }

        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
        
        unchecked {
            _balances[from] = fromBalance - amount;
            _balances[to] += amount;
        }

        emit Transfer(from, to, amount);
    }

    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }

    function _spendAllowance(address owner, address spender, uint256 amount) internal {
        uint256 currentAllowance = _allowances[owner][spender];
        if (currentAllowance != type(uint256).max) {
            require(currentAllowance >= amount, "ERC20: insufficient allowance");
            unchecked {
                _approve(owner, spender, currentAllowance - amount);
            }
        }
    }

    /**
     * @dev Presale functions
     */
    function buyTokens() external payable whenNotPaused {
        require(presaleActive, "Presale is not active");
        require(currentPhase > 0 && currentPhase <= 4, "Invalid presale phase");
        
        PresalePhase storage phase = presalePhases[currentPhase];
        require(phase.active, "Current phase is not active");
        require(msg.value > 0, "Must send ETH to buy tokens");

        // Calculate tokens to buy
        uint256 tokenAmount = (msg.value * 10**decimals) / phase.price;
        require(tokenAmount > 0, "Token amount must be greater than zero");
        require(phase.sold + tokenAmount <= phase.allocation, "Phase allocation exceeded");
        require(totalPresaleSold + tokenAmount <= totalPresaleAllocation, "Total presale allocation exceeded");

        // Update phase and total sold
        phase.sold += tokenAmount;
        totalPresaleSold += tokenAmount;

        // Create vesting schedule for buyer
        _createVestingSchedule(_msgSender(), tokenAmount);

        emit TokensPurchased(_msgSender(), tokenAmount, msg.value, currentPhase);
    }

    /**
     * @dev Create vesting schedule for presale participant
     * 25% unlocked at TGE, rest vested over 6 months
     */
    function _createVestingSchedule(address beneficiary, uint256 amount) private {
        VestingSchedule storage schedule = vestingSchedules[beneficiary];
        
        uint256 tgeAmount = amount / 4; // 25% at TGE
        
        schedule.total += amount;
        schedule.tgeAmount += tgeAmount;
        schedule.vestingDuration = 180 days; // 6 months
        
        emit VestingCreated(beneficiary, amount);
    }

    /**
     * @dev Claim vested tokens
     */
    function claimVestedTokens() external whenNotPaused {
        require(tgeTimestamp > 0, "TGE has not occurred yet");
        
        VestingSchedule storage schedule = vestingSchedules[_msgSender()];
        require(schedule.total > 0, "No vesting schedule found");

        // Initialize vesting start if first claim
        if (schedule.vestingStart == 0) {
            schedule.vestingStart = tgeTimestamp;
        }

        uint256 releasable = _calculateReleasableAmount(_msgSender());
        require(releasable > 0, "No tokens available for release");

        // Mark TGE as claimed if applicable
        if (!schedule.tgeClaimed && block.timestamp >= tgeTimestamp) {
            schedule.tgeClaimed = true;
        }

        schedule.released += releasable;
        
        // Transfer tokens from owner to beneficiary
        _transfer(owner(), _msgSender(), releasable);
        
        emit TokensReleased(_msgSender(), releasable);
    }

    /**
     * @dev Calculate releasable amount for an address (does not modify state)
     */
    function _calculateReleasableAmount(address beneficiary) private view returns (uint256) {
        VestingSchedule storage schedule = vestingSchedules[beneficiary];
        
        if (schedule.total == 0) {
            return 0;
        }

        uint256 releasable = 0;
        uint256 vestingStart = schedule.vestingStart > 0 ? schedule.vestingStart : tgeTimestamp;

        // TGE amount (25%)
        if (!schedule.tgeClaimed && block.timestamp >= tgeTimestamp) {
            releasable += schedule.tgeAmount;
        }

        // Vested amount (75% over 6 months)
        if (block.timestamp > vestingStart) {
            uint256 vestedAmount = schedule.total - schedule.tgeAmount;
            uint256 elapsed = block.timestamp - vestingStart;
            
            // Calculate how much has vested so far
            uint256 totalVested;
            if (elapsed >= schedule.vestingDuration) {
                totalVested = vestedAmount;
            } else {
                totalVested = (vestedAmount * elapsed) / schedule.vestingDuration;
            }
            
            // Calculate how much of the vested portion has already been released
            uint256 vestedReleased = 0;
            if (schedule.released > 0) {
                if (schedule.tgeClaimed) {
                    vestedReleased = schedule.released - schedule.tgeAmount;
                }
            }
            
            // Add unreleased vested amount
            if (totalVested > vestedReleased) {
                releasable += totalVested - vestedReleased;
            }
        }

        return releasable;
    }

    /**
     * @dev Get releasable amount for an address (view function)
     */
    function getReleasableAmount(address beneficiary) external view returns (uint256) {
        VestingSchedule storage schedule = vestingSchedules[beneficiary];
        
        if (schedule.total == 0 || tgeTimestamp == 0) {
            return 0;
        }

        uint256 releasable = 0;

        // TGE amount (25%)
        if (!schedule.tgeClaimed && block.timestamp >= tgeTimestamp) {
            releasable += schedule.tgeAmount;
        }

        // Vested amount (75% over 6 months)
        uint256 vestingStart = schedule.vestingStart > 0 ? schedule.vestingStart : tgeTimestamp;

        if (block.timestamp > vestingStart) {
            uint256 vestedAmount = schedule.total - schedule.tgeAmount;
            uint256 elapsed = block.timestamp - vestingStart;
            
            if (elapsed >= schedule.vestingDuration) {
                uint256 alreadyReleased = schedule.tgeClaimed ? schedule.released : 0;
                releasable += vestedAmount - (alreadyReleased > schedule.tgeAmount ? alreadyReleased - schedule.tgeAmount : 0);
            } else {
                uint256 vested = (vestedAmount * elapsed) / schedule.vestingDuration;
                uint256 alreadyReleased = schedule.tgeClaimed ? schedule.released : 0;
                uint256 vestedReleased = alreadyReleased > schedule.tgeAmount ? alreadyReleased - schedule.tgeAmount : 0;
                if (vested > vestedReleased) {
                    releasable += vested - vestedReleased;
                }
            }
        }

        return releasable;
    }

    /**
     * @dev Owner functions
     */
    function setPresalePhase(uint256 phase) external onlyOwner {
        require(phase > 0 && phase <= 4, "Invalid phase");
        
        // Deactivate current phase
        if (currentPhase > 0) {
            presalePhases[currentPhase].active = false;
        }
        
        // Activate new phase
        currentPhase = phase;
        presalePhases[phase].active = true;
        
        emit PresalePhaseCreated(phase, presalePhases[phase].price, presalePhases[phase].allocation);
    }

    function togglePresale() external onlyOwner {
        presaleActive = !presaleActive;
    }

    function setTGE() external onlyOwner {
        require(tgeTimestamp == 0, "TGE already set");
        require(!presaleActive, "Presale must be ended first");
        
        tgeTimestamp = block.timestamp;
        launchTimestamp = block.timestamp;
    }

    function enableTrading() external onlyOwner {
        require(tgeTimestamp > 0, "TGE must be set first");
        tradingEnabled = true;
        emit TradingEnabled(block.timestamp);
    }

    function setMaxTransactionAmount(uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than zero");
        maxTransactionAmount = amount;
    }

    function updateBlacklist(address account, bool status) external onlyOwner {
        isBlacklisted[account] = status;
        emit BlacklistUpdated(account, status);
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function withdrawETH() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No ETH to withdraw");
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "ETH transfer failed");
    }

    /**
     * @dev Receive function to accept ETH for presale
     */
    receive() external payable {
        // Only allow ETH during presale
        require(presaleActive, "Presale is not active");
        require(msg.value > 0, "Must send ETH to buy tokens");
        require(currentPhase > 0 && currentPhase <= 4, "Invalid presale phase");
        
        PresalePhase storage phase = presalePhases[currentPhase];
        require(phase.active, "Current phase is not active");

        // Calculate tokens to buy
        uint256 tokenAmount = (msg.value * 10**decimals) / phase.price;
        require(tokenAmount > 0, "Token amount must be greater than zero");
        require(phase.sold + tokenAmount <= phase.allocation, "Phase allocation exceeded");
        require(totalPresaleSold + tokenAmount <= totalPresaleAllocation, "Total presale allocation exceeded");

        // Update phase and total sold
        phase.sold += tokenAmount;
        totalPresaleSold += tokenAmount;

        // Create vesting schedule for buyer
        _createVestingSchedule(_msgSender(), tokenAmount);

        emit TokensPurchased(_msgSender(), tokenAmount, msg.value, currentPhase);
    }
}
