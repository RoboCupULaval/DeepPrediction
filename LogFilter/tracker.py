from typing import Dict, List
from itertools import chain

import numpy as np

from multiballservice import MultiBallService
from robot_kalman_filter import RobotFilter


class Tracker:

    MAX_ROBOT_PER_TEAM = 12
    MAX_BALL_ON_FIELD = 1
    MAX_UNDETECTED_DELAY = 1

    def __init__(self):

        self._blue_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._yellow_team = [RobotFilter() for _ in range(Tracker.MAX_ROBOT_PER_TEAM)]
        self._balls = MultiBallService(Tracker.MAX_BALL_ON_FIELD)

        self._current_timestamp = None

    def update(self, detection_frame, t_capture) -> Dict:

        self._current_timestamp = t_capture
        self._update(detection_frame)
        self.remove_undetected()

        return self.track_frame

    def _update(self, detection_frame: Dict):

        for robot_obs in detection_frame.get('robots_blue', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._blue_team[robot_obs['robot_id']].update(obs, self._current_timestamp)

        for robot_obs in detection_frame.get('robots_yellow', ()):
            obs = np.array([robot_obs['x'], robot_obs['y'], robot_obs['orientation']])
            self._yellow_team[robot_obs['robot_id']].update(obs, self._current_timestamp)

        for ball_obs in detection_frame.get('balls', ()):
            obs = np.array([ball_obs['x'], ball_obs['y']])
            self._balls.update(obs, self._current_timestamp)

    def predict(self, t_capture):

        for robot in chain(self._blue_team, self._yellow_team):
            robot.predict(t_capture)

        self._balls.predict(t_capture)

    def remove_undetected(self):
        active_robots = iter(robot for robot in self._yellow_team + self._blue_team if robot.is_active)
        for robot in active_robots:
            if self._current_timestamp - robot.last_update_time > Tracker.MAX_UNDETECTED_DELAY:
                robot.reset()

        self._balls.remove_undetected()

    @property
    def track_frame(self) -> Dict:
        track_fields = dict()
        track_fields['timestamp'] = self._current_timestamp
        track_fields['blue'] = self.blue_team
        track_fields['yellow'] = self.yellow_team
        track_fields['balls'] = self.balls
        return track_fields

    @property
    def balls(self) -> List[Dict]:
        return Tracker.format_list(self._balls, 'x y')

    @property
    def blue_team(self) -> List[Dict]:
        return Tracker.format_list(self._blue_team, 'x y orientation')

    @property
    def yellow_team(self) -> List[Dict]:
        return Tracker.format_list(self._yellow_team, 'x y orientation')

    @staticmethod
    def format_list(entities: List, states) -> List[Dict]:
        formatted_list = []
        for entity_id, entity in enumerate(entities):
            if entity.is_active:
                fields = dict()
                fields['pose'] = {state: value for state, value in zip(states.split(), entity.pose)}
                fields['velocity'] = {state: value for state, value in zip(states.split(), entity.velocity)}
                fields['id'] = entity_id
                formatted_list.append(fields)
        return formatted_list
