from rlcard import make
from rlcard.agents import DQNAgent
from rlcard.models.limitholdem_rule_models import LimitholdemRuleAgentV1
from rlcard.utils import get_device, reorganize, Logger, tournament, plot_curve, set_seed
import random
import torch
import os

set_seed(100)
num_players = 4
num_episodes = 1
log_dir = "/models/dqn5/"
evaluate_every = 500
num_eval_games = 1000
algorithm = "dqn"
device = get_device()
env = make('limit-holdem', config={'game_num_players': num_players, "seed": 0})
dqnagent_train = DQNAgent(num_actions=env.num_actions)
dqnagent = dqnagent_train
# Start training
with Logger(log_dir) as logger:
    for episode in range(num_episodes):
        # Set agents for the episode
        env.set_agents([dqnagent, dqnagent, dqnagent, dqnagent_train])

        # Generate data from the environment
        trajectories, payoffs = env.run(is_training=True)
        trajectories = reorganize(trajectories, payoffs)

        # Train the DQN agent with the generated data
        for ts in trajectories[3]:
            dqnagent_train.feed(ts)

        # Evaluate the performance
        if episode % evaluate_every == 0:
            dqnagent = dqnagent_train
            logger.log_performance(episode,
                                   tournament(
                                       env,
                                       num_eval_games,
                                   )[0])
    csv_path, fig_path = logger.csv_path, logger.fig_path
# Plot the learning curve
plot_curve(csv_path, fig_path, algorithm)
# Save model
save_path = os.path.join(log_dir, 'model.pth')
torch.save(dqnagent_train, save_path)
print('Model saved in', save_path)
