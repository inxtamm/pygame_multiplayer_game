# Pygame multiplayer game
This is a game, where you can move around and shoot other players. I made this game to learn more about multiplayer gamedev and also to improve my python and pygame coding skills. 

## Setup
This game requires Python 3 and pygame (2.6.0+).

First you have to run the server file: `python3 server.py`. You can change the IP address to your computer's if you want to play it with friends, but if you just want to play it alone then you can keep the IP address 127.0.0.1. Keep in mind that if you change the IP address you have to change it on the network.py file also.

If the server file is running then you can run the client file (`python3 server.py`) and the game should work. 

## Controls
W/A/S/D to move up/left/down/right.

Mouse movement changes the direction of the weapon; left-click to shoot.

## Levels (Extra)
Theres a file called [level_editor.py](level_editor.py) – with this programm you can make your own levels for the game.

Run `python3 level_editor.py` and a window should pop up. In the left you see all the tiles, that you can use.

If you want to use a tile, just click on it, and if you want place it, hold on or click left mouse button.

If you want to delete it, hold on or click right mouse button.
