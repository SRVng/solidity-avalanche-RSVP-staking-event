from tokenize import Token
import brownie, pytest, web3
from brownie import accounts, chain
from brownie.test import given, strategy

w3 = web3.Web3(web3.Web3.HTTPProvider('http://127.0.0.1:8545'))
creator_swap = '1 ether'
creator_stake = 100

def test_staking_one_user_1(accounts, creatorNFT_module_scope, Token_module_scope, RSVP_Event_module_scope, EventCreated):
    addr = accounts[1]
    amount = 300
    Token_module_scope.swap({'from':addr, 'value':'3 ether'})
    assert Token_module_scope.balanceOf(addr) == amount * 1e18

def test_staking_one_user_2(accounts, RSVP_Event_module_scope, EventCreated):
    addr = accounts[1]
    amount = 300
    RSVP_Event_module_scope.RSVP(amount, {'from':addr})
    assert RSVP_Event_module_scope.Stake_Check(addr)[1] == amount
    assert RSVP_Event_module_scope.total_stake()[1] == amount + creator_stake

def test_staking_one_user_3(accounts, RSVP_Event_module_scope, EventCreated):
    addr = accounts[1]
    chain.sleep(30*60)
    assert RSVP_Event_module_scope.total_unclaimed_reward().return_value[0] > 0 and RSVP_Event_module_scope.Reward_Check({'from':addr}).return_value[0] > 0
    total_reward = RSVP_Event_module_scope.total_unclaimed_reward().return_value[0]
    two_addr_reward = RSVP_Event_module_scope.Reward_Check({'from':accounts[0]}).return_value[0] + (RSVP_Event_module_scope.Reward_Check({'from':addr}).return_value[0])
    #decimal problem
    assert (total_reward - two_addr_reward) / 1e18 <= 0.1

def test_staking_one_user_reward_claim(accounts, Token_module_scope, RSVP_Event_module_scope, EventCreated):
    addr = accounts[1]
    chain.sleep(20*60*60 + 30*60) #21 hour passed

    penalty_reward = RSVP_Event_module_scope.Reward_Check({'from':addr}).return_value[1] / 2
    RSVP_Event_module_scope.withdraw_reward({'from':addr})
    assert RSVP_Event_module_scope.Reward_Check({'from':addr}).return_value[0] == 0
    assert (RSVP_Event_module_scope.total_unclaimed_reward().return_value[0] - RSVP_Event_module_scope.Reward_Check({'from':accounts[0]}).return_value[0]) / 1e18 <= 0.1
    assert ((Token_module_scope.balanceOf(addr) / 1e18) - penalty_reward) <= 0.01
    
def test_staking_one_user_check_in(accounts, Token_module_scope, RSVP_Event_module_scope, EventCreated):
    addr = accounts[1]

    chain.sleep(3*60*60) #24 hour passed
    initial_fund_0 = RSVP_Event_module_scope.Stake_Check(accounts[0])[0]
    initial_fund_1 = RSVP_Event_module_scope.Stake_Check(accounts[1])[0] + Token_module_scope.balanceOf(accounts[1])
    reward_0 = RSVP_Event_module_scope.Reward_Check({'from':accounts[0]}).return_value[0]
    reward_1 = RSVP_Event_module_scope.Reward_Check({'from':accounts[1]}).return_value[0]
    assert RSVP_Event_module_scope.total_unclaimed_reward().return_value[0] == (reward_0 + reward_1)
    RSVP_Event_module_scope.Check_in({'from':accounts[0]})
    RSVP_Event_module_scope.Check_in({'from':addr})
    assert Token_module_scope.balanceOf(accounts[0]) == initial_fund_0 + reward_0
    assert Token_module_scope.balanceOf(accounts[1]) == initial_fund_1 + reward_1
    
    for i in range(2):
        with brownie.reverts():
            assert RSVP_Event_module_scope.Stake_Check(accounts[i])[0] == 0
            RSVP_Event_module_scope.Reward_Check({'from':accounts[i]})
            RSVP_Event_module_scope.withdraw_reward({'from':accounts[i]})
            RSVP_Event_module_scope.RSVP(300, {'from':accounts[i]})
            RSVP_Event_module_scope.Check_in({'from':accounts[i]})

def test_staking_one_user_event_end(accounts, RSVP_Event_module_scope, EventCreated):
    initial_balance = w3.eth.get_balance(str(accounts[0]))
    Waiting, Ended = 0, 1
    
    chain.sleep(60*60)
    RSVP_Event_module_scope.RSVP_End(accounts[0])

    assert RSVP_Event_module_scope.event_status() == Ended
    assert RSVP_Event_module_scope.end_time() == 0
    # Assert (balance before end + collateral(0.1)) == (balance after receive the collateral back)
    assert round(float(w3.fromWei(initial_balance, "ether")) + 0.1, 2) == round(float(w3.fromWei(w3.eth.get_balance(str(accounts[0])), "ether")),2)
    

