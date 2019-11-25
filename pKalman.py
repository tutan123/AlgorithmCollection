from pykalman import KalmanFilter
import numpy as np
from scipy.stats import norm
# kf = KalmanFilter(transition_matrices=[[1,1], [0,1]], observation_matrices=[[0.1, 0.5], [-0.3, 0.0]])
# measurements = np.array([[1,0],[0,0],[0,1]])
# kf = kf.em(measurements, n_iter=5)
# (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
# (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)

# kf = KalmanFilter(initial_state_mean=0, n_dim_obs=2)
# measurements = [[1,0],[0,0],[0,1]]
# print(kf.em(measurements).smooth([[2,0],[2,1],[2,2]])[0])
me = np.random.normal()
states = np.zeros((n_timesteps, n_dim_state))
