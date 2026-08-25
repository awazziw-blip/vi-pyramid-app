import io
import json
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

# ==========================================
# 🏛️ 1. Institutional Stock Database (ฐานข้อมูลมูลค่าหุ้น)
# ==========================================
STOCK_DB = {
    "EGCO": {
        "fv": 118.00,
        "tier": "Medium",
        "shares": 1799,
        "avg": 133.40,
        "budget": 300000.0,
    },
    "TISCO": {
        "fv": 110.00,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "SAWAD": {
        "fv": 38.50,
        "tier": "Medium",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "SPA": {
        "fv": 7.00,
        "tier": "Medium",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "WHAUP": {
        "fv": 4.80,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "BDMS": {
        "fv": 27.00,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "CPALL": {
        "fv": 65.00,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "ADVANC": {
        "fv": 403.00,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "WHART": {
        "fv": 11.20,
        "tier": "Defensive",
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
}

# ==========================================
# 🎨 2. Page Configuration & Strict White Text CSS
# ==========================================
st.set_page_config(
    page_title="VI Pyramid & Portfolio Engine", page_icon="📈", layout="wide"
)

st.markdown(
    """
<style>
    /* บังคับพื้นหลังหน้าจอและ Sidebar */
    .stApp { background-color: #0b0f19; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    
    /* 1. บังคับตัวหนังสือสีขาวบริสุทธิ์ทุก Element ทั่วทั้งเว็บ */
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #FFFFFF !important;
    }
    
    /* 2. แก้ปัญหาตัวหนังสือสีดำใน Dropdown / Selectbox ของ Sidebar */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: #FFFFFF !important;
    }
    
    /* รายการตัวเลือกในเมนู Dropdown ที่เด้งลงมา */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #1e293b !important;
        color: #FFFFFF !important;
    }
    li[role="option"] {
        background-color: #1e293b !important;
        color: #FFFFFF !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #334155 !important;
        color: #38bdf8 !important;
    }
    
    /* 3. กล่องพิมพ์ข้อความและตัวเลข (Inputs) */
    input, textarea {
        color: #FFFFFF !important;
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    /* 4. Dashboard Metrics & ตาราง */
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    
    table { width: 100% !important; border-collapse: collapse !important; }
    th { background-color: #1e293b !important; color: #38bdf8 !important; font-weight: bold !important; border: 1px solid #334155 !important; padding: 10px !important; }
    td { background-color: #0f172a !important; color: #FFFFFF !important; border: 1px solid #334155 !important; padding: 8px !important; }
    
    .stDownloadButton>button {
        width: 100%; border-radius: 8px; font-weight: bold; background-color: #1e293b !important; color: #FFFFFF !important; border: 1px solid #38bdf8 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ Institutional VI Engine & Portfolio Scanner")
st.caption(
    "ระบบประเมินมูลค่าหุ้น จัดการไม้ซื้อแบบพีระมิดกลับหัว และระบบจุดขาย No-Loss"
    " TP Gate"
)

# ==========================================
# 🔄 3. State Management & Real-time Auto-Update Engine
# ==========================================
# ฟังก์ชันอัปเดตตัวแปรเมื่อเปลี่ยนชื่อหุ้นใน Dropdown
def handle_stock_selection_change():
  selected = st.session_state.stock_dropdown_key
  if selected in STOCK_DB:
    data = STOCK_DB[selected]
    st.session_state.input_ticker_name = selected
    st.session_state.input_fair_value = float(data["fv"])
    st.session_state.input_risk_tier = data["tier"]
    st.session_state.input_curr_shares = int(data["shares"])
    st.session_state.input_curr_avg = float(data["avg"])
    st.session_state.input_total_budget = float(data["budget"])


# ตั้งค่าเริ่มต้นครั้งแรก (Default First Load)
if "input_ticker_name" not in st.session_state:
  init_data = STOCK_DB["EGCO"]
  st.session_state.stock_dropdown_key = "EGCO"
  st.session_state.input_ticker_name = "EGCO"
  st.session_state.input_fair_value = float(init_data["fv"])
  st.session_state.input_risk_tier = init_data["tier"]
  st.session_state.input_curr_shares = int(init_data["shares"])
  st.session_state.input_curr_avg = float(init_data["avg"])
  st.session_state.input_total_budget = float(init_data["budget"])

# ==========================================
# 📸 4. Gemini Vision AI Scanner (OCR พอร์ต)
# ==========================================
with st.expander("📸 อัปโหลดรูปภาพพอร์ต (Streaming Screenshot Scanner)", expanded=False):
  uploaded_file = st.file_uploader(
      "เลือกไฟล์ภาพแคปหน้าจอพอร์ตหุ้น", type=["jpg", "png", "jpeg"]
  )
  gemini_api_key = st.text_input(
      "ใส่ Gemini API Key (รับฟรีจาก Google AI Studio):", type="password"
  )

  if uploaded_file and gemini_api_key:
    try:
      import google.generativeai as genai

      genai.configure(api_key=gemini_api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")
      img = Image.open(uploaded_file)

      prompt = """
            วิเคราะห์รูปภาพพอร์ตหุ้นนี้ และส่งผลลัพธ์กลับมาเป็น JSON Array เท่านั้น:
            [{"symbol": "ชื่อหุ้น", "shares": จำนวนหุ้น(int), "avg_cost": ต้นทุนเฉลี่ย(float)}]
            ตัด Markdown และคำอธิบายทิ้งทั้งหมด ส่งเฉพาะ JSON
            """
      response = model.generate_content([prompt, img])
      parsed_data = json.loads(
          response.text.replace("```json", "").replace("
