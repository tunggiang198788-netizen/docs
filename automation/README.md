# Video Competitor Research Automation

Hệ thống tự động nghiên cứu 30 video đối thủ TikTok và tạo kế hoạch content 20 video bằng Gemini AI.

## Yêu cầu

- Python 3.11+
- Tài khoản Apify (apify.com)
- Google Cloud project với Service Account
- Gemini API key (aistudio.google.com)

## Cài đặt

```bash
cd automation
pip install -r requirements.txt
cp .env.example .env
# Điền credentials vào .env
```

## Cấu hình credentials

### 1. Apify API Token
- Đăng ký tại apify.com
- Vào Settings → Integrations → API token

### 2. Google Service Account
1. Vào [console.cloud.google.com](https://console.cloud.google.com)
2. Tạo project mới
3. Bật 3 API: **Google Drive API**, **Google Sheets API**, **Google Docs API**
4. Vào IAM & Admin → Service Accounts → Tạo service account
5. Tạo key JSON → download → đặt vào `automation/service_account.json`
6. Copy email của service account (dạng `xxx@xxx.iam.gserviceaccount.com`)
7. Chia sẻ folder Google Drive của mày với email đó (Editor permission)

### 3. Gemini API Key
- Vào [aistudio.google.com](https://aistudio.google.com)
- Get API key

## Sử dụng

```bash
# Full run — 30 video
python run.py --keyword "kem tri mun" --limit 30

# Dry run — chỉ scrape + ghi Sheets, tính cost estimate, không tốn Gemini API
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

| Model | ~Chi phí cho 30 video |
|-------|----------------------|
| gemini-1.5-pro | ~$30-50 USD |
| gemini-1.5-flash | ~$1-3 USD |
| gemini-2.0-flash | ~$1-3 USD |

Dùng `--dry-run` để xem estimate chính xác trước khi chạy thật.

## Kiến trúc

```
run.py
  ├─ pipeline/scraper.py      → Apify TikTok scraper
  ├─ pipeline/sheet_logger.py → Google Sheets
  ├─ pipeline/downloader.py   → Download .mp4
  ├─ pipeline/uploader.py     → Google Drive
  ├─ pipeline/analyzer.py     → Gemini Files API (3 batch + synthesis)
  └─ pipeline/doc_writer.py   → Google Docs
```
