# 🕰️ MCP4XIAOZHI - MCP Tools for XiaoZhi AI

**MCP4XIAOZHI** là bộ công cụ MCP cho XiaoZhi AI và ChatGPT, bao gồm:
- 📅 **ngay_nay_nam_xua** - Sự kiện lịch sử "Ngày này năm xưa"
- 📰 **tin_tuc_vnexpress** - Tin tức mới nhất từ VNExpress
- 📖 **truyen_ngu_ngon** - Câu chuyện ngắn hay
- 📅 **lich_cong_tac** - Lịch công tác tuần từ Excel

---

## 📋 Yêu cầu

- macOS (MacBook)
- Python 3.10+
- Git

---

## 🚀 Cài đặt trên MacBook MỚI

### Bước 1: Clone dự án

Mở **Terminal** và chạy:

```bash
cd ~/Downloads
git clone https://github.com/vdlaptrinh/mcp4xiaozhi.git
cd mcp4xiaozhi
```

### Bước 2: Tạo môi trường ảo

```bash
python3 -m venv mcp4xiaozhi_env
source mcp4xiaozhi_env/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Tạo shortcut trên Desktop

```bash
# Tạo file shortcut
echo '#!/bin/bash
cd /Users/dailuu/mcp4xiaozhi
source mcp4xiaozhi_env/bin/activate
python3 gui.py' > ~/Desktop/MCP4XIAOZHI.command

# Cấp quyền chạy
chmod +x ~/Desktop/MCP4XIAOZHI.command
```

**Kết quả:** File `MCP4XIAOZHI.command` sẽ xuất hiện trên Desktop.

---

## 🎯 Cách sử dụng

### Cách 1: Chạy từ Desktop (Khuyến nghị)

1. **Double-click** vào file `MCP4XIAOZHI.command` trên Desktop
2. Cửa sổ **MCP-CHATBOT-AI** hiện ra

### Cách 2: Chạy từ Terminal

```bash
cd ~/mcp4xiaozhi
source mcp4xiaozhi_env/bin/activate
python3 gui.py
```

---

## 📱 Hướng dẫn sử dụng GUI

### 1. Kết nối MCP Endpoint

```
┌─────────────────────────────────────────┐
│ MCP-CHATBOT-AI                        │
├─────────────────────────────────────────┤
│ MCP Endpoint: [________________] [Kết nối] │
│ Trạng thái: Chưa kết nối             │
│                                         │
│ MCP Endpoint lần cuối: [_____________] [Use]  │
│                                         │
│ Upload File: [_____________] [Chọn] [Upload] │
│                                         │
│ Log kết nối:                           │
│ [                                     ] │
│ [                                     ] │
└─────────────────────────────────────────┘
```

**Các bước:**

1. **Đăng nhập** https://xiaozhi.me/dashboard
2. **Copy** MCP Endpoint URL (có dạng `wss://api.xiaozhi.me/mcp/?token=...`)
3. **Dán** vào ô "MCP Endpoint"
4. **Bấm** "Kết nối"
5. Đợi hiện thông báo "Đã kết nối"

### 2. Upload file lịch công tác

**Khi cần cập nhật lịch tuần mới:**

1. **Chuẩn bị file Excel** với 6 cột:
   - THỨ NGÀY
   - THỜI GIAN
   - NỘI DUNG CÔNG VIỆC
   - CHỦ TRÌ
   - ĐỊA ĐIỂM
   - THÀNH PHẦN

2. **Bấm** "Chọn File" → chọn file Excel

3. **Bấm** "Upload" → File sẽ được:
   - Copy vào thư mục project với tên `lich_lam_viec.xlsx`
   - Hiển thị thông tin file trong log

---

## ❓ Cách hỏi MCP Tools (trên XiaoZhi AI)

### ngay_nay_nam_xua
```
User: Ngày này năm xưa hôm nay là gì?
Bot: 📜 Sự kiện 24-4:
    - 1320: Vua Trần Anh Tông...
    - 1931: ...
```

### tin_tuc_vnexpress
```
User: Tin tức mới nhất hôm nay?
Bot: 📰 Tin mới nhất từ VNExpress:
    1. Chủ tịch Vietcombank...
    2. VN-Index mất hơn...
```

### truyen_ngu_ngon
```
User: Kể cho tôi một câu chuyện hay
Bot: 📖 Câu chuyện:
    1. Quý bà và người ăn mày...
```

### lich_cong_tac
```
User: Lịch thứ hai tuần này?
Bot: 📅 Hai 20/4:
    7h00: Chào cờ...
```

---

## 🔧 Khắc phục lỗi

### ❌ Lỗi "Python not found"
```bash
# Kiểm tra Python
which python3
# Nếu không có, cài đặt:
brew install python3
```

### ❌ Lỗi SSL Certificate
Đã có sẵn fix trong `mcp_pipe.py`

### ❌ Lỗi 401 Unauthorized
- Token hết hạn
- Lấy token mới từ https://xiaozhi.me/dashboard

### ❌ Lỗi "File không tồn tại"
Đảm bảo file `lich_lam_viec.xlsx` đúng định dạng 6 cột

---

## 📂 Cấu trúc file

```
mcp4xiaozhi/
├── server.py           # MCP server (4 tools)
├── mcp_pipe.py         # Kết nối WebSocket
├── gui.py              # Giao diện GUI
├── mcp_config.json    # Cấu hình MCP
├── requirements.txt   # Thư viện Python
├── lich_lam_viec.xlsx  # Lịch công tác
└── README.md         # Tài liệu này
```

---

## 📜 Giấy phép

MIT License - Tự do sử dụng và phân phối.

---

## 🧑‍💻 Tác giả

VD Lập Trình - https://vdlaptrinh.github.io