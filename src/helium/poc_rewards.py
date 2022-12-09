from datetime import datetime
import matplotlib.pyplot as plt 
import numpy as np
import requests
import time

poc_reward_types = ['poc_witnesses', 'poc_challengees']
rewards_by_type = {}
poc_rewards_by_gateway = {}
bone_per_hnt = 100_000_000
num_bins = 100
colors = [
    '#4F7CAC',
    '#C0E0DE',
    '#162521',
    '#3C474B',
    '#9EEFE5',
    '#1B065E',
    '#77CBB9'
]

def fill_rewards_by_type(reward_type: str, amount: float) -> None:
    """Add rewards to corresponding type."""

    if reward_type not in rewards_by_type:
        rewards_by_type[reward_type] = amount 
    else:
        rewards_by_type[reward_type] += amount 
    
    return


def fill_poc_rewards_by_gateway(reward_type: str, gateway: str, amount: float) -> None:
    """Add poc rewards for each gateway."""

    if reward_type == poc_reward_types[0]:
        if gateway not in poc_rewards_by_gateway:
            poc_rewards_by_gateway[gateway] = [amount, 1, 0, amount, 0] 
        else:
            poc_rewards_by_gateway[gateway][0] += amount
            poc_rewards_by_gateway[gateway][3] += amount
    elif reward_type == poc_reward_types[1]:
        if gateway not in poc_rewards_by_gateway:
            poc_rewards_by_gateway[gateway] = [amount, 0, 1, 0, amount] 
        else:
            poc_rewards_by_gateway[gateway][0] += amount
            poc_rewards_by_gateway[gateway][4] += amount
    
    return


def main() -> None:
    """Main. Perform an analysis of rewards for a given epoch."""

    response = requests.get('https://api.helium.io/v1/transactions/_vEtIcW2APKHhK6Vt5IwxgdLuodsXEjLCYff__ibriM')
    response = response.json()['data']['rewards']
    
    hnt_sum = 0
    for transaction in response:
        reward_type = transaction['type']
        amount = transaction['amount'] / bone_per_hnt
        hnt_sum += amount 
        fill_rewards_by_type(reward_type, amount)
        
        if 'gateway' not in transaction: continue
        gateway = transaction['gateway']
        fill_poc_rewards_by_gateway(reward_type, gateway, amount)
    
    for key in rewards_by_type:
        rewards_by_type[key] = (rewards_by_type[key] / hnt_sum) * 100
    
    
    hnt_earned = []
    witness_freq = []
    challenge_freq = []
    poc_freq = []
    challenges = []
    for gateway in poc_rewards_by_gateway:
        total_hnt = poc_rewards_by_gateway[gateway][0]
        witness = poc_rewards_by_gateway[gateway][1]
        challenge = poc_rewards_by_gateway[gateway][2]
        witness_rewards = poc_rewards_by_gateway[gateway][3]
        challenge_rewards = poc_rewards_by_gateway[gateway][4]

        hnt_earned.append(total_hnt)
        witness_freq.append(witness)
        challenge_freq.append(challenge)
        if challenge != 0: 
            challenges.append([gateway, challenge_rewards])
    
    num_challenges = min(300, len(challenges))
    challenges = challenges[:num_challenges]
    payload = {'hotspotIds': [x[0] for x in challenges]}
    r = requests.post('https://etl.hotspotty.org/api/v1/hotspots-lean/', json=payload)
    r = r.json()['data']
    total_ru = []
    for i in range(num_challenges):    
        for h in r:
            if h['id'] == challenges[i][0]:
                total_ru.append((rewards_by_type['poc_challengees'] * 100 * 336 *  h['tru'] * h['rs']) / challenges[i][1])
                
    plt.plot(range(num_challenges), total_ru, '*')
    plt.title('Estimating total rewards units per week by hotspot')
    plt.show()

    plt.hist(witness_freq)
    plt.title('Histogram showing number of hotspots by witness participation')
    plt.xlabel('Number of witnesses participated in during epoch')
    plt.ylabel('Number of hotspots')
    plt.show()

    plt.hist(challenge_freq)
    plt.title('Histogram showing number of hotspots by challenge participation')
    plt.xlabel('Number of challenges participated in during epoch')
    plt.ylabel('Number of hotspots')
    plt.show()

    plt.hist(hnt_earned, bins=num_bins)
    plt.title('Histogram showing number of hotspots vs HNT earned in start epoch 1650363')
    plt.ylabel('Number of hotspots')
    plt.xlabel('HNT earned')
    plt.show()

    plt.bar(rewards_by_type.keys(), rewards_by_type.values(), width=0.4, color=colors)
    plt.title('HNT rewards distribution')
    plt.ylabel('Percentage of HNT distributed')
    plt.xlabel('Rewards types')
    plt.show()
        
if __name__ == '__main__':
    #main()
    pass 


rewards = {}
epochs = 336
block_height = 1650738
for i in  range(epochs):
    print(i , '/', epochs, block_height)
    unique = set()
    rewards_transaction_url = f'https://api.helium.io/v1/blocks/{block_height}/transactions'
    response = requests.get(rewards_transaction_url)
    sleep_time = 1
    while response.status_code != 200:
        time.sleep(sleep_time)
        sleep_time = sleep_time * 2
        response = requests.get(rewards_transaction_url)
    
    response = response.json()['data']
    timestamp = ''
    poc_rewards = []
    for r in response:
        if r['type'] == 'rewards_v2':
            block_height = r['start_epoch'] - 1
            timestamp = datetime.fromtimestamp(r['time']).strftime("%m-%d-%Y")
            poc_rewards = r['rewards']
            if timestamp not in rewards:
                rewards[timestamp] = 0
            for reward in poc_rewards:
                if reward['type'] in poc_reward_types and reward['gateway'] not in unique:
                    rewards[timestamp] += 1
                    unique.add(reward['gateway'])

print(rewards)
days = np.array([x for x in rewards.keys()])
gateways = np.array([x for x in rewards.values()])
idxs = np.argsort(days)
plt.bar(days[idxs], gateways[idxs])
plt.title('Unique number of Hotspots engaging in PoC events by day')
plt.xlabel('Time - days')
plt.ylabel('Number of unique Hotspots')
plt.show()
        
    