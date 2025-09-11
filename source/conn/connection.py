"""
Generic representation of a single connection between any two nodes. Contains methods for sending and receiving messages.
"""
import socket
import json

import time
import threading

import random
import string

import traceback

class Connection:
    """
    Constructor: Get connection ID and optionally start listening
    """
    def __init__(self,
        len_id= 10,
        server = None,
        sock = None,
        connection = None,
        send_acknowledgement = True,
        debug = False,
    ):
        self.__debug = debug;
        self.__single_player = True;
        self.__listening = False;
        
        self.__category_handle_dict = {
            "disconnect": self.disconnect,
            "listGamesNames": self.list_games_names,
            "listPlayersInGame": self.list_players_in_game,
            "login": self.login,
            "signup": self.signup,
            "newGame": self.new_game,
            "joinGame": self.join_game,
            "placeFence": self.place_fence,
            "leaveGame": self.leave_game,
            "endGame": self.end_game,
            "userStats": self.user_stats,
        };

        # Randomly generate an id
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = len_id));

        if server is not None:
            self._server = server;
        
        self.__connection_type = "server" if server is not None else "client";
        self.__send_acknowledgement = send_acknowledgement;
        
        # Write to in-memory connection directly
        self.__connection = connection;

        # Write over provided connection
        self._sock = sock;
        if sock is not None:
            self.__reader = sock.makefile('r');
            self.__writer = sock.makefile('w');
                
            # Start listening for messages
            self.__listening_thread = threading.Thread(target = self.__start_listening);
            self.__listening_thread.daemon = True;
            self.__listening_thread.start();
                
    """
    Listen for messages from the other connection
    """
    def __start_listening(self):
        # Avoid starting multiple listeners
        if self.__listening is True:
            return;
        
        try:
            if self.__debug:
                print(f"Connection {self.id} ({self.__connection_type}) listening for messages");
            self.__listening = True;

            # Listen for messages
            while self.__listening:
                if self.__debug:
                    print(f"Connection {self.id} ({self.__connection_type}) waiting for a message");

                # Read a message
                try:
                    line = self.__reader.readline();
                except ConnectionResetError as e:
                    raise ConnectionResetError(e);

                if line == "":
                    break;

                line = line.strip();
                if line:
                    self.handle_message(line);
        
        except ConnectionResetError as e:
            pass;

        except Exception as e:
            self.__handle_error(e);

        finally:
            self.__handle_error(f"Connection {self.id} closed", attempt_send = False);
            
            if hasattr(self, "_ServerConnection__game"):
                self.leave_game("self");

            if self._sock is not None:
                self._sock.close();
                self._sock = None;
            
            
            return;
    
    """
    Handle an error in the client
    """
    def __handle_error(self, message,
        category = "generic_error",
        attempt_send = True
    ):
        if self.__debug:
            traceback.print_exc();

        # Turn error object into string
        if not isinstance(message, str):
            message = str(message);
        
        if self.__debug:
            print(f"Error in connection {self.id} ({self.__connection_type}): {message}");
        
        # Send error message to client
        if not attempt_send:
            return;

        self.send(category, "error", message);
    
    """
    Send a message to the client
    """
    def send(self, category, status, message,
        delimiter = "\n",
    ):
        try:
            # Convert message to serialisable format
            if isinstance(message, type({}.keys())):
                message = list(message);

            # Wrap string in message object
            if isinstance(message, str):
                message = {"message": message};

            # Send the message
            message = {
                "category": category,
                "status": status,
                "message": message
            };

            str_message = json.dumps(message);

            # Check if connection is still open 
            if self._sock is not None:
                socket_message = str_message + delimiter;
                
                self.__writer.write(socket_message);
                self.__writer.flush();

                if self.__debug:
                    socket_message_info = f"Connection ID {self.id} ({self.__connection_type}) sending message: {socket_message} via socket";
                    print(socket_message_info);
            
            # Write to in-memory connection directly
            if self.__connection is not None: 
                self.__connection.handle_message(str_message);

                if self.__debug:
                    memory_message_info = f"Connection ID {self.id} ({self.__connection_type}) sending message: {str_message} via memory";
                    print(memory_message_info);

        except Exception as e:
            self.__handle_error(f"Error in sending message: {message}, {e}", attempt_send = False);

    """
    Handle a message from the client
    """
    def handle_message(self, message,
        unknown_message = "Unknown message category",
        message_category_no_reply = ["disconnect", "listGamesNames", "leaveGame", "listPlayersInGame", "joinGame", "userStats"],
        message_status_no_reply = ["error"],
    ):
        
        if self.__debug: 
            print(f"Connection {self.id} ({self.__connection_type}) received message: {message}");

        # Handle the message
        try:
            message = json.loads(message);

        except json.JSONDecodeError as e:
            self.__handle_error(e); 
        
        # Get the message category
        message_category = message["category"];
        message_status = message["status"];
        message = message["message"];
        
        # Handle the message
        try:
            if message_category in self.__category_handle_dict:
                self.__category_handle_dict[message_category](**message);
            
            elif message_status == "error":
                self.__handle_error(message, attempt_send = False);
            
            # Valid message category not sent
            else:
                raise Exception(unknown_message);
            
            # Send successs message to client
            if self.__send_acknowledgement and message_category not in message_category_no_reply and message_status not in message_status_no_reply:
                self.send(message_category, "successs", "success");

        # Handle errors in message handling
        except Exception as e:
            self.__handle_error(e, category = message_category);
    
    
    
