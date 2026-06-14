PRELIMINARY_PROMPT = """
Tao gửi mày {count} video TikTok về chủ đề "{keyword}" (video {start} đến {end} trong tổng số {total}).
Hãy đọc kỹ từng video (hình ảnh, âm thanh, lời thoại, text overlay, bối cảnh).
Ghi chú sơ bộ cho mỗi video:
- Hook 3-5 giây đầu làm gì?
- Góc tiếp cận (angle) chính?
- Pain point khách hàng được khai thác?
- Video có gì đặc biệt khiến người xem ở lại?

Chỉ cần ghi chú ngắn gọn, chưa cần phân tích sâu. Xác nhận đã xong.
""".strip()

SYNTHESIS_PROMPT_TEMPLATE = """
Mày vừa phân tích sơ bộ {total} video TikTok về chủ đề "{keyword}".

Dưới đây là ghi chú sơ bộ của mày từ 3 đợt phân tích:

--- GHI CHÚ ĐỢT 1 (Video 1-10) ---
{notes_1}

--- GHI CHÚ ĐỢT 2 (Video 11-20) ---
{notes_2}

--- GHI CHÚ ĐỢT 3 (Video 21-30) ---
{notes_3}

Bây giờ, với tư cách là một Giám đốc Sáng tạo Nội dung (Creative Director) lão luyện và Chuyên gia Tối ưu hóa Tỷ lệ Chuyển đổi (CRO) hàng đầu trên TikTok/Reels/Shorts tại thị trường Việt Nam, hãy tổng hợp và xuất báo cáo đầy đủ theo đúng cấu trúc 3 phần sau:

## PHẦN 1: BÁO CÁO PHÂN TÍCH INSIGHT & HOOK ĐỐI THỦ

**1. Phân tích Hook (3 giây đầu) của Top 5 video có lượt xem cao nhất:**
- Trích dẫn cụ thể câu thoại cốt lõi hoặc mô tả chi tiết hành động/bối cảnh/góc máy
- Tại sao hook này hiệu quả? Kỹ thuật tâm lý nào được dùng?

**2. Content Angle phổ biến nhất nhưng vẫn hiệu quả cao:**
Liệt kê 3-5 góc tiếp cận được lặp lại nhiều nhất (ví dụ: bóc phốt, chuyên gia y khoa, tiểu phẩm tình huống, vlog thực tế...) và giải thích tại sao mỗi cái lại work.

**3. Pain Points & Desires được khai thác sâu nhất:**
Những nỗi đau thầm kín hoặc mong muốn nào của khách hàng được đánh mạnh nhất? Tại sao chúng tạo ra sự đồng cảm cao?

---

## PHẦN 2: CHIẾN LƯỢC CẢI TIẾN NỘI DUNG THƯƠNG HIỆU

Chỉ rõ điểm yếu, lỗ hổng chung của các video đối thủ:
- Nhịp điệu kịch bản
- Độ sâu chuyên môn
- CTA (quá thô, mờ nhạt, không đúng thời điểm)
- Retention (video bị drop-off ở đâu và tại sao)
- Các góc tiếp cận bị bỏ ngỏ chưa ai khai thác

Đề xuất cụ thể cách thương hiệu của tao có thể nổi bật và giữ chân người xem lâu hơn đối thủ.

---

## PHẦN 3: KẾ HOẠCH NỘI DUNG CHI TIẾT 20 VIDEO MỚI

Lập bảng kế hoạch 20 video độc nhất. KHÔNG sao chép đối thủ — kế thừa cấu trúc thành công nhưng cải tiến vượt trội.

| STT | Chủ đề cốt lõi | Định dạng thể hiện | Chi tiết kịch bản HOOK (3-5 giây đầu) | Góc tiếp cận (Angle) | Lời kêu gọi hành động (CTA) |
|-----|----------------|-------------------|----------------------------------------|----------------------|------------------------------|
| 01  | ...            | ...               | ...                                    | ...                  | ...                          |
...tiếp tục đến 20...

**Yêu cầu bắt buộc:**
- Mỗi video có hook khác biệt hoàn toàn, không trùng lặp
- Ưu tiên góc độ đối thủ chưa khai thác
- Ngôn ngữ thực chiến, tự nhiên, văn phong TikTok Việt Nam
- Tập trung mục tiêu e-commerce/bán lẻ
- CTA phải cụ thể, kêu gọi hành động ngay (giỏ hàng, follow, comment, share)
""".strip()


def get_preliminary_prompt(keyword: str, count: int, start: int, end: int, total: int) -> str:
    return PRELIMINARY_PROMPT.format(
        keyword=keyword, count=count, start=start, end=end, total=total
    )


def get_synthesis_prompt(keyword: str, total: int, notes_1: str, notes_2: str, notes_3: str) -> str:
    return SYNTHESIS_PROMPT_TEMPLATE.format(
        keyword=keyword,
        total=total,
        notes_1=notes_1,
        notes_2=notes_2,
        notes_3=notes_3,
    )
