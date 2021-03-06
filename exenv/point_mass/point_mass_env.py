import math
import gym
from gym import spaces
import numpy as np
import random

class PointMassEnv(gym.Env):
    def __init__(self, task_id, goal_range=0.5, reward_range=1, terminal_timestep=28, init_random=False):
        self.task_id = task_id
        self.goal_range = goal_range
        self.reward_range = reward_range
        self.terminal_timestep = terminal_timestep
        self.init_random = init_random

        obs = self.reset()
        self.action_high = 1
        self.observation_high = np.max(np.abs(self.goal)) * 3
        self.action_space = spaces.Box(-self.action_high, self.action_high, shape=(2,))
        self.observation_space = spaces.Box(-self.observation_high, self.observation_high, shape=(len(obs),))
    
    def task_id_to_int(self, task_id):
        task_int = np.argmax(np.array(task_id).reshape(1, -1), axis=1)[0]

        return task_int
    
    def set_goal(self, task_id):
        self.task_id = task_id
        self.task_int = self.task_id_to_int(task_id)

        if self.task_int in [0, 4]:
            self.goal = [3.5, 0]
        elif self.task_int in [1, 5]:
            self.goal = [0, 3.5]
        elif self.task_int in [2, 6]:
            self.goal = [-3.5, 0]
        elif self.task_int in [3, 7]:
            self.goal = [0, -3.5]
        else:
            self.goal = [3.5, 0]
    
    def reset(self, task_id=None):
        if task_id is not None:
            self.set_goal(task_id)
        else:
            self.set_goal(self.task_id)

        if self.init_random:
            x = self.goal[0] * random.randint(0, 1) * 2
            y = self.goal[1] * random.randint(0, 1) * 2
        else:
            x = 0
            y = 0

        #x = 7 * random.random() + 2
        #x = 5.5
        #y = 6 * random.random() - 3
        #x = 16 * random.random() - 8
        #y = 16 * random.random() - 8
        #if x >= self.goal[0]-self.reward_range and x <= self.goal[0]+self.reward_range:
        #    x = self.goal[0] - self.reward_range - 0.1 - random.random()
        #if y >= self.goal[1]-self.reward_range and y <= self.goal[1]+self.reward_range:
        #    y = self.goal[1] + self.reward_range + 0.1 + random.random()
        self.position = np.array([x, y], dtype='float32')
        self.observation = self.get_obs()
        self.terminal = False
        self.time_step = 0

        return self.observation
    
    def cal_reward(self, pos):

        diff = self.goal - pos
        dist = np.linalg.norm(diff)
        
        reward = self.reward_range - dist
        if reward < 0: reward = 0

        self.terminal, info = self.check_terminal(pos, dist)

        if self.terminal:
            if dist <= self.goal_range:
                reward = 1000
            else:
                reward = -1000

        return reward, self.terminal, info
    
    def check_terminal(self, pos, dist):
        terminal = False
        info = ""
        if self.time_step >= self.terminal_timestep:
            terminal = True
            info = "time_up"
        elif abs(pos[0]) > self.observation_high or abs(pos[1]) > self.observation_high:
            terminal = True
            info = "out_of_range"
        else:
            if dist <= self.goal_range:
                terminal = True
 
        return terminal, info
    
    def get_obs(self):
        #obs = np.hstack([self.position, self.goal])
        #obs = self.goal - self.position
        obs = self.position
        return obs
    
    def step(self, action):
        self.time_step += 1

        regular_action = np.array(action, dtype='float32')
        regular_action = np.where(regular_action < self.action_high, regular_action, self.action_high)
        regular_action = np.where(regular_action > -self.action_high, regular_action, -self.action_high)

        self.position += regular_action
        self.observation = self.get_obs()
        self.observation = np.where(self.observation < self.observation_high, self.observation, self.observation_high)
        self.observation = np.where(self.observation > -self.observation_high, self.observation, -self.observation_high)

        reward, done, term_info = self.cal_reward(self.position)

        info = {}
        info['position'] = self.position
        info['goal'] = self.goal
        info['terminal'] = term_info

        return self.observation, reward, done, info
    
    def get_info(self):
        info = {}
        info['position'] = self.position
        info['goal'] = self.goal

        return info
    

if __name__=="__main__":
    env = PointMassEnv((0, 0))
    obs = env.reset()
    print(obs)

    done = False
    for _ in range(20):
        obs, reward, done , _ = env.step([0.9, 0])
        print(obs, reward, done)
        if done:
            break
    
    print('end')