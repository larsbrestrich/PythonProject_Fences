"""
Recieves and processes requests from clients
"""
from conn.server_connection import ServerConnection;
from Leaderboard import Leaderboard;

import socket;

import threading;

import traceback;

import time;
import sys;  

class Server:
    def __init__(self,
        no_socket = False,
    ):
        # Initialise server components
        self.leaderboard = Leaderboard();

        # Initialise internal state
        self.games = {};
        self.__clients = {};
        self.__listening = False;
        
        # Start server socket and listening thread
        if not no_socket:
            self.__start_server();
            self.__thread = threading.Thread(target = self.__listen_for_new_sockets);
            self.__thread.daemon = True;
            self.__thread.start();
            
            # Keep daemon thread alive
            try:
                while True:
                    time.sleep(1);

            except KeyboardInterrupt:
                self.__stop();
    
    """
    Start server socket
    """
    def __start_server(self,
        host = "localhost",
        port = 9999,
        max_clients = 5,
        timeout = 1,
    ):
        # Create and bind socket
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.__server_socket.bind((host, port));
        self.__server_socket.listen(max_clients);
        self.__server_socket.settimeout(timeout);
        print(f"Server started on {host}:{port}");
    
    """
    Start listening for new sockets
    """
    def __listen_for_new_sockets(self):
        if self.__listening:
            return;
        
        print("Server listening for new connections");
        self.__listening = True;

        while self.__listening:
            # Blocks loop until new connection
            try:
                client_socket, client_address = self.__server_socket.accept();
            except socket.timeout:
                continue;

            except Exception as e:
                traceback.print_exc();
                print(f"Server error accepting new connection: {e}");
                break;
            
            print(f"New connection from {client_address}");
            self.create_client(sock = client_socket);
        
        print("Server stopped listening for new connections");

        self.__server_socket.close();
        print("Server socket closed");
        sys.exit(0);
    
    """
    Stop listening and exit on ctrl+c
    """
    def __stop(self):
        print("Recieved ctrl+c"); 

        self.__listening = False;

        # Keep daemon alive until listening stopped
        while self.__thread.is_alive():
            time.sleep(1);


    """
    Create a new server connection to a client
    """
    def create_client(self, 
        sock = None,
    ):
        client = ServerConnection(
            server = self,
            sock = sock, 
        );
        self.__register_client(client);

        print(f"New client registered with server at serverConnection id {client.id}")
    
    """
    Register a client with the server
    """
    def __register_client(self, client):
        self.__clients[client.id] = client;
    
    """
    Get list of game names
    """
    def get_games_keys(self):
        return self.games.keys();
    
    """
    Remove a client from server 
    """
    def disconnect(self, client):
        del self.__clients[client.id];

    """
    Register a new game
    """
    def add_game(self, game,
        existing_game = "This game already exists",
        name_taken = "This game name is already taken",
    ):
        # Check if game or game name already exists
        if game.id in self.games:
            raise Exception(existing_game);

        searched_game = self.get_game(game.name, check_no_game = False);
        if searched_game is not None:
            raise Exception(name_taken);
        
        # Add game to server
        self.games[game.id] = game;
    
    """
    Get a game by name
    """
    def get_game(self, name,
        check_no_game = True,
        no_game = "No game with that name ",
        multiple_games = "Multiple games with the same name",
    ):
        # Get all games with requested name
        games = [game for game in self.games.values() if game.name == name];        
        # Return errors if no game or multiple games found
        if len(games) == 0:
            if check_no_game:
                raise Exception(no_game + name);
            else:
                return None;

        if len(games) > 1:
            raise Exception(multiple_games);
        
        # Return only game found
        return games[0];

    """
    Send message to clients by player id
    """
    def send_to_players(self,
        players = None,
        category = None,
        status = None,
        message = None,
    ):
        clients = [client for client in self.__clients.values() if client.player.username in players];

        [client.send(category, status, message) for client in clients];

    """
    End a game
    """
    def end_game(self, game, game_player_usernames, 
        winner = None
    ):  
        # Remove game from server
        del self.games[game.id];

        # Send game over message to players
        self.send_to_players(
            players = game_player_usernames,
            category = "endGame",
            status = "response",
            message = {
                "winner": winner,
            }
        );

        # Update leaderboard
        self.leaderboard.update(game_player_usernames, winner);

