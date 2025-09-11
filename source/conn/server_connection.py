"""
Class representing a connection from the server to a single client
"""
import socket;
import json;

from conn.connection import Connection;

import random;

import string;

from Game import Game;
from Player import Player;
from Enums import OnFencePlacedState

class ServerConnection(Connection):

    """
    Constructor: Take ownership of a sock from the server
    """
    def __init__(self, 
        server = None, 
        sock = None,
        connection = None,
        len_id = 10,
    ):
        super().__init__(
            server = server,
            sock = sock,
            connection = connection,
            debug = True,
        );
    
    """
    Recieve disconnect from client 
    """
    def disconnect(self):
        # Stop listening loop and inform server
        self._listening = False;
        self._server.disconnect(self.id);
        
        if self._sock is not None:
            self._sock.close();
        
        # Inform other clients in game
        self.leave_game(); 

    """
    Send disconnect to client
    """
    def send_disconnect(self):
        self.send("disconnect", "request", {
            "message": "Server has disconnected you"
        });
        self.disconnect();

    """
    Login an existing player
    """
    def login(self,
        username = None,
        password = None,
        playerNotFound = "Player not found",
        passwordIncorrect = "Password incorrect"
    ):

        # Authenticate player
        player = self._server.leaderboard.get_player(username, check_no_player = False);
        
        if player is None:
            player = self.signup(username = username, password = password)
        
        elif not player.check_password(password):
            raise Exception(passwordIncorrect);
        
        self.player = player;
        return player;

    """
    Signup a new player
    """
    def signup(self,
        username = None,
        password = None,
        playerExists = "Player already exists"
    ):
        # Check if player already exists
        if self._server.leaderboard.get_player(username, check_no_player = False) is not None:
            raise Exception(playerExists);

        # Create new player and register with leaderboard
        player = Player(username = username, password = password);
        self._server.leaderboard.add_player(player);

        self.player = player;
        
        return player;

    """
    Set a new game for the client's player
    """
    def new_game(self,
        name = None,
        length = None,
        height = None,
        max_players = None,
        resource_abundance = None,
        game_exists = "Game already exists"
    ):
        # Check if game already exists
        if self._server.get_game(name, check_no_game = False) is not None:
            raise Exception(game_exists);

        # Create new game and add to server and player
        game = Game(
            name = name,
            host_username = self.player.username,
            dimX = length,
            dimY = height,
            maxPlayers = max_players,
            resourceAbundance = resource_abundance
        );

        self._server.add_game(game);
        self.player.join_game(game);
        self.__game = game;

        return game;
    
    """
    Join an existing game
    """
    def join_game(self, game_name,
        game_not_found = "Game not found",
    ):
        # Check if game exists
        game = self._server.get_game(game_name); 
        
        if game.checkGameoverCondition():
            raise Exception("Game is over");

        self.player.join_game(game);
        self.__game = game;
        
        self.send("joinGame", "success", {
            "game_info": {
                "name": game.name,
                "dimX": game.dimX,
                "dimY": game.dimY,
                "maxPlayers": game.maxPlayers,
                "resourceAbundance": game.resourceAbundance,
            }
        });
        
        self._server.send_to_players([player.username for player in game.players if player.username != self.player.username],
        "joinGame", "request", {
            "player": self.player.username
        });

        return game;

    """
    Place a fence in the player's current game
    """
    def place_fence(self,
        x = None,
        y = None,
    ):
        # Look for cell at x, y and place fence
        cell = self.__game.grid.getCellAt(x, y);
        attempt_place_fence = self.__game.tryPlaceFence(cell, player_id = self.player.username, isServer = True);
        
        # 
        if attempt_place_fence == OnFencePlacedState.FAILURE:
            raise Exception("Fence cannot be placed");

        elif attempt_place_fence == OnFencePlacedState.GAMEOVER:
            return self.end_game(winner = self.__game.getWinner().username);
    
        # Notify all players in game
        game_player_usernames = self.__get_other_usernames(); 

        self._server.send_to_players(game_player_usernames, "placeFence", "response", {
            "fence_info": {
                "x": x,
                "y": y,
                "owner": self.player.username,
            }
        });

    """
    Helper function to get all other players in the game
    """
    def __get_other_usernames(self):
        return [player.username for player in self.__game.players if player.username != self.player.username];

    """
    Helper function to get all players in the game
    """
    def __get_all_usernames(self):
        return [player.username for player in self.__game.players];

    """
    Send a new placed fence to the player's game
    """
    def send_placed_fence(self,
        x = None,
        y = None,
        owner = None,
    ):
        self.send("placedFence", "request", {
            "x": x,
            "y": y,
            "owner": owner,
        });

    """
    Leave the current player's game
    """
    def leave_game(self, 
        player = None,
        message = None
    ):
        # Tell all clients
        game_player_usernames = self.__get_all_usernames(); 
        self._server.send_to_players(game_player_usernames, "leaveGame", "response", {
            "player": self.player.username
        });

        # Tell local player
        self.player.leave_active_game();

        # End game if only one player remaining
        if len(self.__game.players) == 1:
                all_usernames = self.__get_all_usernames();
                if len(all_usernames) == 0:
                    last_username = None;
                else:
                    last_username = all_usernames[0]
                
                self._server.end_game(self.__game, all_usernames, last_username);
    """
    List all games
    """
    def list_games_names(self, message):
        games_names = [game.name for game in self._server.games.values()];
        self.send("listGamesNames", "success", {
            "games": games_names
        });

        return games_names;

    """
    List all players in current game
    """
    def list_players_in_game(self, message):
        players_names = [player.username for player in self.__game.players];
        self.send("listPlayersInGame", "success", {
            "players": players_names
        });

    """
    Notify users that game has ended
    """
    def end_game(self, 
        winner = None
    ):
        game_player_usernames = self.__get_all_usernames(); 
        self._server.end_game(self.__game, game_player_usernames, winner = winner);

    """
    Send current user statistics
    """
    def user_stats(self,
        message = None
    ):
        if self.player is None:
            raise Exception("Player not logged in");

        self.send("userStats", "response", {
            "stats": self.player.get_stats()
        });
