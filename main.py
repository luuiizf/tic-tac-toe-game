import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import json
import time
import random

class TicTacToeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Velha em Rede")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Variáveis de rede
        self.tcp_socket = None
        self.udp_socket = None
        self.tcp_port = 5000
        self.udp_port = 5001
        self.opponent_ip = None
        self.opponent_tcp_port = self.tcp_port
        self.opponent_udp_port = self.udp_port
        self.is_server = False
        self.connected = False
        self.my_turn = False

        # Variáveis do jogo
        self.board = [" " for _ in range(9)]
        self.player_name = ""
        self.opponent_name = ""
        self.player_symbol = ""
        self.opponent_symbol = ""
        self.player_score = 0
        self.opponent_score = 0
        self.game_active = False

        # Criar a interface inicial
        self.create_connection_screen()

    def create_connection_screen(self):
        # Limpar a janela
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=20)

        # Título
        title_label = tk.Label(main_frame, text="Jogo da Velha em Rede", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=20)

        # Nome do jogador
        name_frame = tk.Frame(main_frame, bg="#f0f0f0")
        name_frame.pack(pady=10)
        
        name_label = tk.Label(name_frame, text="Seu nome:", font=("Helvetica", 12), bg="#f0f0f0", fg="#333333")
        name_label.grid(row=0, column=0, padx=10)
        
        self.name_entry = tk.Entry(name_frame, font=("Helvetica", 12), width=20)
        self.name_entry.grid(row=0, column=1, padx=10)

        # Opções de conexão
        conn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        conn_frame.pack(pady=20)
        
        # Botão para criar jogo (servidor)
        create_button = tk.Button(conn_frame, text="Criar Jogo", font=("Helvetica", 12), 
                                 bg="#4CAF50", fg="white", width=15, height=2,
                                 command=self.create_game)
        create_button.grid(row=0, column=0, padx=20, pady=10)
        
        # Botão para entrar em jogo (cliente)
        join_frame = tk.Frame(main_frame, bg="#f0f0f0")
        join_frame.pack(pady=10)
        
        ip_label = tk.Label(join_frame, text="IP do oponente:", font=("Helvetica", 12), bg="#f0f0f0", fg="#333333")
        ip_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.ip_entry = tk.Entry(join_frame, font=("Helvetica", 12), width=15)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5)
        
        join_button = tk.Button(join_frame, text="Entrar no Jogo", font=("Helvetica", 12), 
                               bg="#2196F3", fg="white", width=15, height=2,
                               command=self.join_game)
        join_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Informações
        info_label = tk.Label(main_frame, text="Desenvolvido para estudo de caso de\nprotocolos TCP e UDP em redes", 
                             font=("Helvetica", 10), bg="#f0f0f0", fg="#666666")
        info_label.pack(pady=20)

    def create_game(self):
        """Cria um novo jogo como servidor"""
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            messagebox.showerror("Erro", "Por favor, insira seu nome!")
            return
        
        self.is_server = True
        self.player_symbol = "X"  # Servidor sempre é X
        self.opponent_symbol = "O"
        self.my_turn = True  # Servidor começa
        
        # Iniciar sockets
        try:
            # Socket TCP para movimentos do jogo
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.bind(('0.0.0.0', self.tcp_port))
            self.tcp_socket.listen(1)
            
            # Socket UDP para mensagens de status
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind(('0.0.0.0', self.udp_port))
            
            # Mostrar tela de espera
            self.show_waiting_screen()
            
            # Iniciar threads para aceitar conexões
            tcp_thread = threading.Thread(target=self.accept_tcp_connection)
            tcp_thread.daemon = True
            tcp_thread.start()
            
            udp_thread = threading.Thread(target=self.listen_udp)
            udp_thread.daemon = True
            udp_thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível criar o jogo: {str(e)}")
            self.create_connection_screen()

    def join_game(self):
        """Entra em um jogo como cliente"""
        self.player_name = self.name_entry.get().strip()
        self.opponent_ip = self.ip_entry.get().strip()
        
        if not self.player_name:
            messagebox.showerror("Erro", "Por favor, insira seu nome!")
            return
            
        if not self.opponent_ip:
            messagebox.showerror("Erro", "Por favor, insira o IP do oponente!")
            return
        
        self.is_server = False
        self.player_symbol = "O"  # Cliente sempre é O
        self.opponent_symbol = "X"
        self.my_turn = False  # Servidor começa
        
        # Iniciar sockets
        try:
            # Socket TCP para movimentos do jogo
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((self.opponent_ip, self.opponent_tcp_port))
            
            # Socket UDP para mensagens de status
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind(('0.0.0.0', self.udp_port))
            
            # Enviar nome do jogador
            self.send_tcp_message({
                "type": "player_info",
                "name": self.player_name
            })
            
            # Enviar mensagem UDP de conexão
            self.send_udp_message({
                "type": "player_connected",
                "name": self.player_name
            })
            
            # Iniciar thread para receber mensagens
            tcp_thread = threading.Thread(target=self.receive_tcp_messages)
            tcp_thread.daemon = True
            tcp_thread.start()
            
            udp_thread = threading.Thread(target=self.listen_udp)
            udp_thread.daemon = True
            udp_thread.start()
            
            # Mostrar tela de conexão
            self.show_connecting_screen()
            
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao jogo: {str(e)}")
            self.create_connection_screen()

    def show_waiting_screen(self):
        """Mostra a tela de espera por um oponente"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        waiting_frame = tk.Frame(self.root, bg="#f0f0f0")
        waiting_frame.pack(expand=True, fill=tk.BOTH)
        
        waiting_label = tk.Label(waiting_frame, text="Aguardando oponente conectar...", 
                                font=("Helvetica", 16), bg="#f0f0f0", fg="#333333")
        waiting_label.pack(pady=30)
        
        # Mostrar informações de IP para compartilhar
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            ip_info = f"Seu IP: {ip_address}\nPorta TCP: {self.tcp_port}\nPorta UDP: {self.udp_port}"
        except:
            ip_info = "Não foi possível obter seu IP"
        
        ip_label = tk.Label(waiting_frame, text=ip_info, font=("Helvetica", 12), 
                           bg="#f0f0f0", fg="#333333")
        ip_label.pack(pady=20)
        
        cancel_button = tk.Button(waiting_frame, text="Cancelar", font=("Helvetica", 12), 
                                 bg="#f44336", fg="white", width=10,
                                 command=self.cancel_connection)
        cancel_button.pack(pady=20)

    def show_connecting_screen(self):
        """Mostra a tela de conexão ao servidor"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        connecting_frame = tk.Frame(self.root, bg="#f0f0f0")
        connecting_frame.pack(expand=True, fill=tk.BOTH)
        
        connecting_label = tk.Label(connecting_frame, text=f"Conectando a {self.opponent_ip}...", 
                                   font=("Helvetica", 16), bg="#f0f0f0", fg="#333333")
        connecting_label.pack(pady=30)
        
        cancel_button = tk.Button(connecting_frame, text="Cancelar", font=("Helvetica", 12), 
                                 bg="#f44336", fg="white", width=10,
                                 command=self.cancel_connection)
        cancel_button.pack(pady=20)

    def cancel_connection(self):
        """Cancela a conexão e volta para a tela inicial"""
        if self.tcp_socket:
            self.tcp_socket.close()
        if self.udp_socket:
            self.udp_socket.close()
            
        self.tcp_socket = None
        self.udp_socket = None
        self.connected = False
        self.create_connection_screen()

    def accept_tcp_connection(self):
        """Aceita conexão TCP de um cliente"""
        try:
            client_socket, client_address = self.tcp_socket.accept()
            self.tcp_socket = client_socket
            self.opponent_ip = client_address[0]
            
            # Iniciar thread para receber mensagens
            tcp_thread = threading.Thread(target=self.receive_tcp_messages)
            tcp_thread.daemon = True
            tcp_thread.start()
            
            # Enviar informações do jogador
            self.send_tcp_message({
                "type": "player_info",
                "name": self.player_name
            })
            
        except Exception as e:
            if self.tcp_socket:
                print(f"Erro ao aceitar conexão TCP: {str(e)}")

    def receive_tcp_messages(self):
        """Recebe mensagens TCP do oponente"""
        try:
            while True:
                data = self.tcp_socket.recv(1024)
                if not data:
                    # Conexão fechada
                    self.handle_disconnect()
                    break
                    
                message = json.loads(data.decode('utf-8'))
                self.handle_tcp_message(message)
                
        except Exception as e:
            if self.connected:
                print(f"Erro ao receber mensagem TCP: {str(e)}")
                self.handle_disconnect()

    def send_tcp_message(self, message):
        """Envia mensagem TCP para o oponente"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.tcp_socket.send(data)
        except Exception as e:
            print(f"Erro ao enviar mensagem TCP: {str(e)}")
            self.handle_disconnect()

    def listen_udp(self):
        """Escuta mensagens UDP"""
        try:
            while True:
                data, addr = self.udp_socket.recvfrom(1024)
                if not self.opponent_ip:
                    self.opponent_ip = addr[0]
                    
                message = json.loads(data.decode('utf-8'))
                self.handle_udp_message(message, addr)
                
        except Exception as e:
            if self.connected:
                print(f"Erro ao receber mensagem UDP: {str(e)}")

    def send_udp_message(self, message):
        """Envia mensagem UDP para o oponente"""
        if not self.opponent_ip:
            return
            
        try:
            data = json.dumps(message).encode('utf-8')
            self.udp_socket.sendto(data, (self.opponent_ip, self.opponent_udp_port))
        except Exception as e:
            print(f"Erro ao enviar mensagem UDP: {str(e)}")

    def handle_tcp_message(self, message):
        """Processa mensagens TCP recebidas"""
        msg_type = message.get("type", "")
        
        if msg_type == "player_info":
            # Recebeu informações do oponente
            self.opponent_name = message.get("name", "Oponente")
            
            if not self.connected:
                self.connected = True
                self.game_active = True
                self.create_game_board()
                
        elif msg_type == "move":
            # Recebeu um movimento do oponente
            position = message.get("position")
            if position is not None and 0 <= position < 9 and self.board[position] == " ":
                self.board[position] = self.opponent_symbol
                self.update_board()
                self.my_turn = True
                self.update_status_label()
                
                # Verificar se o jogo acabou
                self.check_game_end()
                
        elif msg_type == "restart":
            # Oponente quer reiniciar o jogo
            self.restart_game()

    def handle_udp_message(self, message, addr):
        """Processa mensagens UDP recebidas"""
        msg_type = message.get("type", "")
        
        if msg_type == "player_connected":
            # Jogador conectado
            name = message.get("name", "Alguém")
            print(f"UDP: {name} conectou")
            
            # Responder com uma mensagem de confirmação
            self.send_udp_message({
                "type": "connection_ack",
                "name": self.player_name
            })
            
        elif msg_type == "connection_ack":
            # Confirmação de conexão
            name = message.get("name", "Alguém")
            print(f"UDP: {name} confirmou conexão")
            
        elif msg_type == "ping":
            # Ping para verificar conexão
            self.send_udp_message({
                "type": "pong",
                "timestamp": message.get("timestamp")
            })
            
        elif msg_type == "pong":
            # Resposta ao ping
            sent_time = message.get("timestamp", 0)
            latency = time.time() - sent_time
            print(f"UDP: Latência: {latency*1000:.2f}ms")
            
        elif msg_type == "game_started":
            # Jogo iniciado
            print("UDP: Jogo iniciado")
            
        elif msg_type == "player_disconnected":
            # Jogador desconectado
            print("UDP: Oponente desconectou")

    def handle_disconnect(self):
        """Trata a desconexão do oponente"""
        if not self.connected:
            return
            
        self.connected = False
        messagebox.showinfo("Desconexão", "O oponente desconectou.")
        self.create_connection_screen()

    def create_game_board(self):
        """Cria o tabuleiro do jogo"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Placar
        score_frame = tk.Frame(main_frame, bg="#e0e0e0", bd=1, relief=tk.RAISED)
        score_frame.pack(fill=tk.X, padx=20, pady=10)
        
        player_label = tk.Label(score_frame, text=f"{self.player_name} ({self.player_symbol})", 
                               font=("Helvetica", 12, "bold"), bg="#e0e0e0", fg="#333333")
        player_label.grid(row=0, column=0, padx=20, pady=5)
        
        vs_label = tk.Label(score_frame, text="vs", font=("Helvetica", 12), bg="#e0e0e0", fg="#666666")
        vs_label.grid(row=0, column=1, padx=20, pady=5)
        
        opponent_label = tk.Label(score_frame, text=f"{self.opponent_name} ({self.opponent_symbol})", 
                                 font=("Helvetica", 12, "bold"), bg="#e0e0e0", fg="#333333")
        opponent_label.grid(row=0, column=2, padx=20, pady=5)
        
        score_label = tk.Label(score_frame, text=f"{self.player_score} - {self.opponent_score}", 
                              font=("Helvetica", 14, "bold"), bg="#e0e0e0", fg="#333333")
        score_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Status
        self.status_label = tk.Label(main_frame, text="", font=("Helvetica", 14), bg="#f0f0f0", fg="#333333")
        self.status_label.pack(pady=10)
        
        # Tabuleiro
        board_frame = tk.Frame(main_frame, bg="#f0f0f0")
        board_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(3):
            for j in range(3):
                index = i * 3 + j
                button = tk.Button(board_frame, text=" ", font=("Helvetica", 24, "bold"), 
                                  width=3, height=1, bg="#ffffff", 
                                  command=lambda idx=index: self.make_move(idx))
                button.grid(row=i, column=j, padx=5, pady=5)
                self.buttons.append(button)
        
        # Botões de ação
        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(pady=20)
        
        restart_button = tk.Button(action_frame, text="Reiniciar Jogo", font=("Helvetica", 12), 
                                  bg="#2196F3", fg="white", width=15,
                                  command=self.request_restart)
        restart_button.grid(row=0, column=0, padx=10)
        
        ping_button = tk.Button(action_frame, text="Ping", font=("Helvetica", 12), 
                               bg="#9C27B0", fg="white", width=10,
                               command=self.send_ping)
        ping_button.grid(row=0, column=1, padx=10)
        
        quit_button = tk.Button(action_frame, text="Sair", font=("Helvetica", 12), 
                               bg="#f44336", fg="white", width=10,
                               command=self.quit_game)
        quit_button.grid(row=0, column=2, padx=10)
        
        # Atualizar status
        self.update_status_label()
        
        # Enviar mensagem UDP de início de jogo
        self.send_udp_message({
            "type": "game_started"
        })

    def update_status_label(self):
        """Atualiza o texto do status do jogo"""
        if self.my_turn:
            self.status_label.config(text=f"Sua vez ({self.player_symbol})")
        else:
            self.status_label.config(text=f"Vez de {self.opponent_name} ({self.opponent_symbol})")

    def make_move(self, position):
        """Realiza um movimento no tabuleiro"""
        if not self.game_active or not self.my_turn or self.board[position] != " ":
            return
            
        # Atualizar tabuleiro
        self.board[position] = self.player_symbol
        self.update_board()
        self.my_turn = False
        self.update_status_label()
        
        # Enviar movimento para o oponente via TCP
        self.send_tcp_message({
            "type": "move",
            "position": position
        })
        
        # Verificar se o jogo acabou
        self.check_game_end()

    def update_board(self):
        """Atualiza a interface do tabuleiro"""
        for i in range(9):
            text = self.board[i]
            color = "#ffffff"
            
            if text == "X":
                color = "#e6f7ff"  # Azul claro para X
            elif text == "O":
                color = "#fff0e6"  # Vermelho claro para O
                
            self.buttons[i].config(text=text, bg=color)

    def check_game_end(self):
        """Verifica se o jogo acabou (vitória ou empate)"""
        winner = self.check_winner()
        
        if winner:
            self.game_active = False
            
            if winner == self.player_symbol:
                self.player_score += 1
                messagebox.showinfo("Fim de Jogo", "Você venceu!")
            else:
                self.opponent_score += 1
                messagebox.showinfo("Fim de Jogo", f"{self.opponent_name} venceu!")
                
            self.create_game_board()  # Atualiza o placar
            
        elif " " not in self.board:
            self.game_active = False
            messagebox.showinfo("Fim de Jogo", "Empate!")
            self.create_game_board()  # Atualiza o placar

    def check_winner(self):
        """Verifica se há um vencedor"""
        # Linhas horizontais
        for i in range(0, 9, 3):
            if self.board[i] != " " and self.board[i] == self.board[i+1] == self.board[i+2]:
                return self.board[i]
                
        # Linhas verticais
        for i in range(3):
            if self.board[i] != " " and self.board[i] == self.board[i+3] == self.board[i+6]:
                return self.board[i]
                
        # Diagonais
        if self.board[0] != " " and self.board[0] == self.board[4] == self.board[8]:
            return self.board[0]
            
        if self.board[2] != " " and self.board[2] == self.board[4] == self.board[6]:
            return self.board[2]
            
        return None

    def request_restart(self):
        """Solicita reinício do jogo"""
        if messagebox.askyesno("Reiniciar", "Deseja reiniciar o jogo?"):
            self.send_tcp_message({
                "type": "restart"
            })
            self.restart_game()

    def restart_game(self):
        """Reinicia o jogo"""
        self.board = [" " for _ in range(9)]
        self.game_active = True
        
        # Determinar quem começa (alternar)
        if self.is_server:
            self.my_turn = not self.my_turn
        else:
            self.my_turn = not self.my_turn
            
        self.update_board()
        self.update_status_label()

    def send_ping(self):
        """Envia um ping UDP para medir latência"""
        self.send_udp_message({
            "type": "ping",
            "timestamp": time.time()
        })

    def quit_game(self):
        """Sai do jogo"""
        if messagebox.askyesno("Sair", "Deseja realmente sair do jogo?"):
            # Enviar mensagem de desconexão
            try:
                self.send_udp_message({
                    "type": "player_disconnected"
                })
            except:
                pass
                
            # Fechar sockets
            if self.tcp_socket:
                self.tcp_socket.close()
            if self.udp_socket:
                self.udp_socket.close()
                
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGame(root)
    root.mainloop()
