# Vàng vs Tiết kiệm — bản thử nghiệm giá DOJI

## Có gì trong gói này
- `index.html`: app so sánh vàng và tiết kiệm.
- `scripts/fetch_doji_price.py`: thử đọc giá nhẫn tròn 9999 Hưng Thịnh Vượng từ website DOJI bằng trình duyệt Chromium.
- `.github/workflows/update-doji-price.yml`: chạy hằng ngày lúc 09:30 giờ Việt Nam, hoặc chạy thủ công.
- `data/doji-price.json`: được workflow tạo ra sau lần lấy giá thành công đầu tiên.

## Cài vào repo GitHub Pages
1. Tải và giải nén ZIP.
2. Chép các file/thư mục trong gói vào thư mục gốc repo `vang-vs-tiet-kiem`, giữ nguyên cấu trúc.
3. Commit và push lên GitHub.
4. Vào **Settings → Actions → General**, bảo đảm workflow được phép chạy và quyền ghi nội dung repo được bật (workflow có `permissions: contents: write`).
5. Vào tab **Actions** → **Update DOJI gold price** → **Run workflow** để thử lần đầu.
6. Nếu chạy thành công, file `data/doji-price.json` sẽ xuất hiện; website có thể bấm **Nạp giá DOJI gần nhất**.

## Quan trọng
- Đây là scraper thử nghiệm, không phải API chính thức của DOJI. Nếu DOJI đổi cấu trúc trang hoặc đơn vị hiển thị, workflow sẽ báo lỗi thay vì cập nhật thành công.
- Giá trên bảng DOJI có thể được hiển thị theo nghìn đồng/chỉ; script hiện giả định đơn vị đó và đổi sang đồng/lượng. Hãy kiểm tra log lần chạy đầu tiên trước khi tin dùng.
- Workflow chạy mỗi ngày, không cập nhật theo từng biến động trong ngày.
- GitHub Pages chỉ đọc file snapshot đã commit. Nút trên trang nạp snapshot mới nhất, không tự chạy GitHub Actions ngay tại thời điểm bấm.
- Để lưu lịch sử theo ngày cho biểu đồ, cần chỉnh workflow để append từng snapshot vào file lịch sử thay vì chỉ giữ bản giá mới nhất; bản thử nghiệm này mới lưu giá mới nhất.
