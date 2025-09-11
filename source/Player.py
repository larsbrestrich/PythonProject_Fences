"""
Class representing a single registered player
"""

import random
import string

class Player:
    def __init__(self,
        username = None,
        password = None,
    ):
        self.username = username;
        self.__password = password;
        self.__wins = 0;
        self.__draws = 0;
        self.__losses = 0;

        # Set game details
        self.__active_game = None;
        self.active_game_score = 0;

        # Create collections
        self.games = {};

            
    """
    Get the game the player is currently playing
    """
    def __get_active_game(self,
        no_active_game = " is not in a game"
    ):
        if self.__active_game is None:
            raise Exception(self.username + no_active_game);
        
        return self.__active_game;

    """
    Set the game the player is currently playing
    """
    def __set_active_game(self, game,
        already_in_game = " is already in this game"                     
    ):
        if game is not None and self.__active_game is not None and game.id == self.__active_game.id:
            raise Exception(self.username + already_in_game);

        self.__active_game = game;
        self.games[game.id] = game; 

    """
    Get player to join a game
    """
    def join_game(self, game):
        game.add_player(self);
        self.__set_active_game(game);

    """
    Check if password is correct
    """
    def check_password(self, password):
        return self.__password == password;

    """
    Place a fence in the current game
    """
    def place_fence(self, 
        x = None, 
        y = None, 
        orientation = None,
    ):
        active_game = self.__get_active_game();
        active_game.tryPlaceFence(self, x, y, orientation);

    """
    Leave currently active game
    """
    def leave_active_game(self):
        # Clean up active game
        active_game = self.__get_active_game();
        if active_game != None:
            active_game.remove_player(self.username);
        
        # Unset active game
        self.__active_game = None;


    """
    Get player statistics
    """
    def get_stats(self):
        return { 
            "wins": self.__wins,
            "draws": self.__draws,
            "losses": self.__losses,
        };

    """
    Add wins, losses or draws to the player
    """
    def add_win(self):
        self.__wins += 1;

    def add_loss(self):
        self.__losses += 1;

    def add_draw(self):
        self.__draws += 1;

