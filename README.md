# Jogo da Velha em Rede (Tic-Tac-Toe Multiplayer)

Este projeto implementa um jogo da velha multiplayer que utiliza protocolos TCP e UDP para comunicação em rede. O jogo foi desenvolvido como um estudo de caso para transmissão de dados em redes de computadores.

## Requisitos

- Python 3.6 ou superior
- Tkinter (geralmente já vem instalado com o Python)

## Como Executar

1. Clone ou baixe este repositório
2. Execute o arquivo principal:
   
```python
python main.py
```

## Funcionalidades

- Interface gráfica usando Tkinter
- Comunicação em rede usando TCP e UDP
- Placar de pontuação
- Reinício de jogo mantendo o placar
- Medição de latência via ping UDP

## Protocolos de Rede

### TCP (Transmission Control Protocol)

O TCP é usado para todas as comunicações que exigem confiabilidade:
- Movimentos no tabuleiro
- Informações do jogador
- Solicitações de reinício de jogo

O TCP garante que todos os dados sejam entregues na ordem correta e sem perdas, o que é essencial para manter a consistência do estado do jogo entre os jogadores.

### UDP (User Datagram Protocol)

O UDP é usado para mensagens auxiliares e informações não críticas:
- Notificações de conexão
- Pings para medir latência
- Notificações de início de jogo
- Notificações de desconexão

O UDP é mais rápido que o TCP, mas não garante a entrega dos pacotes. É adequado para informações que podem ser perdidas sem afetar o funcionamento do jogo.

## Como Jogar

1. Inicie o aplicativo em dois computadores diferentes
2. Em um computador, clique em "Criar Jogo" (este será o servidor)
3. No outro computador, insira o IP do servidor e clique em "Entrar no Jogo"
4. Após a conexão, o jogo começará automaticamente
5. Jogue alternadamente até que haja um vencedor ou empate
6. Use o botão "Reiniciar Jogo" para jogar novamente mantendo o placar

## Estrutura do Código

O código está organizado em uma única classe `TicTacToeGame` que gerencia:
- Interface gráfica
- Lógica do jogo
- Comunicação em rede
- Gerenciamento de estado

As mensagens TCP e UDP são formatadas como objetos JSON para facilitar o processamento.
