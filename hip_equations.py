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
print("Total reward: ", total_reward)

#HIP 17
density_tgt = 1
density_max = 4

N = 2
for n in range(8):
    hex_density_limit = min(density_tgt * max(n - N + 1,1), density_max)
    print(n, ",", hex_density_limit*100)

# occupied_count


