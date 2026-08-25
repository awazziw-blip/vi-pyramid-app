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
# 🎨 2. Page Configuration & White Text UI Theme
# ==========================================
st.set_page_config(
    page_title="VI Pyramid & Portfolio Engine", page_icon="📈", layout="wide"
)

# บังคับสีตัวอักษรเป็นสีขาวบริสุทธิ์ (#FFFFFF) ทุกจุดในระบบ
st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; }
    
    /* บังคับตัวหนังสือสีขาวทั้งหมด */
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #FFFFFF !important;
    }
    
    /* ตัวเลข Metrics Dashboard */
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
    }
    
    /* ตารางผลลัพธ์ */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    th {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        font-weight: bold !important;
        border: 1px solid #334155 !important;
        padding: 10px !important;
    }
    td {
        background-color: #0f172a !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        padding: 8px !important;
    }
    
    /* กล่องข้อความและอินพุต */
    input, select, textarea {
        color: #FFFFFF !important;
        background-color: #1e293b !important;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #1e293b !important;
        color: #FFFFFF !important;
        border: 1px solid #38bdf8 !important;
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
# 🔄 3. State Management & Auto-Update Engine
# ==========================================
if "selected_stock" not in st.session_state:
  st.session_state.selected_stock = "EGCO"
  st.session_state.fair_value = STOCK_DB["EGCO"]["fv"]
  st.session_state.risk_tier = STOCK_DB["EGCO"]["tier"]
  st.session_state.curr_shares = STOCK_DB["EGCO"]["shares"]
  st.session_state.curr_avg = STOCK_DB["EGCO"]["avg"]
  st.session_state.total_budget = STOCK_DB["EGCO"]["budget"]


def update_stock_parameters():
  ticker = st.session_state.ticker_selector.upper().strip()
  if ticker in STOCK_DB:
    data = STOCK_DB[ticker]
    st.session_state.fair_value = data["fv"]
    st.session_state.risk_tier = data["tier"]
    st.session_state.curr_shares = data["shares"]
    st.session_state.curr_avg = data["avg"]
    st.session_state.total_budget = data["budget"]


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
          response.text.replace("```json", "").replace("```", "").strip()
      )
      st.success("✅ ดึงข้อมูลพอร์ตสำเร็จ!")
      st.json(parsed_data)

      # อัปเดตค่าเข้าสู่ระบบทันทีหากพบหุ้น
      if parsed_data:
        first_stock = parsed_data[0]
        sym = first_stock.get("symbol", "").upper()
        if sym in STOCK_DB:
          st.session_state.ticker_selector = sym
          update_stock_parameters()
        st.session_state.curr_shares = int(first_stock.get("shares", 0))
        st.session_state.curr_avg = float(first_stock.get("avg_cost", 0.0))
        st.rerun()
    except Exception as e:
      st.error(f"เกิดข้อผิดพลาดในการอ่านภาพ: {e}")

# ==========================================
# ⚙️ 5. Sidebar: Input Parameters
# ==========================================
st.sidebar.header("⚙️ ข้อมูลหุ้นและงบประมาณ")

# กล่องเลือก/พิมพ์ชื่อหุ้น (เปลี่ยนชื่อแล้วตัวเลขจะเปลี่ยนตามทันที)
stock_list = list(STOCK_DB.keys())
selected_ticker = st.sidebar.selectbox(
    "เลือกหุ้นจากฐานข้อมูล (Auto-Fill):",
    stock_list,
    key="ticker_selector",
    on_change=update_stock_parameters,
)

custom_ticker = st.sidebar.text_input(
    "หรือพิมพ์ชื่อหุ้นเอง (Manual):", value=selected_ticker
).upper()

fair_value = st.sidebar.number_input(
    "มูลค่าเหมาะสม (Fair Value : บาท)",
    key="fair_value",
    step=0.5,
    format="%.2f",
)

tier_options = ["Defensive", "Medium", "Cyclical"]
risk_tier = st.sidebar.selectbox(
    "ระดับความเสี่ยง (Risk Tier)",
    tier_options,
    index=tier_options.index(st.session_state.risk_tier)
    if st.session_state.risk_tier in tier_options
    else 1,
    key="risk_tier",
)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 สถานะพอร์ตปัจจุบัน")
curr_shares = st.sidebar.number_input(
    "จำนวนหุ้นที่มีอยู่", key="curr_shares", step=100
)
curr_avg = st.sidebar.number_input(
    "ราคาต้นทุนเฉลี่ยปัจจุบัน (บาท)", key="curr_avg", step=0.1, format="%.2f"
)
curr_cost = curr_shares * curr_avg

st.sidebar.markdown("---")
st.sidebar.subheader("💰 งบประมาณลงทุน")
total_budget = st.sidebar.number_input(
    "งบลงทุนทั้งหมดที่ตั้งเป้าไว้ (บาท)",
    key="total_budget",
    step=10000.0,
    format="%.2f",
)
pyramid_budget = max(0.0, total_budget - curr_cost)
st.sidebar.info(f"💵 งบสำรองสำหรับซื้อพีระมิด: **{pyramid_budget:,.2f} บาท**")

# ==========================================
# 📐 6. Core Mathematical Engine
# ==========================================
# 1) Dynamic MOS & TP Intervals
if risk_tier == "Defensive":
  mos_rates = [0.12, 0.16, 0.20, 0.24]
  tp_rates = [0.12, 0.16, 0.20]
elif risk_tier == "Medium":
  mos_rates = [0.18, 0.27, 0.36, 0.45]
  tp_rates = [0.18, 0.25, 0.32]
else:
  mos_rates = [0.25, 0.36, 0.48, 0.60]
  tp_rates = [0.25, 0.35, 0.45]

# 2) Buy allocations (Pyramid 15/20/30/35%)
buy_alloc = [0.15, 0.20, 0.30, 0.35]
buy_prices = [fair_value * (1 - r) for r in mos_rates]
buy_funds = [pyramid_budget * a for a in buy_alloc]
buy_shares = [
    int(f / p) if p > 0 else 0 for f, p in zip(buy_funds, buy_prices)
]

# Calculate Cumulative Average Cost
cum_shares = curr_shares
cum_cost = curr_cost
avg_costs = []
for s, p in zip(buy_shares, buy_prices):
  cum_shares += s
  cum_cost += s * p
  avg_costs.append(cum_cost / cum_shares if cum_shares > 0 else 0.0)

final_avg_price = avg_costs[-1] if avg_costs else curr_avg

# 3) Target Prices (TP1, TP2, TP3) & No-Loss Gate
tp_prices = [fair_value * (1 + r) for r in tp_rates]
tp_alloc = [0.30, 0.35, 0.35]

table_rows = []

# --- แถว Take Profit (เรียง TP3 -> TP2 -> TP1) ---
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

# --- แถว Fair Value ---
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

# --- แถว Current Base ---
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

# --- แถว Buy Pyramid (MOS 1 -> MOS 4) ---
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
# 📊 7. Render Output Dashboard
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("ชื่อหุ้น", custom_ticker)
col2.metric("มูลค่าเหมาะสม (Fair Value)", f"{fair_value:.2f} บาท")
col3.metric("ต้นทุนเฉลี่ยเดิม", f"{curr_avg:.2f} บาท")
col4.metric("ต้นทุนเฉลี่ยใหม่ (เมื่อซื้อครบ)", f"{final_avg_price:.2f} บาท")

st.markdown("### 📊 ตารางแผนการลงทุน Pyramid ครบวงจรแบบบูรณาการ")
st.table(df_output)

# ==========================================
# 📥 8. Export Functions (Excel & CSV)
# ==========================================
st.markdown("### 📥 ดาวน์โหลดรายงานแผนการลงทุน")
btn_col1, btn_col2 = st.columns(2)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_output.to_excel(writer, index=False, sheet_name=f"Plan_{custom_ticker}")
excel_data = excel_buffer.getvalue()

csv_data = df_output.to_csv(index=False).encode("utf-8-sig")

with btn_col1:
  st.download_button(
      label=f"📊 ดาวน์โหลดเป็น Excel (.xlsx) - {custom_ticker}",
      data=excel_data,
      file_name=f"VI_Pyramid_Plan_{custom_ticker}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )

with btn_col2:
  st.download_button(
      label=f"📄 ดาวน์โหลดเป็น CSV (.csv) - {custom_ticker}",
      data=csv_data,
      file_name=f"VI_Pyramid_Plan_{custom_ticker}.csv",
      mime="text/csv",
  )
