import io
import json
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import yfinance as yf

# ==============================================================================
# 🎨 1. Institutional Dark Theme & Strict White Text CSS
# ==============================================================================
st.set_page_config(
    page_title="Real-time VI Valuation & Pyramid Engine",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #0b0f19; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    
    /* บังคับตัวหนังสือสีขาวบริสุทธิ์ (#FFFFFF) ทุกจุด */
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #FFFFFF !important;
    }
    
    /* กล่องอินพุต */
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

st.title("🛡️ Institutional Real-Time VI Valuation & Pyramid Engine")
st.caption(
    "ระบบดึงงบการเงินสดจากตลาดหลักทรัพย์ ประเมิน 4 โมเดล Real-time คำนวณพีระมิด"
    " 15/20/30/35% และ No-Loss TP Gate"
)

# ==============================================================================
# 📸 2. Gemini Vision OCR Scanner (อ่านภาพพอร์ต)
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
        st.session_state.target_ticker = (
            parsed[0].get("symbol", "EGCO").upper()
        )
        st.session_state.shares_val = int(parsed[0].get("shares", 0))
        st.session_state.avg_val = float(parsed[0].get("avg_cost", 0.0))
        st.rerun()
    except Exception as e:
      st.error(f"เกิดข้อผิดพลาดในการอ่านภาพ: {e}")

# ==============================================================================
# ⚙️ 3. Sidebar: Real-time Stock Search & Portfolio Inputs
# ==============================================================================
st.sidebar.header("🎯 ค้นหาหุ้น Real-Time")

if "target_ticker" not in st.session_state:
  st.session_state.target_ticker = "EGCO"
if "shares_val" not in st.session_state:
  st.session_state.shares_val = 0
if "avg_val" not in st.session_state:
  st.session_state.avg_val = 0.0

ticker_input = st.sidebar.text_input(
    "พิมพ์ชื่อย่อหุ้น (เช่น PTT, CPALL, BDMS, MINT):",
    value=st.session_state.target_ticker,
).upper().strip()

st.sidebar.markdown("---")
st.sidebar.subheader("📊 ข้อมูลพอร์ต")
curr_shares = st.sidebar.number_input(
    "จำนวนหุ้นที่มีอยู่เดิม",
    value=st.session_state.shares_val,
    step=100,
    key="curr_shares_input",
)
curr_avg = st.sidebar.number_input(
    "ราคาต้นทุนเฉลี่ยเดิม (บาท)",
    value=st.session_state.avg_val,
    step=0.1,
    format="%.2f",
    key="curr_avg_input",
)
curr_cost = curr_shares * curr_avg

st.sidebar.subheader("💰 งบประมาณลงทุน")
total_budget = st.sidebar.number_input(
    "งบลงทุนทั้งหมดที่ตั้งเป้าไว้ (บาท)",
    value=100000.0 if curr_cost == 0 else curr_cost + 100000.0,
    step=10000.0,
    format="%.2f",
)
pyramid_budget = max(0.0, total_budget - curr_cost)
st.sidebar.info(f"💵 งบสำรองซื้อพีระมิด: **{pyramid_budget:,.2f} บาท**")

# ==============================================================================
# 🌐 4. Live Financial Data Fetching Engine (Yahoo Finance API)
# ==============================================================================
@st.cache_data(ttl=3600)  # แคชข้อมูล 1 ชั่วโมงเพื่อความเร็ว
def fetch_live_stock_data(symbol):
  clean_sym = symbol.replace(".BK", "")
  yf_sym = f"{clean_sym}.BK"
  tk = yf.Ticker(yf_sym)
  info = tk.info

  if not info or "regularMarketPrice" not in info:
    # กรณีดึงตรงไม่เจอ พยายามดึงแบบ fallback
    return None

  # สกัดตัวเลขสำคัญ
  market_price = info.get("regularMarketPrice") or info.get("currentPrice", 0.0)
  eps = (
      info.get("trailingEps")
      or info.get("forwardEps")
      or (market_price / max(1.0, info.get("trailingPE", 15.0)))
  )
  bvps = info.get("bookValue") or (
      market_price / max(0.5, info.get("priceToBook", 1.5))
  )
  dps = info.get("dividendRate") or info.get("trailingAnnualDividendRate") or 0.0

  # ถ้าไม่มีปันผล ให้ประมาณการ Conservative Yield 2.5%
  if dps == 0.0 and market_price > 0:
    dps = market_price * 0.025

  pe = info.get("trailingPE") or info.get("forwardPE") or 15.0
  beta = info.get("beta") or 0.85
  company_name = info.get("longName") or info.get("shortName") or clean_sym
  sector = info.get("sector") or "General"

  return {
      "symbol": clean_sym,
      "name": company_name,
      "sector": sector,
      "price": float(market_price),
      "eps": float(eps),
      "bvps": float(bvps),
      "dps": float(dps),
      "pe": float(pe),
      "beta": float(beta),
  }


# โหลดข้อมูล Real-time
with st.spinner(f"กำลังดึงข้อมูลงบการเงินสดของ {ticker_input} จากตลาดหลักทรัพย์..."):
  stock_data = fetch_live_stock_data(ticker_input)

if stock_data is None or stock_data["eps"] <= 0:
  st.error(
      f"❌ ไม่พบข้อมูลหุ้นย่อ '{ticker_input}' ในตลาด หรือหุ้นมีผลการดำเนินงานขาดทุน"
      " กรุณาตรวจสอบชื่อย่อหุ้นอีกครั้ง"
  )
  st.stop()

# ==============================================================================
# 🧮 5. Layer 1: Real-Time 4-Model Valuation Matrix Engine
# ==============================================================================
eps = max(0.01, stock_data["eps"])
bvps = max(0.01, stock_data["bvps"])
dps = max(0.0, stock_data["dps"])
pe = max(5.0, min(35.0, stock_data["pe"]))  # Normalization Cap 5x - 35x
beta = max(0.40, min(1.80, stock_data["beta"]))

# Dynamic Cost of Equity (r) & Growth (g)
rf = 0.020  # Risk Free 2.0%
erp = 0.070  # ERP 7.0%
cost_of_equity = max(0.075, rf + (beta * erp))  # Conservative Floor 7.5%
roe = min(0.30, eps / bvps)  # Normalization Cap ROE 30%
payout = min(0.90, dps / eps) if eps > 0 else 0.50
growth_g = max(0.01, min(0.035, roe * (1 - payout)))  # Cap Sustainable g 1.0% - 3.5%

# 1. Historical PE Model
fv_pe = eps * pe

# 2. Justified PBV Model = ((ROE - g) / (r - g)) * BVPS
if cost_of_equity > growth_g:
  justified_pbv = max(0.5, (roe - growth_g) / (cost_of_equity - growth_g))
  fv_pbv = justified_pbv * bvps
else:
  fv_pbv = bvps * 1.5

# 3. Gordon DDM Model = DPS * (1 + g) / (r - g)
if dps > 0 and cost_of_equity > growth_g:
  fv_ddm = (dps * (1 + growth_g)) / (cost_of_equity - growth_g)
else:
  fv_ddm = fv_pe * 0.85

# 4. DCF 2-Stage Model (5Y Forecast + Terminal)
d_proj = [dps * ((1 + 0.04) ** t) for t in range(1, 6)]
pv_d = sum([d / ((1 + cost_of_equity) ** t) for t, d in enumerate(d_proj, 1)])
term_val = (d_proj[-1] * (1 + growth_g)) / (cost_of_equity - growth_g)
pv_term = term_val / ((1 + cost_of_equity) ** 5)
fv_dcf = pv_d + pv_term

# Blended Fair Value
fair_value = (fv_pe * 0.25) + (fv_pbv * 0.25) + (fv_ddm * 0.25) + (fv_dcf * 0.25)

# Risk Tiering
if beta <= 0.75:
  risk_tier = "Defensive"
  mos_rates = [0.12, 0.16, 0.20, 0.24]
  tp_rates = [0.12, 0.16, 0.20]
elif beta <= 1.10:
  risk_tier = "Medium"
  mos_rates = [0.18, 0.27, 0.36, 0.45]
  tp_rates = [0.18, 0.25, 0.32]
else:
  risk_tier = "Cyclical"
  mos_rates = [0.25, 0.36, 0.48, 0.60]
  tp_rates = [0.25, 0.35, 0.45]

# ==============================================================================
# 📐 6. Execution Engine: Dynamic MOS, Pyramid & No-Loss TP
# ==============================================================================
buy_alloc = [0.15, 0.20, 0.30, 0.35]
buy_prices = [fair_value * (1 - r) for r in mos_rates]
buy_funds = [pyramid_budget * a for a in buy_alloc]
buy_shares = [
    int(f / p) if p > 0 else 0 for f, p in zip(buy_funds, buy_prices)
]

# Cumulative Average Cost
cum_s = curr_shares
cum_c = curr_cost
avg_costs = []
for s, p in zip(buy_shares, buy_prices):
  cum_s += s
  cum_c += s * p
  avg_costs.append(cum_c / cum_s if cum_s > 0 else 0.0)

final_avg_price = avg_costs[-1] if avg_costs else curr_avg

# Target Prices & No-Loss TP
tp_prices = [fair_value * (1 + r) for r in tp_rates]
tp_alloc = [0.30, 0.35, 0.35]

table_rows = []

# Take Profit Rows (TP3 -> TP2 -> TP1)
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

# Fair Value Row
table_rows.append({
    "ประเภทคำสั่ง": "⚖️ Fair Value",
    "โซนกลยุทธ์": "Intrinsic (Real-time)",
    "ราคาเป้าหมาย (บาท)": f"{fair_value:.2f}",
    "จำนวนหุ้น (เข้า / ออก)": "-",
    "สัดส่วน Action (%)": "-",
    "จำนวนเงิน (ซื้อ / ขาย) (บาท)": "-",
    "เงินสะสม / เงินรับรวม (บาท)": "-",
    "ทุนเฉลี่ย / กำไรสุทธิ (บาท)": "-",
    "แผนปฏิบัติการและผลลัพธ์เชิงตัวเลข": (
        "มูลค่าเหมาะสมจากการคำนวณสด 4 โมเดล"
    ),
})

# Current Base Row
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

# Buy Pyramid Rows (MOS 1 -> MOS 4)
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

# ตาราง Valuation Breakdown
df_valuation = pd.DataFrame([
    {
        "โมเดลประเมินมูลค่า": "1. Historical P/E",
        "สูตรและตัวแปร Real-time": f"EPS {eps:.2f} × PE {pe:.1f}x",
        "Fair Value (บาท)": f"{fv_pe:.2f}",
        "น้ำหนัก": "25%",
        "Blended (บาท)": f"{fv_pe*0.25:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "2. Justified PBV",
        "สูตรและตัวแปร Real-time": (
            f"ROE {roe*100:.1f}%, r {cost_of_equity*100:.1f}%, BVPS {bvps:.2f}"
        ),
        "Fair Value (บาท)": f"{fv_pbv:.2f}",
        "น้ำหนัก": "25%",
        "Blended (บาท)": f"{fv_pbv*0.25:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "3. Gordon DDM",
        "สูตรและตัวแปร Real-time": (
            f"DPS {dps:.2f}, g {growth_g*100:.1f}%, r"
            f" {cost_of_equity*100:.1f}%"
        ),
        "Fair Value (บาท)": f"{fv_ddm:.2f}",
        "น้ำหนัก": "25%",
        "Blended (บาท)": f"{fv_ddm*0.25:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "4. DCF 2-Stage",
        "สูตรและตัวแปร Real-time": (
            f"5Y Dividend PV + Terminal @ g {growth_g*100:.1f}%"
        ),
        "Fair Value (บาท)": f"{fv_dcf:.2f}",
        "น้ำหนัก": "25%",
        "Blended (บาท)": f"{fv_dcf*0.25:.2f}",
    },
    {
        "โมเดลประเมินมูลค่า": "⭐ สรุปมูลค่าเหมาะสมสุทธิ",
        "สูตรและตัวแปร Real-time": (
            "ผลรวมถ่วงน้ำหนัก 4 โมเดล (Weighted Blended)"
        ),
        "Fair Value (บาท)": f"{fair_value:.2f}",
        "น้ำหนัก": "100%",
        "Blended (บาท)": f"{fair_value:.2f}",
    },
])

# ==============================================================================
# 📊 7. Render Output Dashboard
# ==============================================================================
st.info(
    f"🏢 **{stock_data['name']}** ({stock_data['symbol']}) |"
    f" กลุ่มอุตสาหกรรม: **{stock_data['sector']}** | ราคาตลาดล่าสุด:"
    f" **{stock_data['price']:.2f} บาท** | Risk Tier: **{risk_tier}**"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("ชื่อหุ้น", stock_data["symbol"])
col2.metric("Fair Value คำนวณสด", f"{fair_value:.2f} บาท")
col3.metric("ต้นทุนเฉลี่ยเดิม", f"{curr_avg:.2f} บาท")
col4.metric("ต้นทุนเฉลี่ยใหม่ (ซื้อครบ 4 ไม้)", f"{final_avg_price:.2f} บาท")

st.markdown(
    "### 📐 Layer 1: ผลประเมินมูลค่า 4 โมเดลแบบ Real-time (Valuation Matrix)"
)
st.table(df_valuation)

st.markdown(
    "### 📊 Layer 2 & 3: ตารางแผนการลงทุน Pyramid ครบวงจรแบบบูรณาการ"
    f" ({stock_data['symbol']})"
)
st.table(df_output)

# Download Section
st.markdown("### 📥 ดาวน์โหลดรายงานแผนการลงทุน")
b1, b2 = st.columns(2)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
  df_valuation.to_excel(
      writer, index=False, sheet_name=f"Valuation_{stock_data['symbol']}"
  )
  df_output.to_excel(
      writer, index=False, sheet_name=f"Plan_{stock_data['symbol']}"
  )
excel_data = excel_buffer.getvalue()

csv_data = df_output.to_csv(index=False).encode("utf-8-sig")

with b1:
  st.download_button(
      label=f"📊 ดาวน์โหลดเป็น Excel (.xlsx) - {stock_data['symbol']}",
      data=excel_data,
      file_name=f"VI_Realtime_Plan_{stock_data['symbol']}.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  )

with b2:
  st.download_button(
      label=f"📄 ดาวน์โหลดเป็น CSV (.csv) - {stock_data['symbol']}",
      data=csv_data,
      file_name=f"VI_Realtime_Plan_{stock_data['symbol']}.csv",
      mime="text/csv",
  )
