# 音樂補習班預約系統

完整的預約管理系統，包含學生預約網頁 + 管理後台。

## 檔案結構

```
music_booking/
├── server.py              # Flask 後端（API + 頁面路由）
├── requirements.txt       # 相依套件
├── static/
│   ├── booking.html       # 學生預約頁面（http://localhost:5000/）
│   └── admin.html         # 管理後台（http://localhost:5000/admin）
└── booking.db             # SQLite 資料庫（自動建立）
```

---

## 快速啟動

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器
```bash
python server.py
```

啟動後自動建立資料庫，並載入 3 位範例老師（14 天時段）。

### 3. 開啟頁面
- 學生預約：http://localhost:5000
- 管理後台：http://localhost:5000/admin（預設密碼：`admin123`）

---

## 環境變數（選用）

| 變數名稱 | 說明 | 預設值 |
|---|---|---|
| `SECRET_KEY` | Flask Session 金鑰 | music-school-secret-2024 |
| `ADMIN_PASSWORD` | 管理後台密碼 | admin123 |

設定方式：
```bash
export ADMIN_PASSWORD="你的密碼"
python server.py
```

---

## API 說明

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/teachers` | 取得老師列表 |
| GET | `/api/courses` | 取得課程列表 |
| GET | `/api/slots?teacher_id=1&days=14` | 取得可用時段 |
| POST | `/api/book` | 送出預約 |
| GET | `/admin/api/bookings` | 查看所有預約（需密碼） |
| POST | `/admin/api/bookings/:id/cancel` | 取消預約（需密碼） |
| GET | `/admin/api/teachers` | 管理老師列表（需密碼） |
| POST | `/admin/api/teachers` | 新增老師（需密碼） |
| DELETE | `/admin/api/teachers/:id` | 停用老師（需密碼） |

---

## 管理後台功能

- 查看所有預約（可依狀態篩選、搜尋學生姓名/電話）
- 取消預約（時段自動釋放）
- 統計資料（總預約數、已確認、今日課程、預估收入）
- 新增 / 停用老師（新增時自動建立 14 天時段）

---

## 部署到 Railway / Render

1. 上傳到 GitHub
2. 新增環境變數 `ADMIN_PASSWORD`
3. 啟動指令：`gunicorn server:app`
4. 將 LINE Bot Webhook URL 改為部署後的網址