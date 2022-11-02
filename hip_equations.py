import requests
from pprint import pprint
# import utils
# import h3

# requests.get('https://api.helium.io/v1/vars').json()['data']

#HIP 15 -------------------------------------------------
reward_tx = 0   #Reward for transmitter
reward_rx = 0   #Reward for each receiver

#Witness information will be pulled from nodes
invalid_witnesses = 10
valid_witnesses = 2
witnesses = invalid_witnesses + valid_witnesses

chain_variables = requests.get('https://api.helium.io/v1/vars').json()['data']

redunacy = chain_variables['witness_redundancy']    #Redundancy is 4, but I can pull this from Helium in case it ever updates
decay_rate = chain_variables['poc_reward_decay_rate']    #See above

#Eqautions given from HIP15
if (witnesses <= redunacy):
    reward_tx = witnesses / redunacy
    reward_rx = 1
else:
    reward_tx = 1 + (1 - pow(decay_rate, (witnesses - redunacy)))
    reward_rx = (redunacy - (1 - pow(decay_rate, witnesses - redunacy))) / witnesses

if reward_tx > chain_variables['hip15_tx_reward_unit_cap']:
    reward_tx = chain_variables['hip15_tx_reward_unit_cap']

total_rx = reward_rx * valid_witnesses  #Total reward for recievers
tx_scale = valid_witnesses / witnesses  #Used to determine reward for transmitters
total_reward = total_rx + reward_tx * tx_scale  #total rewards calculation

print("Tx reward: ", (reward_tx * tx_scale))
print("Rx reward per witness: ", reward_rx)
print("Total reward: ", total_reward)

#HIP 17
#The following are chain variables that can all be pulled
N = [chain_variables['hip17_res_10'][0],chain_variables['hip17_res_9'][0],chain_variables['hip17_res_8'][0],
chain_variables['hip17_res_7'][0],chain_variables['hip17_res_6'][0],chain_variables['hip17_res_5'][0],
chain_variables['hip17_res_4'][0]] #number of neighboring hex’s that must meet Density_tgt 
density_tgt = [chain_variables['hip17_res_10'][1],chain_variables['hip17_res_9'][1],chain_variables['hip17_res_8'][1],
chain_variables['hip17_res_7'][1],chain_variables['hip17_res_6'][1],chain_variables['hip17_res_5'][1],
chain_variables['hip17_res_4'][1]] #Target number of hotspots in target hex res
density_max = [chain_variables['hip17_res_10'][2],chain_variables['hip17_res_9'][2],chain_variables['hip17_res_8'][2],
chain_variables['hip17_res_7'][2],chain_variables['hip17_res_6'][2],chain_variables['hip17_res_5'][2],
chain_variables['hip17_res_4'][2]] #maximum number of hotspots to consider for target hex res

n = [1,1,1,1,1,1,1] # occupied count (neighbors)
N_miner = [1,1,2,9,21,91,301]    #Needs to be pulled, number of interactive miners in res hex

hex_density_limit = []
hex_transmit_scale = []
for i in range(7):  #loops through res 10-4
    hex_density_limit.append(min(density_tgt[i] * max(n[i] - N[i] + 1,1), density_max[i]))
    hex_transmit_scale.append(min(1, hex_density_limit[i]/N_miner[i]))

net_transmit_scale = 1
for i in range (len(hex_transmit_scale)):
    net_transmit_scale *= hex_transmit_scale[i]

print('Transmit scale is: ', net_transmit_scale)

HNT_oracle_price = 8
DC_price = 8000000 * 0.00001

DC_transferred_toHNT = DC_price/HNT_oracle_price
Remaining_HNT = 651.0417 - DC_transferred_toHNT

challenge_group = 82.1247
witnesses_group = 328.4989

challenge_group += Remaining_HNT * .2
witnesses_group += Remaining_HNT * .8
# (8,000,000 DC * $0.00001 / $8.00 HNT Oracle Price)
