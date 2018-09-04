import random

with open('test/user-agents.txt', 'r', encoding = 'utf-8') as f:
    list_user_agents = f.readlines()
    user_agent = random.choice(list_user_agents).strip()
    print(user_agent)
headers = {'user-agent':user_agent}
print(headers)

