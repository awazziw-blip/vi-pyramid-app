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
          res.text.replace("```json", "").replace("
