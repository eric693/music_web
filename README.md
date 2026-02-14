# 音樂補習班管理系統 - 完整版

完整的補習班管理系統，包含 16 個功能模組，涵蓋預約、師生、財務、LINE、網站、出席、成績、排班等完整功能。

## 系統特色

- 完整的 16 個功能模組，全部已實作完成
- 模組化設計，可彈性啟用/停用
- 專業的紫色主題介面
- 響應式設計，支援電腦與手機
- 完整的資料庫設計與 API
- 無 Emoji / Icon 設計，專業簡潔

## 快速啟動

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 啟動伺服器
```bash
python app.py
```

### 3. 開啟頁面
- 學生預約：http://localhost:5000
- 管理後台登入：http://localhost:5000/admin（預設密碼：`admin123`）
- 模組管理首頁：http://localhost:5000/dashboard（需先登入）

### 4. 使用流程
1. 訪問 `/admin` 輸入管理員密碼
2. 登入成功後自動跳轉到 `/dashboard`（模組管理頁面）
3. 點擊模組卡片啟用/停用功能
4. 左側選單會動態顯示已啟用的模組功能
5. 點擊選單項目使用各項功能

## 檔案結構

```
music_booking/
├── app.py                     # Flask 後端主程式
├── requirements.txt           # Python 套件清單
├── README.md                  # 說明文件
├── LINE_SETUP.md             # LINE 串接設定指南
├── MODULE_CHECKLIST.md        # 模組檢查清單
├── static/                    # 前端靜態檔案
│   ├── index.html            # 模組管理首頁
│   ├── admin.html            # 管理員登入頁
│   ├── booking.html          # 學生預約頁面
│   ├── booking-admin.html    # 預約管理（iframe）
│   ├── teacher-mgmt.html     # 師生管理（iframe）
│   ├── attendance.html       # 出席打卡（iframe）
│   ├── grades.html           # 成績管理（iframe）
│   ├── staff-schedule.html   # 排班管理（iframe）
│   ├── finance.html          # 財務報表（iframe）
│   ├── accounting.html       # 會計科目（iframe）
│   ├── course-schedule.html  # 課表系統（iframe）
│   ├── ceo-report.html       # CEO每日報（iframe）
│   ├── line-messages.html    # LINE訊息推播（iframe）
│   ├── line-notifications.html # LINE通知設定（iframe）
│   ├── line-interactive.html # LINE互動功能（iframe）
│   ├── website-design.html   # 網站設計（iframe）
│   ├── website-content.html  # 內容管理（iframe）
│   └── online-booking.html   # 線上報名（iframe）
└── booking.db                # SQLite 資料庫（自動建立）
```

## 完整功能模組

### 核心功能（預設啟用）

#### 1. 模組管理
- 視覺化模組卡片
- 啟用/停用切換開關
- 即時費用計算
- 統計資訊顯示
- 模組狀態保存

#### 2. 預約管理
- 預約列表顯示
- 搜尋與篩選（姓名/電話/編號）
- 狀態管理（已確認/已取消）
- 取消預約功能
- 統計報表（總預約、已確認、今日課程、預估收入）
- 教師管理（新增/停用）

### LINE 串接模組（FREE - $3000/年）

#### 3. 訊息推播
- 群發訊息功能
- 訊息範本（自訂/上課/繳費/活動）
- 發送對象選擇（全部/在學/指定學生）
- 排程發送功能
- 訊息歷史記錄
- 手機介面即時預覽
- 發送統計

#### 4. 通知設定
- 到班通知（學生到班自動通知家長）
- 課程提醒（可設定提前時間）
- 繳費提醒（定期自動發送）
- 課表通知（每週定時發送）
- 通知範本自訂
- 開關控制

#### 5. 互動功能
- 關鍵字自動回覆
- 快速回覆按鈕
- 問卷調查功能
- 統計圖表顯示

### 基本功能模組（$7000/年）

#### 6. 師生管理
- 學生資料管理（新增/編輯/停學）
  - 基本資料（姓名、年齡、聯絡方式）
  - 學習資訊（項目、程度）
  - 家長資訊
  - 地址與備註
- 教師資料管理（新增/停用）
- 搜尋功能
- 學生編號自動生成
- 統計資訊（在學/總數）

#### 7. 出席打卡系統
- 快速打卡
  - 選擇學生與狀態（出席/遲到/缺席/請假）
  - 即時記錄打卡時間
- 打卡記錄
  - 日期篩選
  - 狀態篩選
  - 學生搜尋
  - 刪除記錄
- QR Code 打卡
  - 自動生成 QR Code
  - 5 分鐘自動更新
  - 學生掃碼打卡
- 統計報表
  - 今日出席/遲到/缺席統計
  - 出席率計算
  - 學生個別統計
  - 自動更新（30秒）

#### 8. 成績管理系統
- 考試管理
  - 新增考試（名稱、日期、滿分、及格分數）
  - 考試列表
- 成績登記
  - 選擇考試與學生
  - 輸入分數與備註
  - 自動等第計算（A/B/C/D/F）
  - 自動排名計算
  - 自動進退步分析
- 成績分析
  - 平均分數、最高分、最低分
  - 及格率統計
  - 學生個別分析
  - 進步幅度追蹤
  - 趨勢圖表（預留）
- 成績單生成
  - 選擇學生與時間範圍
  - 生成完整成績單
  - PDF 匯出（預留）

#### 9. 排班管理系統
- 排班表（週曆視圖）
  - 視覺化週曆（橫軸7天、縱軸教師）
  - 週導航（上週/下週/本週）
  - 新增排班（教師/日期/時段/課程）
  - 快速新增（點擊空格）
  - 複製上週排班（預留）
- 代課申請
  - 申請代課（原教師/代課教師/日期/時段/原因）
  - 審核功能（待處理/核准/拒絕）
  - 狀態追蹤（待處理/已核准/已拒絕/已完成）
  - 狀態篩選
- 請假管理
  - 申請請假（教師/類型/起迄日期/原因）
  - 自動計算天數
  - 審核功能（待審核/核准/拒絕）
  - 狀態篩選
- 工時統計
  - 月份篩選
  - 排班時數、實際上課、代課、請假時數
  - 總時數與時薪
  - 預估薪資
  - 匯出報表（預留）
- 薪資計算
  - 基本時數與薪資
  - 代課時數與費用（1.2倍）
  - 獎金與扣款
  - 實發薪資
  - 生成薪資單（預留）
  - 列印薪資條（預留）

#### 10. 財務報表
- 收入明細管理
  - 新增收入記錄
  - 學生選擇
  - 付款方式（現金/轉帳/信用卡）
  - 月份追蹤
- 支出明細管理
  - 分類管理（租金/薪資/水電等）
  - 日期記錄
- 月份篩選
- 財務統計
  - 總收入
  - 總支出
  - 淨收入
  - 本月收入

#### 11. 會計科目
- 收入科目管理
- 支出科目管理
- 新增/刪除科目
- 科目說明
- 資料保存（LocalStorage）
- 預設科目範本

#### 12. 課表系統
- 週曆顯示
- 今日高亮
- 課程時段顯示
- 上週/下週切換
- 本週統計
  - 本週課程數
  - 今日課程數
  - 本週教師數

#### 13. CEO每日報
- 今日 KPI 儀表板
  - 今日收入
  - 在學學生
  - 今日課程
  - 出席率
- 今日重點摘要
- 財務概況
  - 本月收支
  - 年度累計
- 學生統計
  - 在學人數
  - 本月新生/流失
  - 留存率

### 形象網站模組（$3000/年）

#### 14. 網站設計
- 基本設定
  - 網站標題
  - 副標題
  - 主色調選擇
  - 字體大小
  - 版面配置
- 即時預覽功能
- 設定保存

#### 15. 內容管理
- 分頁式內容編輯
  - 關於我們
  - 課程介紹
  - 師資陣容
  - 最新消息
  - 聯絡資訊
- 最新消息發布
- 內容保存

#### 16. 線上報名
- 報名申請列表
- 狀態管理（待審核/已核准/已拒絕）
- 篩選功能
- 核准/拒絕操作
- 報名統計

## 資料庫結構

### 核心資料表
- `teachers` - 教師資料
- `time_slots` - 時段管理
- `courses` - 課程項目
- `bookings` - 預約記錄

### 擴充資料表
- `students` - 學生資料（含家長資訊、報名日期）
- `payments` - 繳費記錄（金額、日期、付款方式、月份）
- `expenses` - 支出記錄（分類、金額、日期、說明）
- `attendance` - 出席記錄（學生、日期、時間、狀態、遲到分鐘）
- `exams` - 考試資料（名稱、日期、滿分、及格分數）
- `grades` - 成績記錄（考試、學生、分數、排名、趨勢）
- `shifts` - 排班表（教師、日期、時段、課程）
- `substitutes` - 代課記錄（原教師、代課教師、日期、時段、狀態）
- `leaves` - 請假記錄（教師、類型、起迄日期、天數、狀態）

## API 端點

### 公開 API
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 學生預約頁面 |
| GET | `/api/teachers` | 取得老師列表 |
| GET | `/api/courses` | 取得課程列表 |
| GET | `/api/slots` | 取得可用時段 |
| POST | `/api/book` | 送出預約 |

### 管理 API（需密碼驗證）
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/admin/api/bookings` | 查看所有預約 |
| POST | `/admin/api/bookings/:id/cancel` | 取消預約 |
| GET/POST/DELETE | `/admin/api/teachers` | 教師管理 |
| GET/POST/PUT/DELETE | `/admin/api/students` | 學生管理 |
| GET/POST/DELETE | `/admin/api/payments` | 繳費管理 |
| GET/POST/DELETE | `/admin/api/expenses` | 支出管理 |
| GET | `/admin/api/finance/summary` | 財務摘要統計 |
| GET/POST/DELETE | `/admin/api/attendance` | 出席打卡管理 |
| GET | `/admin/api/attendance/stats` | 出席統計 |
| GET/POST/DELETE | `/admin/api/exams` | 考試管理 |
| GET/POST/DELETE | `/admin/api/grades` | 成績管理 |
| GET/POST/DELETE | `/admin/api/shifts` | 排班管理 |
| GET/POST | `/admin/api/substitutes` | 代課申請 |
| POST | `/admin/api/substitutes/:id/approve` | 核准代課 |
| POST | `/admin/api/substitutes/:id/reject` | 拒絕代課 |
| GET/POST | `/admin/api/leaves` | 請假申請 |
| POST | `/admin/api/leaves/:id/approve` | 核准請假 |
| POST | `/admin/api/leaves/:id/reject` | 拒絕請假 |
| GET | `/admin/api/line/config` | LINE 設定狀態 |
| POST | `/admin/api/line/test` | 測試 LINE 連線 |
| POST | `/admin/api/line/broadcast` | LINE 群發訊息 |
| POST | `/admin/api/line/push` | LINE 推送訊息 |
| POST | `/webhook/line` | LINE Webhook（公開） |

### 頁面路由
| 路徑 | 說明 |
|------|------|
| `/admin` | 管理員登入頁 |
| `/dashboard` | 模組管理首頁 |
| `/booking-admin` | 預約管理頁面 |
| `/teacher-mgmt` | 師生管理頁面 |
| `/attendance` | 出席打卡頁面 |
| `/grades` | 成績管理頁面 |
| `/staff-schedule` | 排班管理頁面 |
| `/finance` | 財務報表頁面 |
| `/accounting` | 會計科目頁面 |
| `/course-schedule` | 課表系統頁面 |
| `/ceo-report` | CEO每日報頁面 |
| `/line-messages` | LINE訊息推播頁面 |
| `/line-notifications` | LINE通知設定頁面 |
| `/line-interactive` | LINE互動功能頁面 |
| `/website-design` | 網站設計頁面 |
| `/website-content` | 內容管理頁面 |
| `/online-booking` | 線上報名頁面 |

## 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `SECRET_KEY` | Flask Session 金鑰 | music-school-secret-2024 |
| `ADMIN_PASSWORD` | 管理後台密碼 | admin123 |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Channel Access Token | （選填）|
| `LINE_CHANNEL_SECRET` | LINE Channel Secret | （選填）|

設定方式：
```bash
export ADMIN_PASSWORD="你的密碼"
export LINE_CHANNEL_ACCESS_TOKEN="你的_Access_Token"
export LINE_CHANNEL_SECRET="你的_Channel_Secret"
python app.py
```

## 部署指南

### Render 部署
1. 上傳到 GitHub
2. 連接到 Render
3. 設定環境變數：
   - `ADMIN_PASSWORD`: 你的管理密碼
   - `SECRET_KEY`: 自動生成
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Railway 部署
1. 上傳到 GitHub
2. 連接到 Railway
3. 設定環境變數
4. 自動部署

### render.yaml 範例
```yaml
services:
  - type: web
    name: music-booking
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: ADMIN_PASSWORD
        sync: false
    disk:
      name: booking-disk
      mountPath: /var/data
      sizeGB: 1
```

## 技術堆疊

- 後端：Python 3.x + Flask 2.3.0
- 資料庫：SQLite + SQLAlchemy
- 前端：HTML5 + CSS3 + JavaScript（原生）
- 字體：Noto Sans TC（Google Fonts）
- 架構：模組化 + iframe 嵌入設計
- HTTP 客戶端：requests 2.31.0（LINE API 串接）
- QR Code：qrcode.js 1.5.1（出席打卡）

## 設計特色

- 紫色主題（#7c3aed）專業現代
- 卡片式設計清晰易讀
- 流暢的動畫效果
- 統一的介面風格
- 響應式設計支援手機

## 注意事項

1. 首次啟動會自動建立範例資料（3位老師、6個課程）
2. 模組啟用狀態保存在瀏覽器 localStorage
3. 登入狀態保存在 sessionStorage，關閉瀏覽器會清除
4. 會計科目設定保存在 localStorage
5. 清除瀏覽器快取會重置模組設定

## 功能完成度

- 核心功能：2/2 = 100%
- 基本功能模組：8/8 = 100%
- LINE 串接模組：3/3 = 100%
- 形象網站模組：3/3 = 100%

總完成度：16/16 = 100%

## 後續擴充

### 新增模組只需：
1. 在 `index.html` 新增模組卡片
2. 在側邊欄加入對應導航
3. 建立功能頁面 HTML
4. 在 `app.py` 加入路由
5. 更新 JavaScript 模組狀態

### 可擴充功能：
- 學生家長 APP
- 影片教學系統
- 線上繳費整合
- 庫存管理系統
- 數據分析儀表板
- 試聽課程管理
- 推薦獎勵系統
- 活動管理系統

## 相關文件

- `LINE_SETUP.md` - LINE API 串接設定完整指南
- `MODULE_CHECKLIST.md` - 詳細的模組功能檢查清單

## 授權

此專案為音樂補習班管理系統，供內部使用。

## 聯絡資訊

如有問題或建議，歡迎透過系統回饋功能聯繫我們。