import pygame as pg
import math
from EventManager import *
from Model import GameEngine
import Const


class GraphicalView:
    '''
    Draws the state of GameEngine onto the screen.
    '''
    background = pg.Surface(Const.ARENA_SIZE)

    def __init__(self, ev_manager: EventManager, model: GameEngine):
        '''
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        '''
        self.ev_manager = ev_manager
        ev_manager.register_listener(self)

        self.model = model

        self.screen = pg.display.set_mode(Const.WINDOW_SIZE)
        pg.display.set_caption(Const.WINDOW_CAPTION)
        self.background.fill(Const.BACKGROUND_COLOR)

    def initialize(self):
        '''
        This method is called when a new game is instantiated.
        '''
        pass

    def notify(self, event):
        '''
        Called by EventManager when a event occurs.
        '''
        if isinstance(event, EventInitialize):
            self.initialize()

        elif isinstance(event, EventEveryTick):
            self.display_fps()

            cur_state = self.model.state_machine.peek()
            if cur_state == Const.STATE_MENU: self.render_menu()
            elif cur_state == Const.STATE_PLAY:
                self.round_timer = event.round_timer
                self.render_play()
            elif cur_state == Const.STATE_PAUSE: self.render_pause()
            elif cur_state == Const.STATE_ENDGAME: self.render_endgame()
        
        elif isinstance(event, EventSwitchRoles):
            self.render_play();
    

    def display_fps(self):
        '''
        Display the current fps on the window caption.
        '''
        pg.display.set_caption(f'{Const.WINDOW_CAPTION} - FPS: {self.model.clock.get_fps():.2f}')


    def draw_timer(self, round_timer, screen):
        color = Const.PLAYER_COLOR[0] if self.model.players[0].role == 1 else Const.PLAYER_COLOR[1]
        # draw a circle
        center_x = 725
        center_y = 75
        radius = 45
        iterations = 150
        percentage = round_timer / Const.ROUND_LENGTH

        for i in range(iterations):
                ang = i * 3.14159 * 2 / iterations * percentage
                dx = int(math.cos(ang) * radius)
                dy = int(math.sin(ang) * radius)
                x = center_x + dx
                y = center_y + dy
                pg.draw.circle(screen, color, (x, y), 2)

    def draw_scoreboard(self, screen):
        font = pg.font.Font(None, 36)
        color = pg.Color('gray88')

        #draw outline rectangle
        pg.draw.rect(screen, color, pg.Rect(250, 50, 300, 3))
        pg.draw.rect(screen, color, pg.Rect(250, 53, 3, 100))
        pg.draw.rect(screen, color, pg.Rect(250, 153, 300, 3))
        pg.draw.rect(screen, color, pg.Rect(547, 53, 3, 100))

        text_surface_green = font.render("Green", 1, color)
        text_position_green = (325, 75)
        screen.blit(text_surface_green, text_surface_green.get_rect(center = text_position_green))

        text_surface_magenta = font.render("Magenta", 1, color)
        text_position_magenta = (475, 75)
        screen.blit(text_surface_magenta, text_surface_magenta.get_rect(center = text_position_magenta))

        text_surface_green = font.render(str(self.model.players[0].score), 1, color)
        text_position_green = (325, 125)
        screen.blit(text_surface_green, text_surface_green.get_rect(center = text_position_green))

        text_surface_magenta = font.render(str(self.model.players[1].score), 1, color)
        text_position_magenta = (475, 125)
        screen.blit(text_surface_magenta, text_surface_magenta.get_rect(center = text_position_magenta))

                

    def render_menu(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)
        
        # draw text
        font = pg.font.Font(None, 36)
        text_surface = font.render("Press [space] to start ...", 1, pg.Color('gray88'))
        text_center = (Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[1] / 2)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))

        pg.display.flip()

    def render_play(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)

        #draw scoreboard
        self.draw_scoreboard(self.screen)

        #draw counter
        seconds = round(self.round_timer / Const.FPS, 2)
        self.draw_timer(self.round_timer, self.screen)
        font = pg.font.Font(None, 24)
        text_surface = font.render(f'{seconds}s', 0, pg.Color('white'))
        self.screen.blit(text_surface, text_surface.get_rect(center = (725, 75)))        

        # draw players
        font = pg.font.Font(None, 24)
        for player in self.model.players:
            center = list(map(int, player.position))
            pg.draw.circle(self.screen, Const.PLAYER_COLOR[player.player_id], center, Const.PLAYER_RADIUS)
            text_surface = font.render(Const.PLAYER_ROLE[player.role], 0, pg.Color('black'))
            self.screen.blit(text_surface, text_surface.get_rect(center = center))
        pg.display.flip()



    def render_pause(self):
        
        s = pg.Surface(Const.WINDOW_SIZE)
        s.set_alpha(100)
        s.fill(Const.BACKGROUND_COLOR)

        #draw tinted players
        font = pg.font.Font(None, 24)
        for player in self.model.players:
            center = list(map(int, player.position))
            pg.draw.circle(s, Const.PLAYER_COLOR[player.player_id], center, Const.PLAYER_RADIUS)
            text_surface = font.render(Const.PLAYER_ROLE[player.role], 0, pg.Color('black'))
            s.blit(text_surface, text_surface.get_rect(center = center))
        
        #draw counter
        seconds = round(self.round_timer / Const.FPS, 2)
        self.draw_timer(self.round_timer, s)
        font = pg.font.Font(None, 24)
        text_surface = font.render(f'{seconds}s', 0, pg.Color('white'))
        s.blit(text_surface, text_surface.get_rect(center = (725, 75)))        

        self.screen.fill(Const.BACKGROUND_COLOR)
        self.screen.blit(s, (0, 0))
        font = pg.font.Font(None, 40)

        text_surface = font.render("Game Paused. Press Enter to continue", 0, pg.Color('gray88'))
        text_center = (Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[1] / 2)
        self.screen.blit(text_surface, text_surface.get_rect(center = text_center))
        pg.display.flip()

    def render_endgame(self):
        
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)
        # draw text
        font = pg.font.Font("None", 36)
        text_surface = font.render("Game Over Player 1 Wins", 1, pg.Color('gray88'))
        text_center = (Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[1] / 2)
        self.screen.blit(text_surface, text_surface.get_rect(center = text_center))
        pg.display.update()
