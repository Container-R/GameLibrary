VAR reward_seen = false
EXTERNAL award(event_id, amount)
~ award("bridge.reward.1", 10)
~ reward_seen = true
Reward. # command:reward:bridge.reward.1:10
CMD reward bridge.reward.1 10
-> END
