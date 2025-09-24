from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time, json

# ================= SETTINGS =================
URL = "https://tanzeemdigitallibrary.com/Book/Farmoodat/20/70197/82058/120156"
LOAD_DELAY = 5   # Har page ke baad rukne ka waqt (seconds)
# ============================================

# Browser setup
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(URL)
wait = WebDriverWait(driver, 20)

book_texts = []
page_number = 1

while True:
    try:
        # Urdu text properly lo (innerText)
        current_text = driver.execute_script(
            "return document.getElementById('divPageContent').innerText;"
        ).strip()

        # Save text agar naya ho
        if current_text and (len(book_texts) == 0 or current_text != book_texts[-1]):
            print(f"Page {page_number} scraped")

            # JSON list me save (RTL support ke liye bas UTF-8 rakho)
            book_texts.append({
                "صفحہ": page_number,
                "متن": current_text
            })

            # TXT file me bhi likho
            with open("book_full.txt", "a", encoding="utf-8") as f:
                f.write(f"\n\n=== صفحہ {page_number} ===\n{current_text}\n")

        # Next button locate
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.ID, "NextPage")))
        except:
            print("📘 No more pages found. Done!")
            break

        if not next_btn.is_displayed() or not next_btn.is_enabled():
            print("📘 Next button not available anymore. Done!")
            break

        # Click next
        old_text = current_text
        next_btn.click()

        # Wait until *new* text appears
        wait.until(
            lambda d: d.execute_script("return document.getElementById('divPageContent').innerText;").strip() != old_text
        )

        # Page load ka time
        time.sleep(LOAD_DELAY)
        page_number += 1

    except Exception as e:
        print(f" Error on page {page_number}: {e}")
        break

# Save JSON (RTL Urdu keys ke sath)
book_json = {
    "کتاب": "فرمودات",   # Example: yahan aap book ka asal title dal sakte ho
    "کل_صفحات": len(book_texts),
    "صفحات": book_texts
}

with open("book_full.json", "w", encoding="utf-8") as f:
    json.dump(book_json, f, ensure_ascii=False, indent=4)

print(f"\n✅ Scraping completed.\n📘 کل صفحات: {len(book_texts)}")
print("📝 Text saved to book_full.txt")
print("📑 JSON saved to book_full.json")

driver.quit()
