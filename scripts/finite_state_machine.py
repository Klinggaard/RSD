import numpy as np

from scripts.MesOrder import MesOrder


class FiniteStateMachine:
    __instance = None   #INITIAL INSTANCE OF CLASS

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

    @staticmethod
    def getInstance():
        """ Static access method. """
        if FiniteStateMachine.__instance == None:
            FiniteStateMachine()
        return FiniteStateMachine.__instance

    def __init__(self, list_states, list_transitions):
        self.transition = list_transitions
        self.states = list_states
        self.state = 'Idle'

        """ Virtually private constructor. """
        if FiniteStateMachine.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            FiniteStateMachine.__instance = self

    def change_state(self, trigger, from_state, to_state):
        arr = np.array([trigger, from_state, to_state])
        flag = False
        if trigger == 'Abort':
            self.state = 'Aborting'
            print('[PackML FSM]: Transition from {} to {} was successful.'.format(from_state, to_state))
        elif trigger == 'Stop':
            self.state = 'Stopping'
            print('[PackML FSM]: Transition from {} to {} was successful.'.format(from_state, to_state))
        elif self.state == from_state:
            for row in self.transition:
                if np.array_equal(row, arr):
                    self.state = to_state
                    flag = True
                    MesOrder().log_state(self.state)
                    print('[PackML FSM]: Transition from {} to {} is successful.'.format(from_state, to_state))
            if not flag:
                print('[PackML FSM]: Transition from {} to {} failed.'.format(from_state, to_state))
        else:
            print('Wrong starting state, transition is impossible')
