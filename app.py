import io
import json
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

# ==========================================
# 🏛️ 1. Institutional Financial Metrics Database (ข้อมูลทางการเงินตั้งต้น)
# ==========================================
FINANCIAL_DB = {
    "EGCO": {
        "sector": "Utilities",
        "eps": 11.20,
        "bvps": 210.00,
        "dps": 6.50,
        "target_pe": 10.5,
        "beta": 0.85,
        "g": 0.015,
        "shares": 1799,
        "avg": 133.40,
        "budget": 300000.0,
    },
    "TISCO": {
        "sector": "Banking",
        "eps": 8.00,
        "bvps": 55.00,
        "dps": 7.75,
        "target_pe": 11.5,
        "beta": 0.70,
        "g": 0.010,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "SAWAD": {
        "sector": "Non-Bank",
        "eps": 3.65,
        "bvps": 25.00,
        "dps": 1.80,
        "target_pe": 12.0,
        "beta": 1.15,
        "g": 0.025,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "SPA": {
        "sector": "Services",
        "eps": 0.36,
        "bvps": 1.90,
        "dps": 0.20,
        "target_pe": 26.0,
        "beta": 1.10,
        "g": 0.025,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "WHAUP": {
        "sector": "Utilities",
        "eps": 0.40,
        "bvps": 3.60,
        "dps": 0.25,
        "target_pe": 11.5,
        "beta": 0.75,
        "g": 0.020,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "BDMS": {
        "sector": "Healthcare",
        "eps": 1.00,
        "bvps": 6.50,
        "dps": 0.75,
        "target_pe": 27.0,
        "beta": 0.65,
        "g": 0.035,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "CPALL": {
        "sector": "Commerce",
        "eps": 2.40,
        "bvps": 14.00,
        "dps": 1.35,
        "target_pe": 27.0,
        "beta": 0.80,
        "g": 0.030,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "ADVANC": {
        "sector": "Defensive ICT",
        "eps": 13.00,
        "bvps": 33.00,
        "dps": 10.50,
        "target_pe": 25.0,
        "beta": 0.60,
        "g": 0.025,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
    "WHART": {
        "sector": "REIT",
        "eps": 0.82,
        "bvps": 10.80,
        "dps": 0.79,
        "target_pe": 13.5,
        "beta": 0.50,
        "g": 0.010,
        "shares": 0,
        "avg": 0.0,
        "budget": 100000.0,
    },
}

# ==========================================
# 🎨 2. Page Configuration & Dark Theme (Strict White Text)
# ==========================================
st.set_page_config(
    page_title="VI Dynamic Valuation & Pyramid Engine",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText { color: #FFFFFF !important; }
    
    div[data-baseweb="select"] > div { background-color: #1e293b !important; border-color: #334155 !important; color: #FFFFFF !important; }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #FFFFFF !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] { background-color: #1e293b !important; color: #FFFFFF !important; }
    li[role="option"] { background-color: #1e293b !important; color: #FFFFFF !important; }
    li[role="option"]:hover, li[aria-selected="true"] { background-color: #334155 !important; color: #38bdf8 !important; }
    
    input, textarea { color: #FFFFFF !important; background-color: #1e293b !important; border: 1px solid #334155 !important; }
    [data-testid="stMetricValue"] { color: #38bdf8 !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #FFFFFF !important; }
    
    table { width: 100% !important; border-collapse: collapse !important; margin-bottom: 20px !important; }
    th { background-color: #1e293b !important; color: #38bdf8 !important; font-weight: bold !important; border: 1px solid #334155 !important; padding: 10px !important; }
    td { background-color: #0f172a !important; color: #FFFFFF !important; border: 1px solid #334155 !important; padding: 8px !important; }
    
    .stDownloadButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1e293b !important; color: #FFFFFF !important; border: 1px solid #38bdf8 !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ Institutional VI Valuation & Execution Engine")
st.caption(
    "ระบบประเมินมูลค่า 4-Model Matrix อัตโนมัติ จัดการไม้ซื้อแบบพีระมิดกลับหัว"
    " และระบบ No-Loss TP Gate"
)

# ==========================================
# 🔄 3. State Management
# ==========================================
def on_stock_select_change():
  sel = st.session_state.stock_select_key
  if sel in FINANCIAL_DB:
    d = FINANCIAL_DB[sel]
    st.session_state.ticker_key = sel
    st.session_state.eps_key = float(d["eps"])
    st.session_state.bvps_key = float(d["bvps"])
    st.session_state.dps_key = float(d["dps"])
    st.session_state.pe_key = float(d["target_pe"])
    st.session_state.beta_key = float(d["beta"])
    st.session_state.g_key = float(d["g"] * 100)
    st.session_state.shares_key = int(d["shares"])
    st.session_state.avg_key = float(d["avg"])
    st.session_state.budget_key = float(d["budget"])


if "eps_key" not in st.session_state:
  d = FINANCIAL_DB["EGCO"]
  st.session_state.stock_select_key = "EGCO"
  st.session_state.ticker_key = "EGCO"
  st.session_state.eps_key = float(d["eps"])
  st.session_state.bvps_key = float(d["bvps"])
  st.session_state.dps_key = float(d["dps"])
  st.session_state.pe_key = float(d["target_pe"])
  st.session_state.beta_key = float(d["beta"])
  st.session_state.g_key = float(d["g"] * 100)
  st.session_state.shares_key = int(d["shares"])
  st.session_state.avg_key = float(d["avg"])
  st.session_state.budget_key = float(d["budget"])

# ==========================================
# 📸 4. Gemini Vision OCR Scanner
# ==========================================
with st.expander("📸 อัปโหลดรูปภาพพอร์ต (Streaming Screenshot Scanner)", expanded=False):
  uploaded_file = st.file_uploader(
      "เลือกไฟล์ภาพแคปหน้าจอพอร์ตหุ้น", type=["jpg", "png", "jpeg"]
  )
  gemini_api_key = st.text_input(
      "ใส่ Gemini API Key (ฟรีจาก Google AI Studio):", type="password"
  )

  if uploaded_file and gemini_api_key:
    try:
      import google.generativeai as genai

      genai.configure(api_key=gemini_api_key)
      model = genai.GenerativeModel("gemini-1.5-flash")
      img = Image.open(uploaded_file)
      prompt = (
          "วิเคราะห์รูปภาพพอร์ตหุ้น และส่งผลลัพธ์เป็น JSON Array เท่านั้น:"
          ' [{"symbol": "ชื่อหุ้น", "shares": int, "avg_cost": float}]'
      )
      res = model.generate_content([prompt, img])
      parsed = json.loads(
          res.text.replace("```json", "").replace("```", "").strip()
      )
      st.success("✅ ดึงข้อมูลพอร์ตสำเร็จ!")
      st.json(parsed)

      if parsed:
        first = parsed[0]
        sym = first.get("symbol", "").upper()
        if sym in FINANCIAL_DB:
          st.session_state.stock_select_key = sym
          on_stock_select_change()
        st.session_state.shares_key = int(first.get("shares", 0))
        st.session_state.avg_key = float(first.get("avg_cost", 0.0))
        st.rerun()
    except Exception as e:
      st.error(f"เกิดข้อผิดพลาดในการอ่านภาพ: {e}")

# ==========================================
# ⚙️ 5. Sidebar: Inputs & Financial Metrics
# ==========================================
st.sidebar.header("⚙️ ข้อมูลทางการเงินและพอร์ต")
st.sidebar.selectbox(
    "เลือกหุ้นเพื่อดึงข้อมูลงบการเงิน:",
    options=list(FINANCIAL_DB.keys()),
    key="stock_select_key",
    on_change=on_stock_select_change,
)

ticker = st.sidebar.text_input("ชื่อย่อหุ้น (Symbol):", key="ticker_key").upper()

st.sidebar.subheader("📐 ตัวแปรประเมินมูลค่า (Valuation Inputs)")
eps_input = st.sidebar.number_input(
    "EPS (กำไรต่อหุ้น TTM : บาท)", key="eps_key", step=0.1, format="%.2f"
)
bvps_input = st.sidebar.number_input(
    "BVPS (มูลค่าทางบัญชี : บาท)", key="bvps_key", step=1.0, format="%.2f"
)
dps_input = st.sidebar.number_input(
    "DPS (เงินปันผลต่อหุ้น : บาท)", key="dps_key", step=0.05, format="%.2f"
)
pe_target_input = st.sidebar.number_input(
    "Target P/E (Historical Median)", key="pe_key", step=0.5, format="%.1f"
)
beta_input = st.sidebar.number_input(
    "Beta (ความผันผวนเทียบตลาด)", key="beta_key", step=0.05, format="%.2f"
)
growth_input = (
    st.sidebar.number_input(
        "Sustainable Growth Rate (g : %)",
        key="g_key",
        step=0.1,
        format="%.2f",
    )
    / 100.0
)

# กำหนด Dynamic Cost of Equity (r)
rf = 0.020  # Risk Free Rate 2.0%
erp = 0.070  # Equity Risk Premium 7.0%
cost_of_equity = max(0.075, rf + (beta_input * erp))  # Conservative Floor 7.5%

# คำนวณ ROE จากข้อมูลงบ
current_roe = (eps_input / bvps_input) if bvps_input > 0 else 0.12

st.sidebar.markdown("---")
st.sidebar.subheader("📊 สถานะพอร์ตปัจจุบัน")
curr_shares = st.sidebar.number_input(
    "จำนวนหุ้นที่มีอยู่", key="shares_key", step=100
)
curr_avg = st.sidebar.number_input(
    "ราคาต้นทุนเฉลี่ยเดิม (บาท)", key="avg_key", step=0.1, format="%.2f"
)
curr_cost = curr_shares * curr_avg

st.sidebar.subheader("💰 งบประมาณลงทุน")
total_budget = st.sidebar.number_input(
    "งบลงทุนทั้งหมดที่ตั้งเป้าไว้ (บาท)",
    key="budget_key",
    step=10000.0,
    format="%.2f",
)
pyramid_budget = max(0.0, total_budget - curr_cost)
st.sidebar.info(f"💵 งบสำรองซื้อพีระมิด: **{pyramid_budget:,.2f} บาท**")

# ==========================================
# 🧮 6. Layer 1: 4-Model Valuation Engine (คำนวณสด)
# ==========================================
# Model 1: Historical P/E
fv_pe = eps_input * pe_target_input

# Model 2: Justified PBV = ((ROE - g) / (r - g)) * BVPS
if cost_of_equity > growth_input:
  justified_pbv = (current_roe - growth_input) / (
      cost_of_equity - growth_input
  )
  fv_pbv = justified_pbv * bvps_input
else:
  fv_pbv = bvps_input * 1.5

# Model 3: Gordon Growth DDM = (DPS * (1 + g)) / (r - g)
if cost_of_equity > growth_input:
  fv_ddm = (dps_input * (1 + growth_input)) / (cost_of_equity - growth_input)
else:
  fv_ddm = dps_input * 15.0

# Model 4: 2-Stage DDM / DCF Model
d1_5 = [dps_input * ((1 + 0.04) ** t) for t in range(1, 6)]
pv_d = sum([d / ((1 + cost_of_equity) ** t) for t, d in enumerate(d1_5, 1)])
term_val = (d1_5[-1] * (1 + growth_input)) / (cost_of_equity - growth_input)
pv_term = term_val / ((1 + cost_of_equity) ** 5)
fv_dcf = pv_d + pv_term

# Sector Weighting Allocation
w_pe, w_pbv, w_ddm, w_dcf = 0.25, 0.25, 0.25, 0.25
calculated_fair_value = (
    (fv_pe * w_pe) + (fv_pbv * w_pbv) + (fv_ddm * w_ddm) + (fv_dcf * w_dcf)
)

# ตารางแสดงการคำนวณ 4 โมเดล
df_valuation = pd.DataFrame([
    {
        "โมเดลประเมินมูลค่า": "1. Historical P/E",
        "ตัวแปรหลัก": f"EPS {eps_input:.2f} × Target PE {pe_target_input:.1f}x",
        "Fair Value ที่คำนวณได้ (บาท)": f"{fv_pe:.2f}",
        "น้ำหนัก": f"{w_pe*100:.0f}%",
        "Blended (บาท)": f"{fv_pe*w_pe:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "2. Justified PBV",
        "ตัวแปรหลัก": (
            f"ROE {current_roe*100:.1f}%, r {cost_of_equity*100:.1f}%, BVPS"
            f" {bvps_input:.2f}"
        ),
        "Fair Value ที่คำนวณได้ (บาท)": f"{fv_pbv:.2f}",
        "น้ำหนัก": f"{w_pbv*100:.0f}%",
        "Blended (บาท)": f"{fv_pbv*w_pbv:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "3. Gordon DDM",
        "ตัวแปรหลัก": (
            f"DPS {dps_input:.2f}, g {growth_input*100:.1f}%, r"
            f" {cost_of_equity*100:.1f}%"
        ),
        "Fair Value ที่คำนวณได้ (บาท)": f"{fv_ddm:.2f}",
        "น้ำหนัก": f"{w_ddm*100:.0f}%",
        "Blended (บาท)": f"{fv_ddm*w_ddm:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
        "ตัวแปรหลัก": (
            f"5Y Dividend PV + Terminal Value @ g {growth_input*100:.1f}%"
        ),
        "Fair Value ที่คำนวณได้ (บาท)": f"{fv_dcf:.2f}",
        "น้ำหนัก": f"{w_dcf*100:.0f}%",
        "Blended (บาท)": f"{fv_dcf*w_dcf:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "⭐ สรุปมูลค่าเหมาะสมสุทธิ",
        "ตัวแปรหลัก": "ผลรวมถ่วงน้ำหนัก 4 โมเดล (Weighted Blended Matrix)",
        "Fair Value ที่คำนวณได้ (บาท)": f"{calculated_fair_value:.2f}",
        "น้ำหนัก": "100%",
        "Blended (บาท)": f"{calculated_fair_value:.2f}",
    },
])

# ==========================================
# 📐 7. Layer 2 & 3: Dynamic MOS & Pyramid Execution
# ==========================================
# กำหนด Risk Tier จาก Beta และ Sector
if beta_input <= 0.75:
  mos_rates = [0.12, 0.16, 0.20, 0.24]
  tp_rates = [0.12, 0.16, 0.20]
  tier_name = "Defensive"
elif beta_input <= 1.10:
  mos_rates = [0.18, 0.27, 0.36, 0.45]
  tp_rates = [0.18, 0.25, 0.32]
  tier_name = "Medium"
else:
  mos_rates = [0.25, 0.36, 0.48, 0.60]
  tp_rates = [0.25, 0.35, 0.45]
  tier_name = "Cyclical"

# Buy Allocations (15%, 20%, 30%, 35%)
buy_alloc = [0.15, 0.20, 0.30, 0.35]
buy_prices = [calculated_fair_value * (1 - r) for r in mos_rates]
buy_funds = [pyramid_budget * a for a in buy_alloc]
buy_shares = [
    int(f / p) if p > 0 else 0 for f, p in zip(buy_funds, buy_prices)
]

# Cumulative Average Cost Calculation
cum_s = curr_shares
cum_c = curr_cost
avg_costs = []
for s, p in zip(buy_shares, buy_prices):
  cum_s += s
  cum_c += s * p
  avg_costs.append(cum_c / cum_s if cum_s > 0 else 0.0)

final_avg_price = avg_costs[-1] if avg_costs else curr_avg

# Target Prices (TP1, TP2, TP3)
tp_prices = [calculated_fair_value * (1 + r) for r in tp_rates]
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

# แถว Fair Value (ผลลัพธ์จากการคำนวณ 4 โมเดล)
table_rows.append({
    "ประเภทคำสั่ง": "⚖️ Fair Value",
    "โซนกลยุทธ์": "Intrinsic (4-Model)",
    "ราคาเป้าหมาย (บาท)": f"{calculated_fair_value:.2f}",
    "จำนวนหุ้น (เข้า / ออก)": "-",
    "สัดส่วน Action (%)": "-",
    "จำนวนเงิน (ซื้อ / ขาย) (บาท)": "-",
    "เงินสะสม / เงินรับรวม (บาท)": "-",
    "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": "-",
    "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
        "มูลค่าเหมาะสมจากการคำนวณ 4 โมเดลทางคณิตศาสตร์"
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

# ==========================================
# 📊 8. Render Outputs & Download
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("ชื่อหุ้น", ticker)
col2.metric("Fair Value จากการคำนวณ", f"{calculated_fair_value:.2f} บาท")
col3.metric("ต้นทุนเฉลี่ยเดิม", f"{curr_avg:.2f} บาท")
col4.metric("ต้นทุนเฉลี่ยใหม่ (ซื้อครบ 4 ไม้)", f"{final_avg_price:.2f} บาท")

st.markdown("### 📐 Layer 1: ผลลัพธ์การประเมินมูลค่า 4 โมเดล (Valuation Matrix)")
st.table(df_valuation)

st.markdown("### 📊 Layer 2 & 3: ตารางแผนการลงทุน Pyramid ครบวงจรแบบบูรณาการ")
st.table(df_output)

# Download Section
st.markdown("### 📥 ดาวน์โหลดรายงานแผนการลงทุน")
b1, b2 = st.columns(2)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_valuation.to_excel(writer, index=False, sheet_name="Valuation_Matrix")
  df_output.to_excel(writer, index=False, sheet_name="Pyramid_Plan")
excel_data = excel_buffer.getvalue()

csv_data = df_output.to_csv(index=False).encode("utf-8-sig")

with b1:
  st.download_button(
      label=f"📊 ดาวน์โหลดเป็น Excel (.xlsx) - {ticker}",
      data=excel_data,
      file_name=f"VI_Full_Plan_{ticker}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )

with b2:
  st.download_button(
      label=f"📄 ดาวน์โหลดเป็น CSV (.csv) - {ticker}",
      data=csv_data,
      file_name=f"VI_Pyramid_Plan_{ticker}.csv",
      mime="text/csv",
  )
