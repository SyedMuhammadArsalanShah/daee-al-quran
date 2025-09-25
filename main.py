import streamlit as st
import requests
from bs4 import BeautifulSoup
import pyperclip
from fpdf import FPDF
import re

# -------- Streamlit Page Config --------
st.set_page_config(
    page_title="داعی القرآن 📚",
    page_icon="📖",
    layout="wide"
)

# -------- Custom CSS --------
st.markdown("""
<style>
html, body, [class*="css"], .stMarkdown, .stTextInput, .stSelectbox, .stButton, .stAlert ,div{
    font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif !important;
    font-size: 15px !important;
    direction: rtl !important;
    text-align: right !important;
    line-height: 2 !important;
    color: #111827;
}
h1, h2, h3 {
    font-family: 'Noto Nastaliq Urdu', serif !important;
    text-align: center !important;
    color: #1e3a8a !important;
    margin-bottom: 20px;
}
.stTextInput input {
    border: 2px solid #1e3a8a !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    font-size: 15px !important;
}
.stButton button {
    background: linear-gradient(135deg, #1e3a8a, #4338ca) !important;
    color: white !important;
    font-size: 18px !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    transition: 0.3s ease-in-out;
}
.stButton button:hover {
    background: linear-gradient(135deg, #4338ca, #1e3a8a) !important;
    transform: scale(1.05);
}
.card {
    background: #ffffff;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 18px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.12);
    font-size: 18px;
}
.summary-bullet {
    background: #f9fafb;
    padding: 12px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    border-right: 5px solid #1e40af;
    font-size: 17px;
}
.button-style {
    text-decoration:none;
    display:inline-block;
    padding:12px 20px;
    margin:5px 0;
    border-radius:12px;
    font-size:18px;
    color:white;
    text-align:center;
    width:100%;
    transition:0.3s;
}
.pdf-btn {background:#1e40af;}
.copy-btn {background:#f59e0b;}
.whatsapp-btn {background:#25D366;}
.pdf-btn:hover {background:#4338ca;}
.copy-btn:hover {background:#d97706;}
.whatsapp-btn:hover {background:#128C7E;}
.img-center {
    display:block;
    margin-left:auto;
    margin-right:auto;
    border-radius:50%;
    width:180px;
    height:180px;
    margin-bottom:15px;
    border: 4px solid #1e40af;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# -------- Constants --------
BASE_URL = "https://tanzeemdigitallibrary.com"

# -------- Functions --------
def search_books(query):
    url = f"{BASE_URL}/Search/{query}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for link in soup.select("ul#resultlist li a"):
        results.append({"id": link.get("id"), "title": link.text.strip()})
    return results

def get_page_content(book_id, search_text):
    url = f"{BASE_URL}/Home/GetSearchData"
    payload = {"Id": book_id, "IsEqual": True, "IsLike": False, "searchetext": search_text}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    return response.text if response.status_code==200 else f"<p style='color:red'>⚠️ مواد حاصل نہیں ہو سکا (status {response.status_code})</p>"

def generate_ai_summary(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = " ".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
    sentences = re.split(r'(?<=[۔؟!])\s+', text)
    summary = [f"• {s.strip()}" for s in sentences[:5]]
    return summary

def share_whatsapp_button(text):
    url = f"https://api.whatsapp.com/send?text={text}"
    st.markdown(f'''
    <a href="{url}" target="_blank" class="button-style whatsapp-btn">
        📱 واتس ایپ پر شئیر کریں
    </a>
    ''', unsafe_allow_html=True)

def save_pdf_fpdf(text, filename="content.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoNastaliq", '', "fonts/NotoNastaliqUrdu-Regular.ttf", uni=True)
    pdf.set_font("NotoNastaliq", size=14)
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 8, line)
    pdf.output(filename)

# -------- Streamlit UI --------
st.markdown("""
<div style="text-align:center;">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrzS1yZ1cKk7WrfaygfGt7IMzQmCTTztDY1MzKjrVv6u9lSyr9mKZH6ouHr671eKy8ebI&usqp=CAU"
    alt="ڈاکٹر اسرار احمد" class="img-center">
</div>
""", unsafe_allow_html=True)
st.markdown('<h2>داعی القرآن 📚</h2>', unsafe_allow_html=True)

query = st.text_input("🔎 تلاش کریں (اردو/English)", "خلافت کی اہمیت")
search_btn = st.button("🔍 تلاش")

if "results" not in st.session_state:
    st.session_state.results = []
if "query" not in st.session_state:
    st.session_state.query = ""

if search_btn:
    with st.spinner("🔎 تلاش ہو رہی ہے..."):
        st.session_state.results = search_books(query)
        st.session_state.query = query

if st.session_state.results:
    choice = st.selectbox("📌 کتاب/مضمون منتخب کریں", [r["title"] for r in st.session_state.results])
    ids = {r["title"]: r["id"] for r in st.session_state.results}

    if choice:
        with st.spinner("📄 مواد لوڈ ہو رہا ہے..."):
            html = get_page_content(ids[choice], st.session_state.query)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        summary = generate_ai_summary(html)
        st.markdown('<h3>🤖AI خلاصہ</h3>', unsafe_allow_html=True)
        for s in summary:
            st.markdown(f'<div class="summary-bullet">{s}</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 پی ڈی ایف"):
                save_pdf_fpdf(html)
                st.success("✅ PDF محفوظ ہو گیا ہے!")
        with col2:
            if st.button("📋 کاپی کریں"):
                pyperclip.copy(html)
                st.success("✅ مواد کلپ بورڈ میں کاپی ہو گیا!")
        with col3:
            share_whatsapp_button(st.session_state.query)
else:
    st.info("ℹ️ براہ کرم کچھ تلاش کریں تاکہ نتائج دیکھ سکیں۔")
