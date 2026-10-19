import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

URL = "https://banggia.doji.vn/gold-price"
PRODUCT = "NHẪN TRÒN 9999 HƯNG THỊNH VƯỢNG"

def parse_number(s):
    return float(s.replace(".", "").replace(",", ".")) if "." in s and "," not in s else float(s.replace(",", ""))

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale="vi-VN")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        await page.wait_for_timeout(4000)
        body = await page.locator("body").inner_text()
        await browser.close()

    # Find the exact product row, then extract the first two plausible price figures.
    lines = [re.sub(r"\s+", " ", x).strip() for x in body.splitlines() if x.strip()]
    candidates = [line for line in lines if PRODUCT in line.upper()]
    if not candidates:
        candidates = [line for line in lines if "HƯNG THỊNH VƯỢNG" in line.upper() and "9999" in line.upper()]
    if not candidates:
        raise RuntimeError("Không tìm thấy dòng sản phẩm Nhẫn tròn 9999 Hưng Thịnh Vượng trên DOJI.")

    row = candidates[0]
    # Remove the purity marker (9999) from the product name before extracting prices.
    price_text = re.sub(r"(?i)NHẪN\s*TRÒN\s*9999\s*HƯNG\s*THỊNH\s*VƯỢNG", "", row)
    nums = re.findall(r"(?<![A-Za-z])\d[\d.,]*", price_text)
    values = []
    for token in nums:
        cleaned = token.replace(",", "").replace(".", "")
        if cleaned.isdigit():
            val = int(cleaned)
            # Filter tiny sequence/index values; prices are normally several thousand thousand VND/chỉ.
            if val >= 1000:
                values.append(val)
    if len(values) < 2:
        # Some responsive layouts split product name and prices into adjacent lines.
        pos = lines.index(row)
        nearby = " ".join(lines[max(0, pos-1):min(len(lines), pos+5)])
        nearby = re.sub(r"(?i)NHẪN\s*TRÒN\s*9999\s*HƯNG\s*THỊNH\s*VƯỢNG", "", nearby)
        nums = re.findall(r"(?<![A-Za-z])\d[\d.,]*", nearby)
        values = []
        for token in nums:
            cleaned = token.replace(",", "").replace(".", "")
            if cleaned.isdigit() and int(cleaned) >= 1000:
                values.append(int(cleaned))
    if len(values) < 2:
        raise RuntimeError("Tìm thấy tên sản phẩm nhưng không trích được đủ giá mua/bán. Không ghi đè dữ liệu cũ.")

    buy_raw, sell_raw = values[0], values[1]

    # DOJI's displayed tables commonly express prices in thousand VND per chỉ.
    # Convert nghìn đồng/chỉ -> đồng/lượng (1 lượng = 10 chỉ).
    # Guard against unexpectedly large values, which likely means the page unit changed.
    if buy_raw > 1_000_000 or sell_raw > 1_000_000:
        raise RuntimeError(f"Đơn vị giá bất thường: mua={buy_raw}, bán={sell_raw}. Cần kiểm tra scraper.")
    buy_vnd_per_luong = buy_raw * 1000 * 10
    sell_vnd_per_luong = sell_raw * 1000 * 10

    out = {
        "source": URL,
        "product": PRODUCT,
        "unitOnSource": "nghìn đồng/chỉ (cần kiểm tra nếu DOJI đổi định dạng)",
        "buyVndPerLuong": buy_vnd_per_luong,
        "sellVndPerLuong": sell_vnd_per_luong,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "rawRow": row
    }
    Path("data").mkdir(exist_ok=True)
    Path("data/doji-price.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
