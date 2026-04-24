# MCP-4-XIAOZHI - Hướng dẫn triển khai

## Giới thiệu

MCP-History là bộ MCP tools gồm 3 công cụ:
- **ngay_nay_nam_xua** - Sự kiện lịch sử "Ngày này năm xưa"
- **tin_tuc_vnexpress** - Tin tức mới nhất từ VNExpress
- **truyen_ngu_ngon** - Câu chuyện ngắn ngẫu nhiên (23 câu chuyện)

## Yêu cầu

- macOS
- Python 3.10+
- Git

## Các bước triển khai

### 1. Clone dự án

```bash
git clone https://github.com/vdlaptrinh/mcp4xiaozhi.git
cd mcp-history
```

### 2. Tạo môi trường ảo và cài đặt

```bash
python3 -m venv mcp_history_env
source mcp_history_env/bin/activate
pip install -r requirements.txt
```

### 3. Cấu hình MCP Endpoint

Đăng nhập https://xiaozhi.me/dashboard để lấy MCP_ENDPOINT

Cách 1: Tạo file `.env`
```bash
echo 'MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=YOUR_TOKEN"' > .env
```

Cách 2: Export trực tiếp
```bash
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=YOUR_TOKEN"
```

### 4. Chạy ứng dụng

#### Cách A: Chạy GUI (Khuyến nghị)

```bash
python3 gui.py
```

#### Cách B: Chạy CLI

```bash
python3 mcp_pipe.py
```

### 5. Tạo shortcut trên Desktop

```bash
cat > ~/Desktop/MCP-History.command << 'EOF'
#!/bin/bash
cd /Users/dailuu/mcp-history
source mcp_history_env/bin/activate
python3 gui.py
EOF
chmod +x ~/Desktop/MCP-History.command
```

Double-click file `MCP-History.command` để mở ứng dụng.

## Cấu trúc file

```
mcp-history/
├── server.py           # MCP server chính (3 tools)
├── mcp_pipe.py         # Trình kết nối WebSocket
├── gui.py              # Giao diện đồ họa
├── mcp_config.json     # Cấu hình MCP servers
├── requirements.txt   # Thư viện Python
└── .env                # Token MCP_ENDPOINT
```

## MCP Tools

### ngay_nay_nam_xua
```python
ngay_nay_nam_xua(opt="TODAY")  # TODAY | YESTERDAY | TOMORROW
```

### tin_tuc_vnexpress
```python
tin_tuc_vnexpress(limit=10)  # Số tin muốn lấy (1-50)
```

### truyen_ngu_ngon
```python
truyen_ngu_ngon()  # Trả về 1 câu chuyện ngẫu nhiên
```

## Khắc phục lỗi

### Lỗi SSL Certificate
Nếu gặp lỗi SSL, đã có sẵn fix trong `mcp_pipe.py`.

### Lỗi 401 Unauthorized
- Token hết hạn hoặc không hợp lệ
- Lấy token mới từ https://xiaozhi.me/dashboard

### Lỗi "python not found"
Sửa `mcp_config.json`, thay `python` bằng `python3`:
```json
{
  "mcpServers": {
    "mcp-history": {
      "command": "python3",
      "args": ["server.py"]
    }
  }
}
```

## Tác giả

VD Lập Trình - https://vdlaptrinh.github.io