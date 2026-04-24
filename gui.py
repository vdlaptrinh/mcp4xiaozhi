import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import sys
from dotenv import load_dotenv, set_key

load_dotenv()

LAST_ENDPOINT_FILE = ".last_endpoint"

class MCPHistoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MCP-History - Ngày này năm xưa")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.process = None
        self.is_connected = False
        
        self._build_ui()
        self._load_saved_endpoint()
    
    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="MCP-History", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text="Tra cứu sự kiện lịch sử Ngày này năm xưa")
        subtitle_label.pack(pady=(0, 20))
        
        config_frame = ttk.LabelFrame(main_frame, text="Cấu hình MCP Endpoint", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(config_frame, text="MCP_ENDPOINT:").pack(anchor=tk.W)
        
        endpoint_frame = ttk.Frame(config_frame)
        endpoint_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.endpoint_var = tk.StringVar(value=os.environ.get("MCP_ENDPOINT", ""))
        self.endpoint_entry = ttk.Entry(endpoint_frame, textvariable=self.endpoint_var, width=60)
        self.endpoint_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.connect_btn = ttk.Button(endpoint_frame, text="Kết nối", command=self._toggle_connection)
        self.connect_btn.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(config_frame, text="Chưa kết nối", foreground="gray")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        last_frame = ttk.Frame(config_frame)
        last_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(last_frame, text="MCP_ENDPOINT LẦN CUỐI:").pack(anchor=tk.W)
        last_input_frame = ttk.Frame(last_frame)
        last_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.last_endpoint_var = tk.StringVar(value="")
        self.last_endpoint_entry = ttk.Entry(last_input_frame, textvariable=self.last_endpoint_var, width=60, state="readonly")
        self.last_endpoint_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.use_btn = ttk.Button(last_input_frame, text="Use", command=self._use_last_endpoint)
        self.use_btn.pack(side=tk.LEFT)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log kết nối", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _load_saved_endpoint(self):
        saved_endpoint = os.environ.get("MCP_ENDPOINT", "")
        if saved_endpoint:
            self.endpoint_var.set(saved_endpoint)
        
        last = self._load_last_endpoint()
        if last:
            self.last_endpoint_var.set(last)
    
    def _load_last_endpoint(self):
        if os.path.exists(LAST_ENDPOINT_FILE):
            with open(LAST_ENDPOINT_FILE, 'r') as f:
                return f.read().strip()
        return ""
    
    def _save_last_endpoint(self, endpoint):
        with open(LAST_ENDPOINT_FILE, 'w') as f:
            f.write(endpoint)
        self.last_endpoint_var.set(endpoint)
    
    def _use_last_endpoint(self):
        last = self._load_last_endpoint()
        if last:
            self.endpoint_var.set(last)
        else:
            messagebox.showwarning("Cảnh báo", "Không có MCP_ENDPOINT lần cuối")
    
    def _toggle_connection(self):
        if self.is_connected:
            self._disconnect()
        else:
            self._connect()
    
    def _connect(self):
        endpoint = self.endpoint_var.get().strip()
        if not endpoint:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập MCP_ENDPOINT")
            return
        
        self._log(f"Đang kết nối tới: {endpoint}")
        self.connect_btn.config(state=tk.DISABLED)
        
        def connect_thread():
            try:
                self.process = subprocess.Popen(
                    [sys.executable, "mcp_pipe.py", "server.py"],
                    env={**os.environ, "MCP_ENDPOINT": endpoint},
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in self.process.stdout:
                    self._log(line.strip())
                    if "Successfully connected" in line or "Started server process" in line:
                        self.root.after(0, self._on_connected)
                        break
                
            except Exception as e:
                self.root.after(0, lambda: self._on_error(str(e)))
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def _on_connected(self):
        self.is_connected = True
        self.connect_btn.config(text="Ngắt kết nối", state=tk.NORMAL)
        self.status_label.config(text="Đã kết nối", foreground="green")
        self.endpoint_entry.config(state=tk.DISABLED)
        self._save_last_endpoint(self.endpoint_var.get())
    
    def _on_error(self, msg):
        self.connect_btn.config(state=tk.NORMAL)
        self.status_label.config(text=f"Lỗi: {msg}", foreground="red")
        self._log(f"Lỗi kết nối: {msg}")
    
    def _disconnect(self):
        if self.process:
            self.process.terminate()
            self.process = None
        
        self.is_connected = False
        self.connect_btn.config(text="Kết nối", state=tk.NORMAL)
        self.status_label.config(text="Đã ngắt kết nối", foreground="gray")
        self.endpoint_entry.config(state=tk.NORMAL)
        self._log("Đã ngắt kết nối")
    
    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _on_close(self):
        self._disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MCPHistoryGUI(root)
    root.mainloop()