import numpy as np


class FiniteStateMachine:

    transition = np.array([['Start', 'Idle', 'Starting'],
                       ['SC', 'Starting', 'Execute'],
                       ['SC', 'Execute', 'Completing'],
                       ['SC', 'Completing', 'Complete'],
                       ['Reset', 'Complete', 'Resetting'],
                       ['Suspend', 'Execute', 'Suspending'],
                       ['SC', 'Suspending', 'Suspended'],
                       ['Unsuspend', 'Suspended', 'Unsuspending'],
                       ['SC', 'Unsuspending', 'Execute'],
                       ['Hold', 'Execute', 'Holding'],
                       ['SC', 'Holding', 'Held'],
                       ['Unhold', 'Held', 'Unholding'],
                       ['SC', 'Unholding', 'Execute'],
                       ['SC', 'Aborting', 'Aborted'],
                       ['Clear', 'Aborted', 'Clearing'],
                       ['SC', 'Clearing', 'Stopped'],
                       ['SC', 'Stopping', 'Stopped'],
                       ['Stop', '*', 'Stopping'],
                       ['Abort', '*', 'Aborting'],
                       ['Reset', 'Stopped', 'Resetting'],
                       ['SC', 'Resetting', 'Idle']])

    states_packml = ['Idle',
                 'Starting',
                 'Execute',
                 'Completing',
                 'Complete',
                 'Resetting',
                 'Unsuspending',
                 'Suspended',
                 'Suspending',
                 'Unholding',
                 'Held',
                 'Holding',
                 'Aborting',
                 'Aborted',
                 'Clearing',
                 'Stopping',
                 'Stopped']
    initial_state = 'Idle'
    state = ''

    def __init__(self, list_states, list_transitions):
        self.transition = list_transitions
        self.states = list_states
        self.state = 'Idle'

    def change_state(self, trigger, from_state, to_state):
        arr = np.array([trigger, from_state, to_state])
        flag = False
        if trigger == 'Stop':
            self.state == 'Stopping'
        if trigger == 'Abort':
            self.state == 'Aborting'
        elif self.state == from_state:
            for row in self.transition:
                if np.array_equal(row, arr):
                    self.state = to_state
                    flag = True
                    print('transition from {} to {} is successful.'.format(from_state, to_state))
            if not flag:
                print('transition from {} to {} is a failure.'.format(from_state, to_state))
        else:
            print('Wrong starting state, transition is impossible')
