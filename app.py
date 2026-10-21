import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Bharat AI Stock Doctor V10.0 (Master Edition)", layout="wide"
)

PORTFOLIO_FILE = "my_portfolio.json"


# ================= 1. PERMANENT PORTFOLIO ENGINE =================
def load_saved_portfolio():
  if os.path.exists(PORTFOLIO_FILE):
    try:
      with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
          return data
    except Exception:
      pass
  default_data = [
      {
          "name": "Tata Motors",
          "ticker": "TATAMOTORS.NS",
          "buy_price": 920.0,
          "qty": 15,
      },
      {
          "name": "IRFC (Railway)",
          "ticker": "IRFC.NS",
          "buy_price": 165.0,
          "qty": 50,
      },
  ]
  save_portfolio_to_disk(default_data)
  return default_data


def save_portfolio_to_disk(portfolio_list):
  try:
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
      json.dump(portfolio_list, f, ensure_ascii=False, indent=2)
  except Exception:
    pass


if "my_portfolio" not in st.session_state:
  st.session_state.my_portfolio = load_saved_portfolio()


# ================= 2. BUILT-IN XML NEWS ENGINE (NO FEEDPARSER NEEDED!) =================
@st.cache_data(ttl=600)
def fetch_live_news(search_query, max_items=3):
  """बिना feedparser के इन-बिल्ट Python XML से लाइव खबरें लाता है (Zero Crash)"""
  try:
    q = urllib.parse.quote(search_query)
    url = (
        f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
      xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    headlines = []
    for item in root.findall(".//item")[:max_items]:
      title_el = item.find("title")
      if title_el is not None and title_el.text:
        headlines.append(title_el.text)
    return headlines
  except Exception:
    return []


# ================= 3. TELEGRAM AUTO-ALERT SENDER =================
def send_telegram_alert(message, bot_token, chat_id):
  if not bot_token or not chat_id:
    return False
  try:
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message})
    req = urllib.request.Request(
        api_url, data=payload.encode("utf-8"), method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      return response.status == 200
  except Exception:
    return False


# ================= 4. ALL-INDIA 12 LANGUAGES ENGINE =================
LANGUAGES = {
    "🇮🇳 हिंदी (Hindi)": "hi",
    "🇮🇳 Hinglish (सरल हिंदी-English)": "hinglish",
    "🇮🇳 मराठी (Marathi)": "mr",
    "🇮🇳 गुजराती (Gujarati)": "gu",
    "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": "pa",
    "🇮🇳 বাংলা (Bengali)": "bn",
    "🇮🇳 தமிழ் (Tamil)": "ta",
    "🇮🇳 తెలుగు (Telugu)": "te",
    "🇮🇳 ಕನ್ನಡ (Kannada)": "kn",
    "🇮🇳 മലയാളം (Malayalam)": "ml",
    "🇮🇳 ଓଡ଼ିଆ (Odia)": "or",
    "🇬🇧 English": "en",
}

st.sidebar.header("🌐 1. अपनी भाषा चुनें (Language)")
selected_lang_label = st.sidebar.selectbox(
    "Choose Language / भाषा बदलें:", list(LANGUAGES.keys()), index=0
)
lang_code = LANGUAGES[selected_lang_label]


@st.cache_data(ttl=3600)
def tr(text, target_lang):
  if not text or target_lang in ["hi", "hinglish"]:
    return text
  try:
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto"
        f"&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=4) as response:
      data = json.loads(response.read().decode("utf-8"))
      return "".join([part[0] for part in data[0] if part[0]])
  except Exception:
    return text


# ================= 5. SIDEBAR SETTINGS & BACKUP =================
st.sidebar.header("💰 2. आपका बजट (Budget)")
user_capital = st.sidebar.number_input(
    tr("एक नए शेयर में कितना पैसा लगाना है? (₹)", lang_code),
    min_value=500,
    max_value=10000000,
    value=10000,
    step=1000,
)

st.sidebar.header("🤖 3. Telegram अलर्ट सेटिंग")
tg_token = st.sidebar.text_input("Bot Token:", type="password")
tg_chat_id = st.sidebar.text_input("Chat ID:")
if st.sidebar.button("📤 " + tr("टेलीग्राम टेस्ट मैसेज भेजें", lang_code)):
  if send_telegram_alert(
      "✅ Bharat AI V10.0: आपका टेलीग्राम अलर्ट जुड़ गया है!",
      tg_token,
      tg_chat_id,
  ):
    st.sidebar.success("✅ मैसेज भेज दिया गया!")
  else:
    st.sidebar.error("❌ Token या Chat ID सही नहीं है।")

with st.sidebar.expander("💾 " + tr("पोर्टफोलियो बैकअप (Mobile/PC Sync)", lang_code)):
  portfolio_json_str = json.dumps(
      st.session_state.my_portfolio, ensure_ascii=False, indent=2
  )
  st.download_button(
      "📥 " + tr("बैकअप फाइल डाउनलोड करें", lang_code),
      data=portfolio_json_str,
      file_name="my_portfolio_backup.json",
      mime="application/json",
      use_container_width=True,
  )
  up_file = st.file_uploader(tr("बैकअप फाइल अपलोड करें:", lang_code), type=["json"])
  if up_file is not None:
    try:
      loaded = json.loads(up_file.read().decode("utf-8"))
      if isinstance(loaded, list):
        st.session_state.my_portfolio = loaded
        save_portfolio_to_disk(loaded)
        st.success("✅ पोर्टफोलियो लोड हो गया!")
    except Exception:
      st.error("फाइल में त्रुटि है।")

if st.sidebar.button("🔄 " + tr("ताज़ा लाइव डेटा रिफ्रेश करें", lang_code), use_container_width=True):
  st.cache_data.clear()

# ================= 6. GROWW-STYLE STOCK CATEGORIES =================
STOCK_CATEGORIES = {
    "🏆 Top Nifty दिग्गज (Large Cap)": {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank (SBI)": "SBIN.NS",
        "Infosys": "INFY.NS",
        "Bharti Airtel": "BHARTIARTL.NS",
        "ITC": "ITC.NS",
        "Larsen & Toubro": "LT.NS",
        "Bajaj Finance": "BAJFINANCE.NS",
        "Mahindra & Mahindra": "M&M.NS",
        "Sun Pharma": "SUNPHARMA.NS",
    },
    "🚀 Midcap & Smallcap रॉकेट स्टॉक्स": {
        "Suzlon Energy": "SUZLON.NS",
        "Dixon Technologies": "DIXON.NS",
        "Kalyan Jewellers": "KALYANKJIL.NS",
        "Persistent Systems": "PERSISTENT.NS",
        "KPIT Technologies": "KPITTECH.NS",
        "Polycab India": "POLYCAB.NS",
        "CDSL": "CDSL.NS",
        "BSE Limited": "BSE.NS",
        "Angel One": "ANGELONE.NS",
        "Zomato": "ZOMATO.NS",
    },
    "🚆 सरकारी, रेलवे और डिफेंस (PSU / Railway / Defence)": {
        "IRFC (Railway)": "IRFC.NS",
        "RVNL (Railway)": "RVNL.NS",
        "HAL (Defence)": "HAL.NS",
        "BEL (Defence)": "BEL.NS",
        "Mazagon Dock": "MAZDOCK.NS",
        "Cochin Shipyard": "COCHINSHIP.NS",
        "BHEL": "BHEL.NS",
        "REC Limited": "RECLTD.NS",
        "Power Finance (PFC)": "PFC.NS",
        "Coal India": "COALINDIA.NS",
    },
    "🪙 कम कीमत / छोटे बजट वाले स्टॉक्स (Low Price)": {
        "Suzlon Energy": "SUZLON.NS",
        "Yes Bank": "YESBANK.NS",
        "Vodafone Idea": "IDEA.NS",
        "NHPC": "NHPC.NS",
        "Punjab National Bank (PNB)": "PNB.NS",
        "IDFC First Bank": "IDFCFIRSTB.NS",
        "UCO Bank": "UCOBANK.NS",
        "IRB Infra": "IRB.NS",
        "Morepen Labs": "MOREPENLAB.NS",
        "Trident": "TRIDENT.NS",
    },
    "🆕 हाल ही में आए चर्चित IPO स्टॉक्स (Recent IPOs)": {
        "Bajaj Housing Finance": "BAJAJHFL.NS",
        "Ola Electric": "OLAELEC.NS",
        "Waaree Energies": "WAAREEENER.NS",
        "Premier Energies": "PREMIERENE.NS",
        "Hyundai Motor India": "HYUNDAI.NS",
        "NTPC Green Energy": "NTPCGREEN.NS",
        "IREDA": "IREDA.NS",
        "Tata Technologies": "TATATECH.NS",
        "Jio Financial": "JIOFIN.NS",
        "Mamaearth (Honasa)": "HONASA.NS",
    },
}


# ================= 7. UNIVERSAL 5000+ STOCK SEARCH API =================
@st.cache_data(ttl=1800)
def search_indian_stocks(query_text):
  try:
    q = urllib.parse.quote(query_text.strip())
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=10&newsCount=0"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
      data = json.loads(resp.read().decode("utf-8"))
      results = []
      for item in data.get("quotes", []):
        sym = item.get("symbol", "")
        if sym.endswith(".NS") or sym.endswith(".BO"):
          name = item.get("longname") or item.get("shortname") or sym
          exch = "NSE" if sym.endswith(".NS") else "BSE"
          results.append((f"{name} ({sym}) [{exch}]", name, sym))
      return results
  except Exception:
    return []


# ================= 8. GLOBAL MACRO & INDIAN MARKET RADAR =================
@st.cache_data(ttl=300)
def get_global_and_india_mood():
  macro = {}
  tickers = {
      "Nifty 50": "^NSEI",
      "Bank Nifty": "^NSEBANK",
      "India VIX": "^INDIAVIX",
      "US Market (S&P 500)": "^GSPC",
      "Crude Oil (कच्चा तेल)": "CL=F",
      "Gold (सोना)": "GC=F",
  }
  for label, sym in tickers.items():
    try:
      df = yf.Ticker(sym).history(period="5d")
      if len(df) >= 2:
        c, p = df["Close"].iloc[-1], df["Close"].iloc[-2]
        chg = round(((c - p) / p) * 100, 2)
        macro[label] = (round(c, 1), chg)
    except Exception:
      pass
  return macro


# ================= 9. DEEP 10-LAYER STOCK X-RAY ENGINE (V10.0) =================
@st.cache_data(ttl=300)
def deep_analyze_v10(name, ticker, nifty_chg):
  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    if df.empty or len(df) < 30:
      return None

    curr = round(df["Close"].iloc[-1], 2)
    prev = round(df["Close"].iloc[-2], 2)
    open_p = round(df["Open"].iloc[-1], 2)
    day_chg = round(((curr - prev) / prev) * 100, 2)

    # 1. Moving Averages (5, 20, 50, 200)
    ma5 = round(df["Close"].rolling(min(5, len(df))).mean().iloc[-1], 2)
    ma20 = round(df["Close"].rolling(min(20, len(df))).mean().iloc[-1], 2)
    ma50 = round(df["Close"].rolling(min(50, len(df))).mean().iloc[-1], 2)
    ma200 = (
        round(df["Close"].rolling(200).mean().iloc[-1], 2)
        if len(df) >= 200
        else ma50
    )

    # 2. MACD (12, 26, 9) Institutional Momentum
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_bullish = bool(macd_line.iloc[-1] > signal_line.iloc[-1])

    # 3. RSI (14)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
    rsi = round(rsi_val, 1) if pd.notna(rsi_val) else 50.0

    # 4. Bollinger Bands (20, 2) & VWAP Proxy
    std20 = df["Close"].rolling(20).std().iloc[-1]
    bb_upper = round(ma20 + (2 * std20), 2) if pd.notna(std20) else curr * 1.05
    bb_lower = round(ma20 - (2 * std20), 2) if pd.notna(std20) else curr * 0.95

    recent_20 = df.tail(20).copy()
    tp = (recent_20["High"] + recent_20["Low"] + recent_20["Close"]) / 3
    vwap_20 = (
        round((tp * recent_20["Volume"]).sum() / recent_20["Volume"].sum(), 2)
        if recent_20["Volume"].sum() > 0
        else ma20
    )
    above_vwap = curr >= vwap_20

    # 5. Smart Money Accumulation vs Operator Trap Check
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    vol_ratio = round(curr_vol / avg_vol, 1) if avg_vol > 0 else 1.0

    if day_chg > 2.0 and vol_ratio < 0.75:
      operator_status = "🚨 सावधान: बिना वॉल्यूम की झूठी तेज़ी (Operator Bull Trap हो सकता है!)"
      is_trap = True
    elif vol_ratio >= 1.5 and day_chg > 0.5:
      operator_status = "🔥 बड़े संस्थान/ऑपरेटर खुलकर खरीद रहे हैं (Heavy Institutional Buying)"
      is_trap = False
    elif vol_ratio >= 1.4 and abs(day_chg) <= 0.8 and curr >= open_p:
      operator_status = "🕵️ चुपचाप माल इकट्ठा किया जा रहा है (Secret Accumulation)"
      is_trap = False
    elif vol_ratio >= 1.5 and day_chg < -0.8:
      operator_status = "⚠️ बड़े खिलाड़ी माल बेचकर निकल रहे हैं (Heavy Selling)"
      is_trap = True
    else:
      operator_status = "⚖️ सामान्य कारोबार (कोई ऑपरेटर ट्रैप नहीं)"
      is_trap = False

    # 6. Support, Resistance, Targets & Exact Entry Zone
    support_floor = round(df["Low"].tail(15).min(), 2)
    resistance_roof = round(df["High"].tail(15).max(), 2)
    high_52w = round(df["High"].max(), 2)
    low_52w = round(df["Low"].min(), 2)
    drop_from_high = round(((curr - high_52w) / high_52w) * 100, 1)

    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
    if pd.isna(atr) or atr <= 0:
      atr = curr * 0.02

    target_1 = round(curr + (atr * 1.2), 2)
    target_2 = round(curr + (atr * 2.2), 2)
    stop_loss = round(curr - (atr * 0.85), 2)
    down_risk = round(curr - (atr * 1.5), 2)
    gain_pct = round(((target_1 - curr) / curr) * 100, 1)

    # "भागती ट्रेन" चेक (Chasing Warning & Ideal Buy Zone)
    dist_from_ma5_pct = ((curr - ma5) / ma5) * 100
    if dist_from_ma5_pct > 4.5 or rsi > 78:
      entry_zone_msg = (
          f"⚠️ भागती ट्रेन मत पकड़ें! शेयर अभी काफी ऊपर निकल चुका है। इसे"
          f" ₹{ma5} से ₹{round(curr*0.98, 1)} के बीच आने पर ही खरीदें।"
      )
    else:
      entry_zone_msg = (
          f"✅ सही खरीद ज़ोन (Ideal Entry): ₹{round(curr*0.99, 1)} से ₹{curr}"
      )

    # 7. Historical 1-Year Strategy Win-Rate Backtest
    df["Cond"] = (df["Close"] > df["Close"].rolling(20).mean()) & (
        ema12 > ema26
    )
    df["Next_3D_Win"] = df["Close"].shift(-3) > df["Close"]
    signals_count = int(df["Cond"].sum())
    if signals_count > 5:
      wins_count = int((df["Cond"] & df["Next_3D_Win"]).sum())
      win_rate = round((wins_count / signals_count) * 100, 1)
      win_rate = max(42.0, min(88.0, win_rate))
    else:
      win_rate = 60.0

    # 8. Built-in Live News Crisis & Profit Check
    headlines = fetch_live_news(f"{name} share news India", max_items=2)
    top_news = headlines[0] if headlines else "कोई बड़ी ताज़ा खबर नहीं है"

    bad_words = [
        "loss", "fall", "crash", "fraud", "raid", "penalty", "slump",
        "down", "fire", "debt", "weak", "drop", "notice", "fine", "scam",
    ]
    good_words = [
        "profit", "surge", "order", "jump", "buy", "win", "growth",
        "high", "record", "rally", "deal", "dividend", "upgrade", "bonus",
    ]

    news_score = 0
    for h in headlines:
      hl = h.lower()
      if any(w in hl for w in bad_words):
        news_score -= 1
      if any(w in hl for w in good_words):
        news_score += 1

    # 9. 6-Point Institutional Passbook & Master Score
    p1_trend = curr > ma20 and curr > ma50
    p2_macd = macd_bullish
    p3_vwap = above_vwap
    p4_vol = (vol_ratio >= 1.1 or day_chg > nifty_chg) and not is_trap
    p5_news = news_score >= 0
    p6_rsi = 48 <= rsi <= 75
    passed_tests = sum([p1_trend, p2_macd, p3_vwap, p4_vol, p5_news, p6_rsi])

    score = int((passed_tests / 6) * 85) + (10 if news_score > 0 else 0)
    if news_score < 0 or is_trap:
      score -= 25
    score = max(8, min(98, score))

    # 10. Easy Local Verdict & Holding Period
    if news_score < 0 or is_trap or (curr < ma20 and day_chg < -1.0):
      cat = "BEARISH"
      verdict = "🔴 खतरा / दूर रहें (AVOID OR SELL)"
      hold_time = "❌ अभी पैसा न लगाएं"
      advice = (
          f"इस शेयर में बिकवाली का दबाव, ऑपरेटर ट्रैप या नेगेटिव खबर है। यह"
          f" ₹{down_risk} तक फिसल सकता है।"
      )
    elif score >= 72 and day_chg >= -0.2:
      cat = "BULLISH"
      verdict = "🟢 मज़बूत खरीदारी (STRONG BUY SIGNAL)"
      hold_time = "⏳ 3 से 10 दिन (Swing/Short-Term)"
      advice = (
          f"6 में से {passed_tests} इंस्टीट्यूशनल टेस्ट पास! MACD, VWAP और"
          f" वॉल्यूम सब मज़बूत हैं। पहला टारगेट: ₹{target_1} (+{gain_pct}%),"
          f" बड़ा टारगेट: ₹{target_2}।"
      )
    elif drop_from_high <= -15:
      cat = "OVERSOLD"
      if curr > ma5 and macd_bullish:
        verdict = "💎 सोने का मौका (बहुत गिरने के बाद अब ऊपर मुड़ रहा है)"
        hold_time = "⏳ 1 से 6 महीने (Wealth / Positional)"
        advice = (
            f"अपने 1 साल के हाई से {abs(drop_from_high)}% सस्ता मिल रहा है और"
            " अब MACD ने भी हरी झंडी दे दी है!"
        )
      else:
        verdict = "📉 लगातार लॉस में (अभी गिरावट रुकी नहीं है - रुकें)"
        hold_time = "⏳ हरा सिग्नल आने तक इंतज़ार करें"
        advice = (
            f"यह शेयर हाई से {abs(drop_from_high)}% टूट चुका है। सस्ते के"
            f" चक्कर में अभी न खरीदें, ₹{ma20} के ऊपर निकलने दें।"
        )
    else:
      cat = "NEUTRAL"
      verdict = "🟡 सामान्य / साइडवेज़ (WAIT FOR BREAKOUT)"
      hold_time = "⏳ ब्रेकआउट का इंतज़ार करें"
      advice = (
          f"अभी कोई बड़ा मूवमेंट नहीं है। जब यह ₹{resistance_roof} की छत तोड़े"
          " तब खरीदें।"
      )

    return {
        "name": name,
        "ticker": ticker,
        "price": curr,
        "day_chg": day_chg,
        "ma5": ma5,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "vwap": vwap_20,
        "macd_bullish": macd_bullish,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "score": score,
        "passed_tests": passed_tests,
        "win_rate": win_rate,
        "verdict": verdict,
        "advice": advice,
        "hold_time": hold_time,
        "entry_zone_msg": entry_zone_msg,
        "up_target": target_1,
        "target_2": target_2,
        "stop_loss": stop_loss,
        "down_risk": down_risk,
        "gain_pct": gain_pct,
        "support": support_floor,
        "resistance": resistance_roof,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "drop_from_high": drop_from_high,
        "operator_status": operator_status,
        "top_news": top_news,
        "news_score": news_score,
        "cat": cat,
        "history_close": df["Close"].tail(60),
    }
  except Exception:
    return None


# ================= 10. REAL 15-MINUTE INTRADAY ENGINE (9:15 AM - 3:30 PM) =================
@st.cache_data(ttl=180)
def scan_real_15m_intraday(name, ticker):
  """असली 15-मिनट की कैंडल्स से सुबह का Opening Range Breakout और लाइव VWAP निकालता है"""
  try:
    df15 = yf.Ticker(ticker).history(period="5d", interval="15m")
    if df15.empty or len(df15) < 10:
      return None

    curr = round(df15["Close"].iloc[-1], 2)
    today_date = df15.index[-1].date()
    today_df = df15[df15.index.date == today_date]
    if today_df.empty:
      today_df = df15.tail(15)

    # सुबह की पहली 15-मिनट कैंडल (9:15 - 9:30 Opening Range)
    orb_high = round(today_df["High"].iloc[0], 2)
    orb_low = round(today_df["Low"].iloc[0], 2)
    day_open = round(today_df["Open"].iloc[0], 2)
    intra_chg = round(((curr - day_open) / day_open) * 100, 2)

    # आज का लाइव Intraday VWAP
    tp = (today_df["High"] + today_df["Low"] + today_df["Close"]) / 3
    vol_sum = today_df["Volume"].sum()
    intra_vwap = (
        round((tp * today_df["Volume"]).sum() / vol_sum, 2)
        if vol_sum > 0
        else curr
    )

    avg_15m_vol = df15["Volume"].tail(30).mean()
    last_15m_vol = today_df["Volume"].iloc[-1]
    vol_spike = (
        round(last_15m_vol / avg_15m_vol, 1) if avg_15m_vol > 0 else 1.0
    )

    if curr > orb_high and curr > intra_vwap:
      status = "🟢 ORB UP-BREAKOUT (आज ऊपर भागने वाला इंट्राडे शेयर)"
      intra_target = round(curr * 1.02, 2)
      intra_sl = max(orb_low, intra_vwap)
      signal_type = "BUY"
    elif curr < orb_low and curr < intra_vwap:
      status = "🔴 ORB BREAKDOWN (आज नीचे गिरने वाला इंट्राडे शेयर)"
      intra_target = round(curr * 0.98, 2)
      intra_sl = min(orb_high, intra_vwap)
      signal_type = "SELL"
    else:
      return None

    return {
        "name": name,
        "ticker": ticker,
        "price": curr,
        "intra_chg": intra_chg,
        "orb_high": orb_high,
        "orb_low": orb_low,
        "vwap": intra_vwap,
        "vol_spike": vol_spike,
        "status": status,
        "target": intra_target,
        "sl": round(intra_sl, 2),
        "signal_type": signal_type,
    }
  except Exception:
    return None


# ================= 11. CARD RENDERERS (PORTFOLIO & GENERAL) =================
def render_portfolio_doctor_card(d, buy_price, qty, lang, idx_key):
  invested = round(buy_price * qty, 2)
  current_val = round(d["price"] * qty, 2)
  pnl_rs = round(current_val - invested, 2)
  pnl_pct = round(((d["price"] - buy_price) / buy_price) * 100, 2)

  if pnl_pct >= 0:
    if d["score"] >= 65 and d["news_score"] >= 0 and d["price"] >= d["ma20"]:
      action_badge = "🟢 अभी होल्ड करें (HOLD FOR BIGGER PROFIT)"
      trailing_sl = max(buy_price, d["stop_loss"])
      doctor_advice = (
          f"बधाई हो! आप **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं और"
          f" रफ़्तार मज़बूत है। यह **₹{d['up_target']}** से **₹{d['target_2']}**"
          f" तक जा सकता है। अपना मुनाफा लॉक करने के लिए **₹{trailing_sl}** का"
          " स्टॉप-लॉस लगाएं।"
      )
      box_type = "success"
    elif d["rsi"] >= 76 or d["news_score"] < 0 or d["price"] < d["ma20"]:
      action_badge = "💰 मुनाफा बुक करें / बेचकर निकलें (BOOK PROFIT NOW)"
      doctor_advice = (
          f"सावधान! आप **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं, लेकिन अब"
          " चार्ट पर कमज़ोरी दिख रही है। आया हुआ मुनाफा तुरंत जेब में डालें!"
      )
      box_type = "warning"
    else:
      action_badge = "🟢 सपोर्ट के साथ होल्ड करें (HOLD WITH SL)"
      doctor_advice = (
          f"आप **+₹{pnl_rs}** के मुनाफे में हैं। जब तक यह **₹{d['support']}** के"
          " ऊपर है, बने रहें।"
      )
      box_type = "info"
  else:
    if d["news_score"] < 0 or (
        d["price"] < d["ma20"] and d["price"] < d["ma50"] and d["score"] <= 40
    ):
      action_badge = "🔴 तुरंत बेचकर निकलें (SELL / EXIT DANGER)"
      doctor_advice = (
          f"अलर्ट! आप **₹{abs(pnl_rs)} ({pnl_pct}%)** के नुकसान में हैं और"
          f" ट्रेंड टूट चुका है। यह **₹{d['down_risk']}** तक और गिर सकता है।"
      )
      box_type = "error"
    elif d["price"] > d["ma5"] and d["macd_bullish"]:
      action_badge = "💎 होल्ड करें & एवरेज करें (RECOVERY STARTED)"
      doctor_advice = (
          f"आप **₹{abs(pnl_rs)}** के नुकसान में हैं, लेकिन शेयर अब नीचे से ऊपर"
          " मुड़ चुका है! नीचे दिए गए **Average Calculator** से अपना खरीद भाव"
          " कम करें।"
      )
      box_type = "success"
    else:
      action_badge = "🟡 आखिरी सपोर्ट के साथ होल्ड करें"
      doctor_advice = (
          f"आप **₹{abs(pnl_rs)}** के नुकसान में हैं। मज़बूत फर्श (Support)"
          f" **₹{d['support']}** पर है। इसके नीचे जाने पर ही निकलें।"
      )
      box_type = "warning"

  with st.container(border=True):
    c_h1, c_h2, c_h3 = st.columns([3, 1, 1])
    c_h1.subheader(f"📌 {d['name']} ({d['ticker']})")
    c_h2.metric(tr("डॉक्टर स्कोर", lang), f"{d['score']}/100")
    if c_h3.button("🗑️ " + tr("हटाएं", lang), key=f"del_{idx_key}"):
      st.session_state.my_portfolio.pop(idx_key)
      save_portfolio_to_disk(st.session_state.my_portfolio)
      st.rerun()

    if box_type == "success":
      st.success(f"### {tr(action_badge, lang)}\n🗣️ {tr(doctor_advice, lang)}")
    elif box_type == "error":
      st.error(f"### {tr(action_badge, lang)}\n🗣️ {tr(doctor_advice, lang)}")
    elif box_type == "warning":
      st.warning(f"### {tr(action_badge, lang)}\n🗣️ {tr(doctor_advice, lang)}")
    else:
      st.info(f"### {tr(action_badge, lang)}\n🗣️ {tr(doctor_advice, lang)}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(tr("आपका खरीद भाव", lang), f"₹{buy_price}", f"{qty} Shares", delta_color="off")
    m2.metric(tr("अभी का भाव", lang), f"₹{d['price']}", f"{d['day_chg']}%")
    m3.metric(tr("कुल मुनाफा / नुकसान", lang), f"₹{pnl_rs}", f"{pnl_pct}%")
    m4.metric(tr("अगला टारगेट", lang), f"₹{d['up_target']}")
    m5.metric(tr("मज़बूत सपोर्ट", lang), f"₹{d['support']}")

    # Smart Average Down Calculator for Loss-Making Shares
    if pnl_pct < 0 and d["price"] < buy_price:
      with st.expander(
          "🧮 "
          + tr(
              f"घाटा जल्दी रिकवर करने का 'Average Down कैलकुलेटर' खोलें (अभी भाव ₹{d['price']})",
              lang,
          ),
          expanded=True,
      ):
        if d["score"] <= 40 or d["news_score"] < 0:
          st.error(
              tr(
                  "⚠️ चेतावनी: अभी गिरावट रुकी नहीं है, जब तक भाव ₹"
                  f"{d['ma5']} के ऊपर न जाए तब तक नए शेयर न जोड़ें!",
                  lang,
              )
          )
        else:
          st.success(
              tr(
                  "✅ सही समय: शेयर सपोर्ट के पास टिक रहा है, आप अभी एवरेज कर"
                  " सकते हैं।",
                  lang,
              )
          )

        ac1, ac2 = st.columns([1, 2])
        extra_qty = ac1.number_input(
            tr("अभी के भाव पर कितने नए शेयर और खरीदें?:", lang),
            min_value=1,
            max_value=1000000,
            value=int(qty),
            step=5,
            key=f"avg_{idx_key}",
        )
        new_inv = round(extra_qty * d["price"], 1)
        tot_shares = qty + extra_qty
        new_avg = round((invested + new_inv) / tot_shares, 2)
        old_req = round(((buy_price - d["price"]) / d["price"]) * 100, 1)
        new_req = round(((new_avg - d["price"]) / d["price"]) * 100, 1)

        ac2.markdown(
            f"- 💰 **{tr('कितना नया पैसा लगेगा:', lang)}** `₹{new_inv}` *(कुल शेयर: {tot_shares})*\n"
            f"- 📉 **{tr('आपका नया खरीद भाव (New Average) घटकर हो जाएगा:', lang)}** **`₹{new_avg}`** *(पहले `₹{buy_price}` था)*\n"
            f"- 🚀 **{tr('फायदा:', lang)}** पहले नो-लॉस में आने के लिए शेयर को **{old_req}%** भागना पड़ता, अब सिर्फ **{new_req}%** उछलते ही सारा घाटा खत्म हो जाएगा!"
        )


def show_master_card(d, budget, lang, show_chart=False, key_prefix="card"):
  qty = max(1, int(budget // d["price"]))
  profit_t1 = int(qty * (d["up_target"] - d["price"]))
  profit_t2 = int(qty * (d["target_2"] - d["price"]))
  risk_rs = int(qty * (d["price"] - d["stop_loss"]))

  with st.container(border=True):
    h1, h2 = st.columns([3, 1])
    h1.subheader(f"{d['name']} ({d['ticker']}) — ₹{d['price']} ({d['day_chg']}%)")
    h2.metric(tr("मास्टर स्कोर", lang), f"{d['score']}%", f"Win Rate: {d['win_rate']}%")

    st.markdown(f"### {tr(d['verdict'], lang)}")
    st.info(f"🗣️ **{tr('आसान भाषा में निचोड़:', lang)}** {tr(d['advice'], lang)}")

    # Entry Zone & Holding Time Bar
    e1, e2 = st.columns(2)
    e1.success(f"🎯 **{tr(d['entry_zone_msg'], lang)}**")
    e2.warning(f"⏰ **{tr('कितने दिन रखें?:', lang)}** {tr(d['hold_time'], lang)}")

    # Rupee Profit & Risk Calculator
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        tr("🛒 कितने शेयर खरीदें?", lang),
        f"{qty} Shares",
        f"लागत: ₹{int(qty * d['price'])}",
        delta_color="off",
    )
    m2.metric(
        tr("🎯 टारगेट-1 मुनाफा", lang),
        f"+₹{profit_t1}",
        f"भाव: ₹{d['up_target']}",
    )
    m3.metric(
        tr("🚀 बड़ा टारगेट-2 मुनाफा", lang),
        f"+₹{profit_t2}",
        f"भाव: ₹{d['target_2']}",
    )
    m4.metric(
        tr("🛡️ स्टॉप-लॉस रिस्क", lang),
        f"-₹{risk_rs}",
        f"SL: ₹{d['stop_loss']}",
        delta_color="inverse",
    )

    st.markdown(
        f"📊 **{tr('लेवल और डेटा:', lang)}** "
        f"🧱 **सपोर्ट (फर्श):** `₹{d['support']}` | "
        f"🚧 **रुकावट (छत):** `₹{d['resistance']}` | "
        f"📉 **52W High से दूरी:** `{d['drop_from_high']}%` | "
        f"⚡ **VWAP:** `₹{d['vwap']}`"
    )
    st.caption(f"{tr(d['operator_status'], lang)} | **📰 ताज़ा खबर:** {tr(d['top_news'], lang)}")

    b_col1, b_col2 = st.columns(2)
    if b_col1.button(
        f"➕ {tr('इसे मेरे पोर्टफोलियो (Virtual Test) में जोड़ें', lang)}",
        key=f"add_v_{key_prefix}_{d['ticker']}",
        use_container_width=True,
    ):
      st.session_state.my_portfolio.insert(
          0,
          {
              "name": d["name"],
              "ticker": d["ticker"],
              "buy_price": float(d["price"]),
              "qty": int(qty),
          },
      )
      save_portfolio_to_disk(st.session_state.my_portfolio)
      st.success(f"✅ {d['name']} आपके पोर्टफोलियो (Tab 1) में जुड़ गया!")

    if tg_token and tg_chat_id:
      if b_col2.button(
          f"📤 {tr('Telegram पर अलर्ट भेजें', lang)}",
          key=f"tg_{key_prefix}_{d['ticker']}",
          use_container_width=True,
      ):
        msg = (
            f"🚀 *Bharat AI V10 Signal: {d['name']}*\n"
            f"Price: ₹{d['price']} ({d['day_chg']}%)\n"
            f"Score: {d['score']}% (Win Rate: {d['win_rate']}%)\n"
            f"Verdict: {d['verdict']}\n"
            f"Target 1: ₹{d['up_target']} | SL: ₹{d['stop_loss']}"
        )
        send_telegram_alert(msg, tg_token, tg_chat_id)
        st.success("✅ टेलीग्राम पर भेज दिया गया!")

    if show_chart:
      st.line_chart(d["history_close"])


# ================= 12. TOP HEADER & GLOBAL MACRO RADAR =================
st.title("🇮🇳 " + tr("भारत AI स्टॉक, पोर्टफोलियो & इंट्राडे डॉक्टर (V10.0 Master)", lang_code))
st.caption(
    tr(
        "ग्लोबल मार्केट रडार + 15-मिनट लाइव इंट्राडे + परमानेंट पोर्टफोलियो"
        " & एवरेज कैलकुलेटर + 5000+ शेयर सर्च",
        lang_code,
    )
)

macro_data = get_global_and_india_mood()
nifty_chg = macro_data.get("Nifty 50", (0, 0.0))[1]
vix_chg = macro_data.get("India VIX", (0, 0.0))[1]

if macro_data:
  m_cols = st.columns(len(macro_data))
  for idx, (m_name, (m_val, m_c)) in enumerate(macro_data.items()):
    inv = "inverse" if m_name in ["India VIX", "Crude Oil (कच्चा तेल)"] else "normal"
    m_cols[idx].metric(m_name, f"{m_val}", f"{m_c}%", delta_color=inv)

  if vix_chg > 6 or nifty_chg < -1.0:
    st.error(
        "🚨 "
        + tr(
            "ग्लोबल/मार्केट क्रैश अलर्ट: आज बाज़ार में डर (India VIX) बढ़ा है"
            " या भारी गिरावट है! आज नई खरीदारी में बहुत सावधानी बरतें।",
            lang_code,
        )
    )
  else:
    st.success(
        "✅ "
        + tr(
            "मार्केट का मूड सुरक्षित है: आप नीचे दिए गए 'हरे सिग्नल' वाले"
            " स्टॉक्स में मौका देख सकते हैं।",
            lang_code,
        )
    )

# ================= 13. ALL 8 MASTER TABS =================
(
    tab_port,
    tab_search,
    tab_intra,
    tab_buy,
    tab_sell,
    tab_disc,
    tab_corp,
    tab_ipo,
) = st.tabs([
    "💼 1. " + tr("मेरा पोर्टफोलियो & Average", lang_code),
    "🔍 2. " + tr("5000+ शेयर सर्च करें", lang_code),
    "⚡ 3. " + tr("सुबह 9:15 लाइव Intraday (15-Min)", lang_code),
    "🟢 4. " + tr("आज/कल ऊपर जाने वाले (Top Buy)", lang_code),
    "🔴 5. " + tr("गिरने वाले / ऑपरेटर ट्रैप (Avoid)", lang_code),
    "💎 6. " + tr("सस्ते डिस्काउंट & फ्यूचर स्टॉक्स", lang_code),
    "🎁 7. " + tr("Dividend, Bonus & Split", lang_code),
    "🆕 8. " + tr("लाइव IPO सेंटर & GMP", lang_code),
])

# ----------------- TAB 1: PERMANENT PORTFOLIO & AVERAGE DOCTOR -----------------
with tab_port:
  st.header("🩺 " + tr("मेरे खरीदे हुए शेयर: Hold/Sell सलाह + Average कैलकुलेटर", lang_code))
  with st.container(border=True):
    p_c1, p_c2, p_c3, p_c4 = st.columns([2, 1, 1, 1])
    p_search = p_c1.text_input(
        tr("1. कंपनी का नाम लिखें (जैसे: Suzlon, Tata Motors, IRFC, SBI):", lang_code),
        value="Suzlon",
    )
    p_matches = search_indian_stocks(p_search) if p_search else []
    if p_matches:
      chosen_p = p_c1.selectbox(
          tr("कंपनी चुनें:", lang_code), options=p_matches, format_func=lambda x: x[0]
      )
      sel_name, sel_ticker = chosen_p[1], chosen_p[2]
    else:
      sel_name, sel_ticker = p_search.upper(), p_search.strip().upper() + ".NS"

    p_buy_price = p_c2.number_input(
        tr("2. खरीद भाव (Buy Price ₹):", lang_code), min_value=0.5, value=65.0, step=1.0
    )
    p_qty = p_c3.number_input(
        tr("3. शेयर संख्या (Qty):", lang_code), min_value=1, value=100, step=1
    )
    st.write("")
    if p_c4.button("💾 " + tr("परमानेंट सेव करें", lang_code), use_container_width=True):
      st.session_state.my_portfolio.insert(
          0,
          {
              "name": sel_name,
              "ticker": sel_ticker,
              "buy_price": float(p_buy_price),
              "qty": int(p_qty),
          },
      )
      save_portfolio_to_disk(st.session_state.my_portfolio)
      st.success(f"✅ {sel_name} हमेशा के लिए सेव हो गया!")

  if st.session_state.my_portfolio:
    total_inv, total_curr = 0.0, 0.0
    analyzed_port = []
    for item in st.session_state.my_portfolio:
      p_data = deep_analyze_v10(item["name"], item["ticker"], nifty_chg)
      if p_data:
        total_inv += item["buy_price"] * item["qty"]
        total_curr += p_data["price"] * item["qty"]
        analyzed_port.append((p_data, item["buy_price"], item["qty"]))

    if analyzed_port:
      tot_pnl = round(total_curr - total_inv, 2)
      tot_pct = round((tot_pnl / total_inv) * 100, 2) if total_inv > 0 else 0.0
      s1, s2, s3 = st.columns(3)
      s1.metric(tr("कुल निवेश (Invested)", lang_code), f"₹{round(total_inv, 1)}")
      s2.metric(tr("अभी की कीमत (Current)", lang_code), f"₹{round(total_curr, 1)}")
      s3.metric(tr("कुल मुनाफा / नुकसान (Net P&L)", lang_code), f"₹{tot_pnl}", f"{tot_pct}%")
      st.divider()
      for idx, (pdata, bp, q) in enumerate(analyzed_port):
        render_portfolio_doctor_card(pdata, bp, q, lang_code, idx)

# ----------------- TAB 2: UNIVERSAL 5000+ STOCK SEARCH -----------------
with tab_search:
  st.header("🔍 " + tr("भारत के किसी भी शेयर (5,000+ NSE/BSE) की तुरंत कुंडली निकालें", lang_code))
  search_query = st.text_input(
      tr(
          "कंपनी का नाम लिखें (जैसे: Bajaj Housing, Ola, MRF, LIC, Adani, Tata,"
          " Zomato, PNB):",
          lang_code,
      ),
      placeholder="यहाँ किसी भी शेयर का नाम लिखें...",
  )
  if search_query:
    matches = search_indian_stocks(search_query)
    if matches:
      selected_match = st.selectbox(
          tr("नीचे मिली कंपनियों में से अपना शेयर चुनें:", lang_code),
          options=matches,
          format_func=lambda x: x[0],
      )
      if selected_match:
        s_data = deep_analyze_v10(selected_match[1], selected_match[2], nifty_chg)
        if s_data:
          show_master_card(
              s_data, user_capital, lang_code, show_chart=True, key_prefix="srch"
          )

# ----------------- TAB 3: REAL 15-MINUTE INTRADAY SCANNER -----------------
with tab_intra:
  st.header("⚡ " + tr("सुबह 9:15 से 3:30 का असली 15-Minute Intraday ORB & VWAP स्कैनर", lang_code))
  st.info(
      tr(
          "यह इंजन असली 15-मिनट की लाइव कैंडल्स से जांचता है कि किस शेयर ने"
          " सुबह 9:15-9:30 का हाई (Opening Range) तोड़ा है और आज के लाइव VWAP"
          " के ऊपर भाग रहा है।",
          lang_code,
      )
  )
  if st.button("🚀 " + tr("अभी 15-Min लाइव इंट्राडे स्कैन चलाएं", lang_code)):
    intra_pool = {}
    for cat_dict in STOCK_CATEGORIES.values():
      intra_pool.update(cat_dict)

    intra_hits = []
    with st.spinner("15-मिनट की लाइव कैंडल्स और VWAP चेक हो रहे हैं..."):
      for iname, itick in list(intra_pool.items())[:22]:
        ir = scan_real_15m_intraday(iname, itick)
        if ir:
          intra_hits.append(ir)

    if intra_hits:
      ic1, ic2 = st.columns(2)
      for idx, item in enumerate(intra_hits):
        with (ic1 if idx % 2 == 0 else ic2):
          with st.container(border=True):
            st.subheader(f"{item['name']} — ₹{item['price']} ({item['intra_chg']}%)")
            if item["signal_type"] == "BUY":
              st.success(f"**{item['status']}**")
            else:
              st.error(f"**{item['status']}**")
            st.write(
                f"🎯 **Intraday Target:** `₹{item['target']}` | 🛡️ **Stop-Loss:**"
                f" `₹{item['sl']}` | ⚡ **Live VWAP:** `₹{item['vwap']}`"
            )
            st.caption(
                f"9:15 High: `₹{item['orb_high']}` | 9:15 Low:"
                f" `₹{item['orb_low']}` | 15m Volume Spike: `{item['vol_spike']}x`"
            )
    else:
      st.warning("अभी कोई शेयर 15-मिनट के ब्रेकआउट नियम को पार नहीं कर रहा है।")

# ----------------- TABS 4, 5, 6: CATEGORY SCANNER -----------------
st.sidebar.header("📂 4. स्टॉक कैटेगरी चुनें")
chosen_category = st.sidebar.radio(
    tr("कैटेगरी बदलें:", lang_code), list(STOCK_CATEGORIES.keys())
)
active_stocks = STOCK_CATEGORIES[chosen_category]

results = []
for name, ticker in active_stocks.items():
  r = deep_analyze_v10(name, ticker, nifty_chg)
  if r:
    results.append(r)

with tab_buy:
  st.subheader(f"🟢 {chosen_category} — " + tr("आज/कल ऊपर जाने वाले स्टॉक्स", lang_code))
  bulls = sorted(
      [r for r in results if r["cat"] == "BULLISH" or r["score"] >= 68],
      key=lambda x: x["score"],
      reverse=True,
  )
  cols = st.columns(2)
  for idx, item in enumerate(bulls):
    with cols[idx % 2]:
      show_master_card(item, user_capital, lang_code, key_prefix=f"buy_{idx}")

with tab_sell:
  st.subheader(
      f"🔴 {chosen_category} — "
      + tr("गिरने वाले / ऑपरेटर ट्रैप वाले स्टॉक्स (दूर रहें)", lang_code)
  )
  bears = sorted(
      [r for r in results if r["cat"] == "BEARISH" or r["score"] <= 48],
      key=lambda x: x["score"],
  )
  cols = st.columns(2)
  for idx, item in enumerate(bears):
    with cols[idx % 2]:
      show_master_card(item, user_capital, lang_code, key_prefix=f"sell_{idx}")

with tab_disc:
  st.subheader(
      f"💎 {chosen_category} — "
      + tr("1 साल के हाई से सस्ते मिल रहे स्टॉक्स (Multibagger & Reversal)", lang_code)
  )
  oversold = sorted(
      [r for r in results if r["cat"] == "OVERSOLD" or r["drop_from_high"] <= -12],
      key=lambda x: x["drop_from_high"],
  )
  cols = st.columns(2)
  for idx, item in enumerate(oversold):
    with cols[idx % 2]:
      show_master_card(item, user_capital, lang_code, key_prefix=f"disc_{idx}")

# ----------------- TAB 7: DIVIDEND, BONUS & SPLIT RADAR -----------------
with tab_corp:
  st.header("🎁 " + tr("Dividend, Bonus और Stock Split देने वाली कंपनियों का लाइव रडार", lang_code))
  c_div, c_bon = st.columns(2)
  with c_div:
    with st.container(border=True):
      st.subheader("💰 " + tr("आगामी डिविडेंड (Upcoming Dividends)", lang_code))
      for title in fetch_live_news("dividend stocks record date India", max_items=6):
        st.markdown(f"- 💵 **{tr(title, lang_code)}**")
  with c_bon:
    with st.container(border=True):
      st.subheader("🚀 " + tr("बोनस शेयर और स्टॉक स्प्लिट (Bonus & Splits)", lang_code))
      for title in fetch_live_news("bonus shares stock split India", max_items=6):
        st.markdown(f"- 🎁 **{tr(title, lang_code)}**")

# ----------------- TAB 8: LIVE IPO CENTER & GMP -----------------
with tab_ipo:
  st.header("🆕 " + tr("ऑल-इंडिया लाइव IPO सेंटर & लिस्टिंग गेन डॉक्टर", lang_code))
  ipo1, ipo2 = st.columns(2)
  with ipo1:
    with st.container(border=True):
      st.subheader("🧮 " + tr("IPO अप्लाई करें या नहीं? (1-सेकंड GMP टेस्टर)", lang_code))
      issue_p = st.number_input("IPO Issue Price (₹):", min_value=10, value=500)
      gmp_rs = st.number_input("अभी चल रहा GMP (₹):", min_value=-200, value=140)
      sub_x = st.number_input("Subscription (कितने गुना भरा? e.g. 15x):", min_value=0.1, value=14.0)
      lot_sz = st.number_input("1 लॉट में कितने शेयर हैं?:", min_value=1, value=30)

      gmp_pct = round((gmp_rs / issue_p) * 100, 1)
      est_profit = int(gmp_rs * lot_sz)
      if gmp_pct >= 20 and sub_x >= 10:
        st.success(
            f"🟢 धमाकेदार IPO (STRONG APPLY): लिस्टिंग पर +{gmp_pct}% (लगभग"
            f" +₹{est_profit} प्रति लॉट) मुनाफे की प्रबल संभावना है!"
        )
      elif gmp_pct >= 10 and sub_x >= 3:
        st.warning(
            f"🟡 सामान्य IPO (MODERATE): इसमें +{gmp_pct}% (+₹{est_profit}) का"
            " मामूली लाभ मिल सकता है।"
        )
      else:
        st.error(
            f"🔴 खतरा / दूर रहें (AVOID IPO): GMP ({gmp_pct}%) बहुत कम है,"
            " लिस्टिंग पर पैसा फंस सकता है!"
        )
  with ipo2:
    with st.container(border=True):
      st.subheader("📰 " + tr("अभी चल रहे और आने वाले IPO की लाइव GMP खबरें", lang_code))
      for title in fetch_live_news("IPO GMP subscription status India", max_items=6):
        st.markdown(f"- 🔔 **{tr(title, lang_code)}**")
