#HIP 15 -------------------------------------------------
reward_tx = 0   #Reward for transmitter
reward_rx = 0   #Reward for each receiver

#Witness information will be pulled from nodes
invalid_witnesses = 10
valid_witnesses = 2
witnesses = invalid_witnesses + valid_witnesses

redunacy = 4    #Redundancy is 4, but I can pull this from Helium in case it ever updates
decay_rate = 0.8    #See above

#Eqautions given from HIP15
if (witnesses <= redunacy):
    reward_tx = witnesses / redunacy
    reward_rx = 1
else:
    reward_tx = 1 + (1 - pow(decay_rate, (witnesses - redunacy)))
    reward_rx = (redunacy - (1 - pow(decay_rate, witnesses - redunacy))) / witnesses

if reward_tx > 2:
    reward_tx = 2   #Based off hip_tx_reward_unit_cap

total_rx = reward_rx * valid_witnesses  #Total reward for recievers
tx_scale = valid_witnesses / witnesses  #Used to determine reward for transmitters
total_reward = total_rx + reward_tx * tx_scale  #total rewards calculation
print("Tx reward: ", (reward_tx * tx_scale))
print("Rx reward per witness: ", reward_rx)
print("Total reward: ", total_reward)

#HIP 17
#The following are chain variables that can all be pulled
N = [2,2,2,2,1,1,1] #number of neighboring hex’s that must meet Density_tgt 
density_tgt = [1,1,1,5,25,100,250] #Target number of hotspots in target hex res
density_max = [1,2,4,20,100,400,800] #maximum number of hotspots to consider for target hex res

n = [1,1,1,1,1,1,1] # occupied count (neighbors)
N_miner = [1,1,2,9,21,91,301]    #Needs to be pulled, number of interactive miners in res hex

hex_density_limit = []
hex_transmit_scale = []
for i in range(7):  #loops through res 10-4
    hex_density_limit.append(min(density_tgt[i] * max(n[i] - N[i] + 1,1), density_max[i]))
    hex_transmit_scale.append(min(1, hex_density_limit[i]/N_miner[i]))
    # print(i, ",", hex_density_limit[i])

net_transmit_scale = 1
for i in range (len(hex_transmit_scale)):
    net_transmit_scale *= hex_transmit_scale[i]

print('Transmit scale is: ', net_transmit_scale)


