# Video Competitor Research Automation

Hệ thống tự động nghiên cứu 30 video đối thủ TikTok và tạo kế hoạch content 20 video bằng Gemini AI.

## Yêu cầu

- Python 3.11+
- Tài khoản Apify (apify.com)
- Google Cloud project (OAuth2 hoặc Service Account)
- Gemini API key (aistudio.google.com)

## Cài đặt

```bash
cd automation
pip install -r requirements.txt
cp .env.example .env
# Điền APIFY_API_TOKEN và GEMINI_API_KEY vào .env
```

## Cấu hình credentials

### 1. Apify API Token
- Đăng ký tại apify.com
- Vào Settings → Integrations → API token

### 2. Google Auth (chọn 1 trong 2)

**Option A — Personal Gmail (recommended):**
1. Vào [console.cloud.google.com](https://console.cloud.google.com)
2. Tạo project mới
3. Bật 3 API: **Google Drive API**, **Google Sheets API**, **Google Docs API**
4. Vào APIs & Services → Credentials → Create OAuth 2.0 Client ID (Desktop app)
5. Download JSON → lưu thành `automation/client_secret.json`
6. Vào OAuth consent screen → Add test users → thêm Gmail của mày
7. Chạy 1 lần duy nhất:
```bash
python setup_oauth.py
```
Browser mở ra → đăng nhập Gmail → cho phép → xong. Token lưu vào `token.json`.

**Option B — Google Workspace (service account):**
> **Lưu ý:** Service account KHÔNG thể upload file binary lên Drive cá nhân (quota = 0). Chỉ dùng được với Shared Drive hoặc domain-wide delegation.

1. Tạo service account + download JSON key
2. Set `GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json` trong `.env`
3. Set `USER_EMAIL=your@email.com` để auto-share output files

### 3. Gemini API Key
- Vào [aistudio.google.com](https://aistudio.google.com)
- Get API key

## Sử dụng

```bash
# Full run — 30 video
python run.py --keyword "kem tri mun" --limit 30

# Dry run — chỉ scrape + ghi Sheets, tính cost estimate
python run.py --keyword "kem tri mun" --limit 30 --dry-run

# Test nhanh với 3 video
python run.py --keyword "kem tri mun" --limit 3

# Bỏ qua download (dùng video đã tải trước)
python run.py --keyword "kem tri mun" --limit 30 --skip-download

# Bỏ qua upload Drive (chỉ analyze)
python run.py --keyword "kem tri mun" --limit 30 --skip-upload
```

## Output

Sau khi chạy xong, hệ thống tự động tạo:
1. **Google Sheet** — `{keyword} - Bang chi so tuong tac Top 30`: metadata 30 video
2. **Google Drive folder** — `{keyword} - Top 30 Videos`: 30 file .mp4
3. **Google Doc** — `[{keyword}] Phan tich doi thu + Ke hoach content 20 video`: báo cáo Gemini

Links được gửi qua Slack/Telegram (nếu cấu hình).

## Ước tính chi phí

Video TikTok 15-60s ≈ 4,500-18,000 tokens (Gemini tokenize ~300 tokens/giây).

| Model | ~Chi phí cho 30 video |
|-------|----------------------|
| gemini-2.5-flash | ~$0.06 USD |
| gemini-2.5-pro | ~$0.50 USD |
| gemini-2.0-flash | ~$0.04 USD |

Dùng `--dry-run` để xem estimate chính xác trước khi chạy thật.

## Kiến trúc

```
run.py
  ├─ setup_oauth.py            → One-time OAuth2 consent flow
  ├─ clients/auth.py           → Unified credential provider (OAuth2 / SA)
  ├─ pipeline/scraper.py       → Apify TikTok scraper
  ├─ pipeline/sheet_logger.py  → Google Sheets
  ├─ pipeline/downloader.py    → Download .mp4
  ├─ pipeline/uploader.py      → Google Drive
  ├─ pipeline/analyzer.py      → Gemini Files API (3 batch + synthesis)
  └─ pipeline/doc_writer.py    → Google Docs
```
