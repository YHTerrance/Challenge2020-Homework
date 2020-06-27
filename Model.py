import random

import pygame as pg

from datetime import datetime
from EventManager import *
import Const


class StateMachine(object):
    '''
    Manages a stack based state machine.
    peek(), pop() and push() perform as traditionally expected.
    peeking and popping an empty stack returns None.
    '''
    def __init__(self):
        self.statestack = []

    def peek(self):
        '''
        Returns the current state without altering the stack.
        Returns None if the stack is empty.
        '''
        try:
            return self.statestack[-1]
        except IndexError:
            # empty stack
            return None

    def pop(self):
        '''
        Returns the current state and remove it from the stack.
        Returns None if the stack is empty.
        '''
        try:
            return self.statestack.pop()
        except IndexError:
            # empty stack
            return None

    def push(self, state):
        '''
        Push a new state onto the stack.
        Returns the pushed value.
        '''
        self.statestack.append(state)
        return state

    def clear(self):
        '''
        Clear the stack.
        '''
        self.statestack = []


class GameEngine:
    '''
    The main game engine. The main loop of the game is in GameEngine.run()
    '''

    def __init__(self, ev_manager: EventManager):
        '''
        This function is called when the GameEngine is created.
        For more specific objects related to a game instance
            , they should be initialized in GameEngine.initialize()
        '''
        self.ev_manager = ev_manager
        ev_manager.register_listener(self)
        self.state_machine = StateMachine()

    def initialize(self):
        '''
        This method is called when a new game is instantiated.
        '''
        self.clock = pg.time.Clock()
        self.state_machine.push(Const.STATE_MENU)
        self.players = [Player(0), Player(1)]

    def notify(self, event: BaseEvent):
        '''
        Called by EventManager when a event occurs.
        '''
        if isinstance(event, EventInitialize):
            self.initialize()

        elif isinstance(event, EventEveryTick):
            cur_state = self.state_machine.peek()
            if cur_state == Const.STATE_MENU:
                self.update_menu()
            elif cur_state == Const.STATE_PLAY:
                self.update_objects()
                self.timer -= 1
                self.round_timer -= 1
                
                if self.timer == 0:
                    self.ev_manager.post(EventTimesUp())

                if self.round_timer == 0:
                    self.round_timer = Const.ROUND_LENGTH
                    self.switch_roles()

            elif cur_state == Const.STATE_ENDGAME:
                self.update_endgame()
            

        elif isinstance(event, EventStateChange):
            if event.state == Const.STATE_POP:
                if self.state_machine.pop() is None:
                    self.ev_manager.post(EventQuit())
            else:
                self.state_machine.push(event.state)

        elif isinstance(event, EventQuit):
            self.running = False

        elif isinstance(event, EventPlayerMove):
            self.players[event.player_id].move_direction(event.direction)

        elif isinstance(event, EventTimesUp):
            self.state_machine.push(Const.STATE_ENDGAME)

    def update_menu(self):
        '''
        Update the objects in welcome scene.
        For example: game title, hint text
        '''
        pass

    def update_objects(self):
        '''
        Update the objects not controlled by user.
        For example: obstacles, items, special effects
        '''
        pass

    def update_endgame(self):
        '''
        Update the objects in endgame scene.
        For example: scoreboard
        '''
        pass
    def switch_roles(self):
        for player in self.players:
            player.role = (player.role + 1) % 2
            player.speed = Const.SPEED_ATTACK if player.role == 1 else Const.SPEED_DEFENSE

    def distance_between_players(self):
        return (self.players[0].position.x - self.players[1].position.x) ** 2 + (self.players[0].position.y - self.players[1].position.y) ** 2

    def run(self):
        '''
        The main loop of the game is in this function.
        This function activates the GameEngine.
        '''
        self.running = True
        self.ev_manager.post(EventInitialize())
        self.timer = Const.GAME_LENGTH
        self.round_timer = Const.ROUND_LENGTH
        while self.running:
            self.ev_manager.post(EventEveryTick())
            self.clock.tick(Const.FPS)
            if self.distance_between_players() <= (2 * Const.PLAYER_RADIUS) ** 2:
                self.players[0].reset_position_speed()
                self.players[1].reset_position_speed()
            

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.role = player_id
        self.position = pg.Vector2(Const.PLAYER_INIT_POSITION[player_id]) # is a pg.Vector2
        self.speed = Const.SPEED_ATTACK if self.role == 1 else Const.SPEED_DEFENSE
    
    def reset_position_speed(self):
        self.position = pg.Vector2(Const.PLAYER_INIT_POSITION[self.player_id]) # is a pg.Vector2
        self.speed = Const.SPEED_ATTACK if self.role == 1 else Const.SPEED_DEFENSE
        
    def move_direction(self, direction: str):
        
        '''
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        '''
        self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]
        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))
