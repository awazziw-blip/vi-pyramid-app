import io
import json
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

# ==============================================================================
# 🏛️ 1. Master Institutional Valuation Database (ข้อมูลสำเร็จรูปที่ผ่านการคำนวณแล้ว)
# ==============================================================================
MASTER_STOCK_DB = {
    "EGCO": {
        "name": "บมจ. ผลิตไฟฟ้า",
        "sector": "Utilities / Energy",
        "tier": "Medium",
        "fv": 118.00,
        "default_shares": 1799,
        "default_avg": 133.40,
        "default_budget": 300000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median 10Y PE (10.5x) × EPS 11.20",
                "Fair Value (บาท)": "117.60",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "29.40",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 5.33%, r 7.95%, g 1.50% × BVPS 210.00 (0.59x)"
                ),
                "Fair Value (บาท)": "124.60",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "31.15",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 6.50 × (1 + 0.015) / (0.0795 - 0.015)",
                "Fair Value (บาท)": "102.29",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "25.57",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "2-Stage Dividend Discount Model (Growth 1.5%)",
                "Fair Value (บาท)": "127.50",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "31.88",
            },
        ],
    },
    "TISCO": {
        "name": "บมจ. ทิสโก้ไฟแนนเชียลกรุ๊ป",
        "sector": "Banking",
        "tier": "Defensive",
        "fv": 110.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median 10Y PE (11.5x) × EPS 8.00",
                "Fair Value (บาท)": "92.00",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "18.40",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 14.54%, r 7.50%, g 1.00% × BVPS 55.00 (2.08x)"
                ),
                "Fair Value (บาท)": "114.40",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "34.32",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 7.75 × (1 + 0.010) / (0.0750 - 0.010)",
                "Fair Value (บาท)": "120.42",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "30.10",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "2-Stage Dividend Discount Model (Payout 96.8%)",
                "Fair Value (บาท)": "108.72",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "27.18",
            },
        ],
    },
    "SAWAD": {
        "name": "บมจ. ศรีสวัสดิ์ คอร์ปอเรชั่น",
        "sector": "Finance / Non-Bank",
        "tier": "Medium",
        "fv": 38.50,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Normalized PE (12.0x) × EPS 3.65",
                "Fair Value (บาท)": "43.80",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "10.95",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 14.60%, r 10.05%, g 2.50% × BVPS 25.00 (1.60x)"
                ),
                "Fair Value (บาท)": "40.00",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "12.00",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 1.80 × (1 + 0.025) / (0.1005 - 0.025)",
                "Fair Value (บาท)": "24.44",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "4.89",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "Residual Income / 2-Stage Cash Flow",
                "Fair Value (บาท)": "42.64",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "10.66",
            },
        ],
    },
    "SPA": {
        "name": "บมจ. สยามเวลเนสกรุ๊ป",
        "sector": "Services / Tourism",
        "tier": "Medium",
        "fv": 7.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Normalized PE (26.0x) × EPS 0.36",
                "Fair Value (บาท)": "9.36",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "2.81",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 18.95%, r 9.70%, g 2.50% × BVPS 1.90 (2.28x)"
                ),
                "Fair Value (บาท)": "4.33",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "0.87",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.20 × (1 + 0.025) / (0.0970 - 0.025)",
                "Fair Value (บาท)": "2.85",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "0.57",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "2-Stage Cash Flow (Growth 5Y @ 8% + Terminal)",
                "Fair Value (บาท)": "9.17",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "2.75",
            },
        ],
    },
    "WHAUP": {
        "name": "บมจ. ดับบลิวเอชเอ ยูทิลิตี้ส์ แอนด์ พาวเวอร์",
        "sector": "Utilities / Industrial",
        "tier": "Defensive",
        "fv": 4.80,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (11.5x) × EPS 0.40",
                "Fair Value (บาท)": "4.60",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "1.38",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 11.11%, r 7.50%, g 2.00% × BVPS 3.60 (1.66x)"
                ),
                "Fair Value (บาท)": "5.96",
                "น้ำหนัก": "15%",
                "Blended (บาท)": "0.89",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.25 × (1 + 0.020) / (0.0750 - 0.020)",
                "Fair Value (บาท)": "4.64",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "1.39",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "Dividend / FCFE Discount 5Y + Terminal",
                "Fair Value (บาท)": "4.60",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "1.15",
            },
        ],
    },
    "BDMS": {
        "name": "บมจ. กรุงเทพดุสิตเวชการ",
        "sector": "Healthcare",
        "tier": "Defensive",
        "fv": 27.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (27.0x) × EPS 1.00",
                "Fair Value (บาท)": "27.00",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "8.10",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 15.38%, r 7.50%, g 3.50% × BVPS 6.50 (2.97x)"
                ),
                "Fair Value (บาท)": "19.31",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "3.86",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.75 × (1 + 0.035) / (0.0750 - 0.035)",
                "Fair Value (บาท)": "19.41",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "3.88",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "FCFE 2-Stage Growth @ 6.5% + Terminal @ 3.5%",
                "Fair Value (บาท)": "37.20",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "11.16",
            },
        ],
    },
    "CPALL": {
        "name": "บมจ. ซีพี ออลล์",
        "sector": "Commerce / Consumer",
        "tier": "Defensive",
        "fv": 65.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (27.0x) × EPS 2.40",
                "Fair Value (บาท)": "64.80",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "19.44",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 17.14%, r 7.60%, g 3.00% × BVPS 14.00 (3.07x)"
                ),
                "Fair Value (บาท)": "43.04",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "8.61",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 1.35 × (1 + 0.030) / (0.0760 - 0.030)",
                "Fair Value (บาท)": "30.23",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "6.05",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "FCFE 2-Stage Growth @ 7.0% + Terminal @ 3.0%",
                "Fair Value (บาท)": "103.00",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "30.90",
            },
        ],
    },
    "ADVANC": {
        "name": "บมจ. แอดวานซ์ อินโฟร์ เซอร์วิส",
        "sector": "Defensive ICT",
        "tier": "Defensive",
        "fv": 403.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (25.0x) × EPS 13.00",
                "Fair Value (บาท)": "325.00",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "81.25",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 39.39%, r 7.50%, g 2.50% × BVPS 33.00 (7.38x)"
                ),
                "Fair Value (บาท)": "243.47",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "48.69",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 10.50 × (1 + 0.025) / (0.0750 - 0.025)",
                "Fair Value (บาท)": "215.25",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "53.81",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "High FCF Margin Infrastructure Model",
                "Fair Value (บาท)": "730.83",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "219.25",
            },
        ],
    },
    "WHART": {
        "name": "ทรัสต์เพื่อการลงทุนในอสังหาริมทรัพย์และสิทธิการเช่า ดับบลิวเอชเอ พรีเมี่ยม โกรท",
        "sector": "Industrial REIT",
        "tier": "Defensive",
        "fv": 11.20,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median P/E (13.5x) × EPS 0.82",
                "Fair Value (บาท)": "11.07",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "2.77",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 7.59%, r 7.50%, g 1.00% × NAV 10.80 (1.01x)"
                ),
                "Fair Value (บาท)": "10.95",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "2.74",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPU 0.79 × (1 + 0.010) / (0.0750 - 0.010)",
                "Fair Value (บาท)": "12.27",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "3.07",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "REIT DPU Discount Model (Terminal @ 1.0%)",
                "Fair Value (บาท)": "10.51",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "2.63",
            },
        ],
    },
    "AOT": {
        "name": "บมจ. ท่าอากาศยานไทย",
        "sector": "Transportation / Tourism",
        "tier": "Medium",
        "fv": 64.00,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (38.0x) × EPS 1.45",
                "Fair Value (บาท)": "55.10",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "13.78",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 16.50%, r 8.50%, g 3.00% × BVPS 8.80 (2.45x)"
                ),
                "Fair Value (บาท)": "21.60",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "4.32",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.79 × (1 + 0.030) / (0.0850 - 0.030)",
                "Fair Value (บาท)": "14.80",
                "น้ำหนัก": "15%",
                "Blended (บาท)": "2.22",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "Monopoly Concession Free Cash Flow Model",
                "Fair Value (บาท)": "109.20",
                "น้ำหนัก": "40%",
                "Blended (บาท)": "43.68",
            },
        ],
    },
    "LH": {
        "name": "บมจ. แลนด์แอนด์เฮ้าส์",
        "sector": "Property Development",
        "tier": "Medium",
        "fv": 6.20,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Normalized PE (11.0x) × EPS 0.52",
                "Fair Value (บาท)": "5.72",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "1.43",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 12.00%, r 8.80%, g 1.50% × BVPS 4.20 (1.44x)"
                ),
                "Fair Value (บาท)": "6.04",
                "น้ำหนัก": "25%",
                "Blended (บาท)": "1.51",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.45 × (1 + 0.015) / (0.0880 - 0.015)",
                "Fair Value (บาท)": "6.26",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "1.88",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "Hotel & Rental Asset Cash Flow Valuation",
                "Fair Value (บาท)": "6.90",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "1.38",
            },
        ],
    },
    "WHA": {
        "name": "บมจ. ดับบลิวเอชเอ คอร์ปอเรชั่น",
        "sector": "Industrial Estate",
        "tier": "Medium",
        "fv": 5.60,
        "default_shares": 0,
        "default_avg": 0.0,
        "default_budget": 100000.0,
        "models": [
            {
                "โมเดลประเมินมูลค่า": "1. Historical P/E",
                "ตัวแปรที่ใช้": "Median PE (17.5x) × EPS 0.31",
                "Fair Value (บาท)": "5.43",
                "น้ำหนัก": "30%",
                "Blended (บาท)": "1.63",
            },
            {
                "โมเดลประเมินมูลค่า": "2. Justified PBV",
                "ตัวแปรที่ใช้": (
                    "ROE 13.50%, r 9.00%, g 2.50% × BVPS 2.45 (1.69x)"
                ),
                "Fair Value (บาท)": "4.15",
                "น้ำหนัก": "20%",
                "Blended (บาท)": "0.83",
            },
            {
                "โมเดลประเมินมูลค่า": "3. Gordon DDM",
                "ตัวแปรที่ใช้": "DPS 0.18 × (1 + 0.025) / (0.0900 - 0.025)",
                "Fair Value (บาท)": "2.84",
                "น้ำหนัก": "15%",
                "Blended (บาท)": "0.43",
            },
            {
                "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
                "ตัวแปรที่ใช้": "Data Center & Land Transfer Cash Flow",
                "Fair Value (บาท)": "7.74",
                "น้ำหนัก": "35%",
                "Blended (บาท)": "2.71",
            },
        ],
    },
}

# ==============================================================================
# 🎨 2. Strict Institutional Dark Theme & Pure White Text CSS
# ==============================================================================
st.set_page_config(
    page_title="Institutional VI Valuation & Inverted Pyramid Engine",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    
    /* บังคับตัวหนังสือสีขาวบริสุทธิ์ (#FFFFFF) ทั่วทั้งระบบ */
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #FFFFFF !important;
    }
    
    /* Dropdown / Selectbox ปรับสีขาวชัดเจน */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: #FFFFFF !important;
    }
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
    
    /* กล่องข้อความและตัวเลขอินพุต */
    input, textarea {
        color: #FFFFFF !important;
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    /* Metrics Header Cards */
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: bold !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    
    /* ตารางผลลัพธ์ระดับสถาบัน */
    table { width: 100% !important; border-collapse: collapse !important; margin-bottom: 25px !important; }
    th { background-color: #1e293b !important; color: #38bdf8 !important; font-weight: bold !important; border: 1px solid #334155 !important; padding: 10px !important; }
    td { background-color: #0f172a !important; color: #FFFFFF !important; border: 1px solid #334155 !important; padding: 8px !important; }
    
    .stDownloadButton>button {
        width: 100%; border-radius: 8px; font-weight: bold; background-color: #1e293b !important; color: #FFFFFF !important; border: 1px solid #38bdf8 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ Institutional VI Valuation & Inverted Pyramid Engine")
st.caption(
    "ระบบประเมินมูลค่าหุ้นอัตโนมัติ คำนวณไม้ซื้อพีระมิดกลับหัว 15/20/30/35% และ"
    " No-Loss TP Gate"
)

# ==============================================================================
# 🔄 3. State Management & Instant Auto-Fill
# ==============================================================================
stock_names = list(MASTER_STOCK_DB.keys())


def apply_selected_stock():
  chosen = st.session_state.stock_choice
  data = MASTER_STOCK_DB[chosen]
  st.session_state.shares_val = data["default_shares"]
  st.session_state.avg_val = data["default_avg"]
  st.session_state.budget_val = data["default_budget"]


if "stock_choice" not in st.session_state:
  st.session_state.stock_choice = "EGCO"
  apply_selected_stock()

# ==============================================================================
# 📸 4. Gemini Vision OCR Scanner (อ่านภาพพอร์ตอัตโนมัติ)
# ==============================================================================
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
      res = model.generate_content([prompt, img])
      parsed = json.loads(
          res.text.replace("```json", "").replace("```", "").strip()
      )
      st.success("✅ ดึงข้อมูลพอร์ตสำเร็จ!")
      st.json(parsed)

      if parsed:
        sym = parsed[0].get("symbol", "").upper()
        if sym in MASTER_STOCK_DB:
          st.session_state.stock_choice = sym
        st.session_state.shares_val = int(parsed[0].get("shares", 0))
        st.session_state.avg_val = float(parsed[0].get("avg_cost", 0.0))
        st.rerun()
    except Exception as e:
      st.error(f"เกิดข้อผิดพลาดในการอ่านภาพ: {e}")

# ==============================================================================
# ⚙️ 5. Sidebar: One-Click Stock Selector & Portfolio Input
# ==============================================================================
st.sidebar.header("🎯 เลือกหุ้นที่ต้องการวิเคราะห์")

# 1. กล่องเลือกหุ้น (เลือกปุ๊บคำนวณใหม่ทั้งระบบทันที)
selected_stock = st.sidebar.selectbox(
    "เลือกหุ้นจากฐานข้อมูลสถาบัน:",
    options=stock_names,
    key="stock_choice",
    on_change=apply_selected_stock,
)

active_info = MASTER_STOCK_DB[selected_stock]
fair_value = active_info["fv"]
risk_tier = active_info["tier"]

st.sidebar.info(
    f"🏢 **{active_info['name']}**\n\n"
    f"🔹 **กลุ่มอุตสาหกรรม:** {active_info['sector']}\n\n"
    f"⭐ **Fair Value:** **{fair_value:.2f} บาท**\n\n"
    f"🛡️ **Risk Tier:** **{risk_tier}**"
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 ข้อมูลพอร์ต (ปรับได้อิสระ)")
curr_shares = st.sidebar.number_input(
    "จำนวนหุ้นที่มีอยู่เดิม", key="shares_val", step=100
)
curr_avg = st.sidebar.number_input(
    "ราคาต้นทุนเฉลี่ยเดิม (บาท)", key="avg_val", step=0.1, format="%.2f"
)
curr_cost = curr_shares * curr_avg

st.sidebar.subheader("💰 งบประมาณลงทุน")
total_budget = st.sidebar.number_input(
    "งบลงทุนทั้งหมดที่ตั้งเป้าไว้ (บาท)",
    key="budget_val",
    step=10000.0,
    format="%.2f",
)
pyramid_budget = max(0.0, total_budget - curr_cost)
st.sidebar.info(f"💵 งบสำรองซื้อพีระมิด: **{pyramid_budget:,.2f} บาท**")

# ==============================================================================
# 📐 6. Execution Engine: Dynamic MOS, Pyramid & No-Loss TP
# ==============================================================================
# กำหนด MOS และ TP ตาม Risk Tier
if risk_tier == "Defensive":
  mos_rates = [0.12, 0.16, 0.20, 0.24]
  tp_rates = [0.12, 0.16, 0.20]
elif risk_tier == "Medium":
  mos_rates = [0.18, 0.27, 0.36, 0.45]
  tp_rates = [0.18, 0.25, 0.32]
else:
  mos_rates = [0.25, 0.36, 0.48, 0.60]
  tp_rates = [0.25, 0.35, 0.45]

# คำนวณไม้ซื้อพีระมิดกลับหัว (15%, 20%, 30%, 35%)
buy_alloc = [0.15, 0.20, 0.30, 0.35]
buy_prices = [fair_value * (1 - r) for r in mos_rates]
buy_funds = [pyramid_budget * a for a in buy_alloc]
buy_shares = [
    int(f / p) if p > 0 else 0 for f, p in zip(buy_funds, buy_prices)
]

# คำนวณต้นทุนเฉลี่ยสะสมรายไม้ (Weighted Cumulative Cost)
cum_s = curr_shares
cum_c = curr_cost
avg_costs = []
for s, p in zip(buy_shares, buy_prices):
  cum_s += s
  cum_c += s * p
  avg_costs.append(cum_c / cum_s if cum_s > 0 else 0.0)

final_avg_price = avg_costs[-1] if avg_costs else curr_avg

# คำนวณจุดขาย TP 1-3 พร้อมระบบ No-Loss TP Gate
tp_prices = [fair_value * (1 + r) for r in tp_rates]
tp_alloc = [0.30, 0.35, 0.35]

table_rows = []

# แถว TP3 -> TP2 -> TP1
for i in [2, 1, 0]:
  tp_p = tp_prices[i]
  alloc_pct = tp_alloc[i] * 100
  tp_name = f"TP {i+1} ({'Peak' if i==2 else 'Mid' if i==1 else 'Base'})"

  if curr_shares > 0 and tp_p > curr_avg:
    s_sell = int(curr_shares * tp_alloc[i])
    val_sell = s_sell * tp_p
    profit = (tp_p - curr_avg) * s_sell
    gain_pct = ((tp_p - curr_avg) / curr_avg) * 100
    table_rows.append({
        "ประเภทคำสั่ง": "🔴 Take Profit",
        "โซนกลยุทธ์": tp_name,
        "ราคาเป้าหมาย (บาท)": f"{tp_p:.2f}",
        "จำนวนหุ้น (เข้า / ออก)": f"-{s_sell:,} หุ้น",
        "สัดส่วน Action (%)": f"ขาย {alloc_pct:.0f}%",
        "จำนวนเงิน (ซื้อ / ขาย) (บาท)": f"+{val_sell:,.2f}",
        "เงินสะสม / เงินรับรวม (บาท)": "-",
        "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": f"กำไร +{profit:,.2f} (+{gain_pct:.1f}%)",
        "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
            f"ปลดล็อกกำไรไม้ {i+1} จากพอร์ตปัจจุบัน"
        ),
    })
  else:
    table_rows.append({
        "ประเภทคำสั่ง": "🔴 Take Profit",
        "โซนกลยุทธ์": tp_name,
        "ราคาเป้าหมาย (บาท)": f"{tp_p:.2f}",
        "จำนวนหุ้น (เข้า / ออก)": "0 หุ้น",
        "สัดส่วน Action (%)": "ระงับการขาย",
        "จำนวนเงิน (ซื้อ / ขาย) (บาท)": "+0.00",
        "เงินสะสม / เงินรับรวม (บาท)": "-",
        "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": "⚠️ No-Loss Gate (ราคาต่ำกว่าทุน)",
        "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
            "ระงับการขาย ป้องกันการขาดทุนเงินต้น"
        ),
    })

# แถว Fair Value
table_rows.append({
    "ประเภทคำสั่ง": "⚖️ Fair Value",
    "โซนกลยุทธ์": "Intrinsic",
    "ราคาเป้าหมาย (บาท)": f"{fair_value:.2f}",
    "จำนวนหุ้น (เข้า / ออก)": "-",
    "สัดส่วน Action (%)": "-",
    "จำนวนเงิน (ซื้อ / ขาย) (บาท)": "-",
    "เงินสะสม / เงินรับรวม (บาท)": "-",
    "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": "-",
    "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
        "มูลค่าเหมาะสมตามปัจจัยพื้นฐาน (จุดสมดุล)"
    ),
})

# แถว Current Base
table_rows.append({
    "ประเภทคำสั่ง": "⚪ Current Base",
    "โซนกลยุทธ์": "ต้นทุนปัจจุบัน",
    "ราคาเป้าหมาย (บาท)": f"{curr_avg:.2f}",
    "จำนวนหุ้น (เข้า / ออก)": f"{curr_shares:,} หุ้น",
    "สัดส่วน Action (%)": "ถือครอง",
    "จำนวนเงิน (ซื้อ / ขาย) (บาท)": f"-{curr_cost:,.2f}",
    "เงินสะสม / เงินรับรวม (บาท)": f"{curr_cost:,.2f}",
    "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": f"ทุนเฉลี่ย {curr_avg:.2f}",
    "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
        "สถานะพอร์ตตั้งต้นก่อนเริ่มซื้อตามพีระมิด"
    ),
})

# แถว Buy Pyramid (MOS 1 -> MOS 4)
running_cost = curr_cost
for idx, (p, s, f, avg_c, r) in enumerate(
    zip(buy_prices, buy_shares, buy_funds, avg_costs, mos_rates)
):
  running_cost += s * p
  table_rows.append({
      "ประเภทคำสั่ง": "🟢 Buy (Pyramid)",
      "โซนกลยุทธ์": f"MOS {idx+1} (-{r*100:.0f}%)",
      "ราคาเป้าหมาย (บาท)": f"{p:.2f}",
      "จำนวนหุ้น (เข้า / ออก)": f"+{s:,} หุ้น",
      "สัดส่วน Action (%)": f"ซื้อ {buy_alloc[idx]*100:.0f}%",
      "จำนวนเงิน (ซื้อ / ขาย) (บาท)": f"-{s*p:,.2f}",
      "เงินสะสม / เงินรับรวม (บาท)": f"{running_cost:,.2f}",
      "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": f"ทุนเฉลี่ย {avg_c:.2f}",
      "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
          f"ซื้อไม้ {idx+1} ดึงทุนเฉลี่ยรวมลงมาที่ {avg_c:.2f} บาท"
      ),
  })

df_output = pd.DataFrame(table_rows)

# ตาราง Layer 1 Valuation Matrix
models_list = list(active_info["models"])
models_list.append({
    "โมเดลประเมินมูลค่า": "⭐ สรุปมูลค่าเหมาะสมสุทธิ",
    "ตัวแปรที่ใช้": "ผลรวมถ่วงน้ำหนัก 4 โมเดล (Weighted Matrix)",
    "Fair Value (บาท)": f"{fair_value:.2f}",
    "น้ำหนัก": "100%",
    "Blended (บาท)": f"{fair_value:.2f}",
})
df_valuation = pd.DataFrame(models_list)

# ==============================================================================
# 📊 7. Dashboard Header Metrics & Tables
# ==============================================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("ชื่อหุ้น", selected_stock)
col2.metric("มูลค่าเหมาะสม (Fair Value)", f"{fair_value:.2f} บาท")
col3.metric("ต้นทุนเฉลี่ยเดิม", f"{curr_avg:.2f} บาท")
col4.metric("ต้นทุนเฉลี่ยใหม่ (ซื้อครบ 4 ไม้)", f"{final_avg_price:.2f} บาท")

st.markdown("### 📐 Layer 1: ตารางแจกแจงผลประเมินมูลค่า 4 โมเดล (Valuation Matrix)")
st.table(df_valuation)

st.markdown(
    "### 📊 Layer 2 & 3: ตารางแผนการลงทุน Pyramid ครบวงจรแบบบูรณาการ"
    f" ({selected_stock})"
)
st.table(df_output)

# ==============================================================================
# 📥 8. Export Functions (Excel & CSV)
# ==============================================================================
st.markdown("### 📥 ดาวน์โหลดรายงานแผนการลงทุน")
b1, b2 = st.columns(2)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_valuation.to_excel(
      writer, index=False, sheet_name=f"Valuation_{selected_stock}"
  )
  df_output.to_excel(writer, index=False, sheet_name=f"Plan_{selected_stock}")
excel_data = excel_buffer.getvalue()

csv_data = df_output.to_csv(index=False).encode("utf-8-sig")

with b1:
  st.download_button(
      label=f"📊 ดาวน์โหลดเป็น Excel (.xlsx) - {selected_stock}",
      data=excel_data,
      file_name=f"VI_Plan_{selected_stock}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )

with b2:
  st.download_button(
      label=f"📄 ดาวน์โหลดเป็น CSV (.csv) - {selected_stock}",
      data=csv_data,
      file_name=f"VI_Plan_{selected_stock}.csv",
      mime="text/csv",
  )
