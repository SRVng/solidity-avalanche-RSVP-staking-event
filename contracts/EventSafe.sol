// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EventSafe {
    
    //State-Variable
    uint256 private constant fee = 0.1 ether; // 100m gwei
    
    //Mapping
    mapping(address => bool) depositor;
    
    //Function
    function deposit() internal returns(uint256 collateral) {
        require(depositor[msg.sender] == true, "Error: 1");
        bool currency_check = false;
        
        if (msg.value == fee) {
            currency_check = true;
        }
        
        require(currency_check == true, "Please pay 0.1 ETH");
        depositor[msg.sender] = false;
        
        
        return address(this).balance;
    }
    
    function return_collateral(address payable wallet) internal {
        require(wallet == msg.sender, "You cannot withdraw others wallet");
        wallet.transfer(fee);
    }
    
    //Event
    event LogCollateral(string description,address creator);
}

