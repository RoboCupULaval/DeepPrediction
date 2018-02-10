from tracker import Tracker


class LogFilter:

    def __init__(self, data_json):
        """Robocup SSL game logs filter"""

        # Raw data
        self.data_json = data_json
        self.nb_packets = len(data_json)

        # Filtered data
        self.timestamp = None
        self.current_stage = 'NONE'
        self.current_command = 'NONE'
        self.current_state = None

        # This is where the magic happens
        self.tracker = Tracker()

        self.csv_content = list()

        # Add column headers
        self.csv_content += self._generate_column_headers()

    def apply_filter(self):
        """Loop through all packets and apply the Kalman filter"""

        for n, packet in enumerate(self.data_json):

            # Detection packet
            if packet['message_type'] == 2 and 'detection' in packet['message'].keys():

                detection_frame = packet['message']['detection']

                # Update timestamp
                t_capture = detection_frame['t_capture']
                self.timestamp = t_capture

                # Update the current state
                self.tracker.update(detection_frame, t_capture)
                self.tracker.predict(t_capture)
                self.current_state = self.tracker.track_frame

                # Create a new row
                csv_row = list()

                # Fill the csv row
                self._append_metadata(csv_row)
                self._append_ball(csv_row)
                self._append_teams(csv_row)

                # Add the csv row to the csv_content list
                self.csv_content.append(csv_row)

            # Referee packet
            elif packet['message_type'] == 3:

                # Update the current stage and the current command
                self.current_command = packet['message']['command']
                self.current_stage = packet['message']['stage']

            # Print the number of packets filtered
            if (n + 1) % 1000 == 0:
                print("{} / {} packets processed".format(n + 1, self.nb_packets))

        return self.csv_content

    def _append_metadata(self, csv_row):
        """Append timestamp, current stage and current command"""

        csv_row.append(self.timestamp)
        csv_row.append(self.current_stage)
        csv_row.append(self.current_command)

    def _append_ball(self, csv_row):
        """Append ball information"""

        if self.current_state['balls'] and self.current_state['balls'][0]:
            ball = self.current_state['balls'][0]
            csv_row += [ball['pose']['x'],
                        ball['pose']['y'],
                        ball['velocity']['x'],
                        ball['velocity']['y']]
        else:
            csv_row += [-1] * 4

    def _append_teams(self, csv_row):
        """Append both teams of robots"""

        robots_blue = {robot['id']: robot for robot in self.current_state['blue']}
        robots_yellow = {robot['id']: robot for robot in self.current_state['yellow']}
        self._append_robots(robots_blue, csv_row)
        self._append_robots(robots_yellow, csv_row)

    @staticmethod
    def _append_robots(team, csv_row):
        """Append every possible robots of the given team"""

        for robot_id in range(Tracker.MAX_ROBOT_PER_TEAM):
            if robot_id in team.keys():
                robot = team[robot_id]
                csv_row += [robot['pose']['x'],
                            robot['pose']['y'],
                            robot['pose']['orientation'],
                            robot['velocity']['x'],
                            robot['velocity']['y']]
            else:
                csv_row += [-1] * 5

    @staticmethod
    def _generate_column_headers():
        """Generate 2 headers row for the csv file"""

        header1 = ['', 'Referee', '', 'Ball'] + [''] * 3
        for team_color in ('blue', 'yellow'):
            for robot_id in range(Tracker.MAX_ROBOT_PER_TEAM):
                header1 += ['robot_{}_{}'.format(team_color, robot_id)] + [''] * 4

        header2 = ['timestamp', 'stage', 'command', 'x', 'y', 'v_x', 'v_y'] + \
                  ['x', 'y', 'ori', 'v_x', 'v_y'] * Tracker.MAX_ROBOT_PER_TEAM * 2

        return [header1, header2]
