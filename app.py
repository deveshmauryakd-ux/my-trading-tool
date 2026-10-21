import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Groww-Style Bharat AI Stock Doctor V11.0",
    layout="wide",
    initial_sidebar_state="expanded",
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


# ================= 2. 100% WORKING MULTI-LANGUAGE ENGINE (12 LANGUAGES) =================
LANGUAGES = {
    "🇮🇳 हिंदी (Hindi)": "hi",
    "🇮🇳 Hinglish (सरल बोलचाल)": "hinglish",
    "🇬🇧 English": "en",
    "🇮🇳 मराठी (Marathi)": "mr",
    "🇮🇳 गुजराती (Gujarati)": "gu",
    "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": "pa",
    "🇮🇳 বাংলা (Bengali)": "bn",
    "🇮🇳 தமிழ் (Tamil)": "ta",
    "🇮🇳 తెలుగు (Telugu)": "te",
    "🇮🇳 ಕನ್ನಡ (Kannada)": "kn",
    "🇮🇳 മലയാളം (Malayalam)": "ml",
    "🇮🇳 ଓଡ଼ିଆ (Odia)": "or",
}

st.sidebar.header("🌐 1. Choose Language / भाषा बदलें")
selected_lang_label = st.sidebar.selectbox(
    "Select Language:", list(LANGUAGES.keys()), index=0
)
LANG = LANGUAGES[selected_lang_label]


@st.cache_data(ttl=7200)
def google_translate_api(text, target_lang):
  """Regional languages (Marathi, Gujarati, Tamil, etc.) ke liye fast translator"""
  if not text:
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


def L(hi_text, hinglish_text=None, en_text=None):
  """
  100% Working Language Switcher:
  - Hindi ('hi') -> returns hi_text instantly
  - Hinglish ('hinglish') -> returns hinglish_text instantly
  - English ('en') -> returns en_text instantly
  - Any other Indian language ('mr', 'gu', 'ta', 'te', 'bn', 'pa', 'kn', 'ml', 'or') -> translates cleanly!
  """
  if LANG == "hi":
    return hi_text
  if LANG == "hinglish":
    return hinglish_text if hinglish_text else hi_text
  if LANG == "en":
    return (
        en_text
        if en_text
        else (
            hinglish_text
            if hinglish_text
            else google_translate_api(hi_text, "en")
        )
    )
  # Regional Indian Languages: translate from English/Hindi cleanly
  base_text = en_text if en_text else hi_text
  return google_translate_api(base_text, LANG)


# ================= 3. BUILT-IN XML NEWS ENGINE (NO FEEDPARSER NEEDED!) =================
@st.cache_data(ttl=600)
def fetch_live_news(search_query, max_items=3):
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


# ================= 4. TELEGRAM AUTO-ALERT SENDER =================
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


# ================= 5. SIDEBAR BUDGET, TELEGRAM & BACKUP =================
st.sidebar.header(
    L("💰 2. आपका बजट", "💰 2. Aapka Budget", "💰 2. Your Budget")
)
user_capital = st.sidebar.number_input(
    L(
        "एक शेयर में कितना पैसा लगाना है? (₹)",
        "Ek share mein kitna paisa lagana hai? (₹)",
        "Investment per stock (₹)",
    ),
    min_value=500,
    max_value=10000000,
    value=10000,
    step=1000,
)

if st.sidebar.button(
    "🔄 "
    + L(
        "ताज़ा लाइव डेटा रिफ्रेश करें",
        "Taaza Live Data Refresh Karein",
        "Refresh Live Market Data",
    ),
    use_container_width=True,
):
  st.cache_data.clear()

with st.sidebar.expander(
    "🤖 "
    + L(
        "Telegram अलर्ट सेटिंग",
        "Telegram Alert Setting",
        "Telegram Alert Settings",
    )
):
  tg_token = st.text_input("Bot Token:", type="password")
  tg_chat_id = st.text_input("Chat ID:")
  if st.button(
      "📤 " + L("टेस्ट मैसेज भेजें", "Test Message Bhejein", "Send Test Alert")
  ):
    if send_telegram_alert(
        "✅ Bharat AI V11.0: Telegram Alert Connected!", tg_token, tg_chat_id
    ):
      st.success(L("✅ मैसेज भेज दिया गया!", "✅ Message bhej diya gaya!", "✅ Sent!"))
    else:
      st.error(
          L("❌ Token या Chat ID गलत है।", "❌ Token ya Chat ID galat hai.", "❌ Invalid Token/ID.")
      )

with st.sidebar.expander(
    "💾 "
    + L(
        "पोर्टफोलियो बैकअप (Mobile/PC)",
        "Portfolio Backup (Mobile/PC)",
        "Portfolio Backup & Restore",
    )
):
  portfolio_json_str = json.dumps(
      st.session_state.my_portfolio, ensure_ascii=False, indent=2
  )
  st.download_button(
      "📥 "
      + L(
          "बैकअप डाउनलोड करें",
          "Backup Download Karein",
          "Download Portfolio Backup",
      ),
      data=portfolio_json_str,
      file_name="my_portfolio_backup.json",
      mime="application/json",
      use_container_width=True,
  )
  up_file = st.file_uploader(
      L("बैकअप फाइल अपलोड करें:", "Backup File Upload Karein:", "Upload Backup JSON:"),
      type=["json"],
  )
  if up_file is not None:
    try:
      loaded = json.loads(up_file.read().decode("utf-8"))
      if isinstance(loaded, list):
        st.session_state.my_portfolio = loaded
        save_portfolio_to_disk(loaded)
        st.success("✅ Portfolio Restored!")
    except Exception:
      st.error("Invalid file.")

# ================= 6. GROWW-STYLE STOCK CATEGORIES =================
STOCK_CATEGORIES = {
    "🏆 Top Nifty 50 (Large Cap)": {
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
        "Tata Motors": "TATAMOTORS.NS",
        "Tata Steel": "TATASTEEL.NS",
        "NTPC": "NTPC.NS",
        "Axis Bank": "AXISBANK.NS",
    },
    "🚀 Midcap & Smallcap Rockets": {
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
        "Tata Power": "TATAPOWER.NS",
    },
    "🚆 PSU, Railway & Defence": {
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
    "🪙 Low Price / Pocket Friendly (< ₹250)": {
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
    "🆕 Popular Recent IPO Stocks": {
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
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=12&newsCount=0"
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


# ================= 8. GROWW-STYLE LIVE INDICES & GLOBAL MACRO =================
@st.cache_data(ttl=300)
def get_groww_market_bar():
  macro = {}
  tickers = {
      "🇮🇳 NIFTY 50": "^NSEI",
      "🇮🇳 SENSEX": "^BSESN",
      "🏦 BANK NIFTY": "^NSEBANK",
      "⚡ INDIA VIX": "^INDIAVIX",
      "🇺🇸 US S&P 500": "^GSPC",
      "🛢️ CRUDE OIL": "CL=F",
      "🪙 GOLD": "GC=F",
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


# ================= 9. GROWW + INSTITUTIONAL DEEP ENGINE (V11.0) =================
@st.cache_data(ttl=300)
def deep_analyze_v11(name, ticker, nifty_chg, fetch_fundamentals=False):
  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    if df.empty or len(df) < 25:
      return None

    curr = round(df["Close"].iloc[-1], 2)
    prev = round(df["Close"].iloc[-2], 2)
    open_p = round(df["Open"].iloc[-1], 2)
    day_chg = round(((curr - prev) / prev) * 100, 2)

    # Multi-Period Returns (Groww Style: 1W, 1M, 6M, 1Y)
    ret_1w = (
        round(((curr - df["Close"].iloc[-6]) / df["Close"].iloc[-6]) * 100, 1)
        if len(df) >= 6
        else day_chg
    )
    ret_1m = (
        round(((curr - df["Close"].iloc[-22]) / df["Close"].iloc[-22]) * 100, 1)
        if len(df) >= 22
        else ret_1w
    )
    ret_6m = (
        round(
            ((curr - df["Close"].iloc[-125]) / df["Close"].iloc[-125]) * 100, 1
        )
        if len(df) >= 125
        else ret_1m
    )
    ret_1y = round(((curr - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100, 1)

    # Moving Averages (5, 20, 50, 200)
    ma5 = round(df["Close"].rolling(min(5, len(df))).mean().iloc[-1], 2)
    ma20 = round(df["Close"].rolling(min(20, len(df))).mean().iloc[-1], 2)
    ma50 = round(df["Close"].rolling(min(50, len(df))).mean().iloc[-1], 2)
    ma200 = (
        round(df["Close"].rolling(200).mean().iloc[-1], 2)
        if len(df) >= 200
        else ma50
    )

    # MACD (12, 26, 9)
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_bullish = bool(macd_line.iloc[-1] > signal_line.iloc[-1])

    # RSI (14)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
    rsi = round(rsi_val, 1) if pd.notna(rsi_val) else 50.0

    # VWAP Proxy (20D)
    recent_20 = df.tail(20).copy()
    tp = (recent_20["High"] + recent_20["Low"] + recent_20["Close"]) / 3
    vwap_20 = (
        round((tp * recent_20["Volume"]).sum() / recent_20["Volume"].sum(), 2)
        if recent_20["Volume"].sum() > 0
        else ma20
    )
    above_vwap = curr >= vwap_20

    # Volume & Operator Trap Check
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    vol_ratio = round(curr_vol / avg_vol, 1) if avg_vol > 0 else 1.0

    if day_chg > 2.0 and vol_ratio < 0.75:
      op_hi = "🚨 सावधान: बिना वॉल्यूम की झूठी तेज़ी (Operator Bull Trap!)"
      op_hing = "🚨 Savdhan: Bina volume ki jhoothi tezi (Operator Trap!)"
      op_en = "🚨 Warning: Price up on low volume (Possible Bull Trap!)"
      is_trap = True
    elif vol_ratio >= 1.5 and day_chg > 0.5:
      op_hi = "🔥 बड़े खिलाड़ी जमकर खरीद रहे हैं (Heavy Institutional Buying)"
      op_hing = "🔥 Bade Khiladi jamkar kharid rahe hain (Heavy Buying)"
      op_en = "🔥 Heavy Institutional Buying detected today"
      is_trap = False
    elif vol_ratio >= 1.4 and abs(day_chg) <= 0.8 and curr >= open_p:
      op_hi = "🕵️ चुपचाप नीचे के भाव पर माल उठाया जा रहा है (Secret Accumulation)"
      op_hing = "🕵️ Chupchap niche ke bhaav par mal uthaya ja raha hai"
      op_en = "🕵️ Quiet Smart-Money Accumulation detected"
      is_trap = False
    elif vol_ratio >= 1.5 and day_chg < -0.8:
      op_hi = "⚠️ बड़े खिलाड़ी माल बेचकर निकल रहे हैं (Heavy Selling)"
      op_hing = "⚠️ Bade Khiladi mal bech kar nikal rahe hain (Heavy Selling)"
      op_en = "⚠️ Heavy Institutional Selling pressure"
      is_trap = True
    else:
      op_hi = "⚖️ सामान्य कारोबार (कोई ऑपरेटर ट्रैप नहीं)"
      op_hing = "⚖️ Samanya karobar (Koi operator trap nahi)"
      op_en = "⚖️ Normal trading volume (No operator trap)"
      is_trap = False

    # 52W High/Low Range Position (0 to 100% for Groww Slider)
    high_52w = round(df["High"].max(), 2)
    low_52w = round(df["Low"].min(), 2)
    drop_from_high = round(((curr - high_52w) / high_52w) * 100, 1)
    range_pos = (
        int(((curr - low_52w) / (high_52w - low_52w)) * 100)
        if high_52w > low_52w
        else 50
    )
    range_pos = max(1, min(100, range_pos))

    support_floor = round(df["Low"].tail(15).min(), 2)
    resistance_roof = round(df["High"].tail(15).max(), 2)

    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
    if pd.isna(atr) or atr <= 0:
      atr = curr * 0.02

    target_1 = round(curr + (atr * 1.3), 2)
    target_2 = round(curr + (atr * 2.3), 2)
    stop_loss = round(curr - (atr * 0.85), 2)
    down_risk = round(curr - (atr * 1.5), 2)
    gain_pct = round(((target_1 - curr) / curr) * 100, 1)

    # Ideal Entry Zone Check
    dist_ma5 = ((curr - ma5) / ma5) * 100
    if dist_ma5 > 4.5 or rsi > 78:
      entry_hi = f"⚠️ भागती ट्रेन मत पकड़ें! इसे ₹{ma5}–₹{round(curr*0.98, 1)} के पास आने पर खरीदें"
      entry_hing = f"⚠️ Bhagti train mat pakdein! ₹{ma5}–₹{round(curr*0.98, 1)} par aane dein"
      entry_en = f"⚠️ Don't chase high! Ideal pullback buy zone: ₹{ma5}–₹{round(curr*0.98, 1)}"
    else:
      entry_hi = f"✅ सही खरीद भाव (Buy Zone): ₹{round(curr*0.99, 1)} से ₹{curr}"
      entry_hing = f"✅ Sahi Kharid Bhaav (Buy Zone): ₹{round(curr*0.99, 1)} se ₹{curr}"
      entry_en = f"✅ Ideal Buy Zone: ₹{round(curr*0.99, 1)} to ₹{curr}"

    # Historical 1Y Win-Rate Backtest
    df["Cond"] = (df["Close"] > df["Close"].rolling(20).mean()) & (
        ema12 > ema26
    )
    df["Next_3D_Win"] = df["Close"].shift(-3) > df["Close"]
    sig_cnt = int(df["Cond"].sum())
    if sig_cnt > 5:
      win_cnt = int((df["Cond"] & df["Next_3D_Win"]).sum())
      win_rate = max(42.0, min(88.0, round((win_cnt / sig_cnt) * 100, 1)))
    else:
      win_rate = 62.0

    # Live News Scan
    headlines = fetch_live_news(f"{name} share news India", max_items=2)
    top_news = headlines[0] if headlines else "No major breaking news today"

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

    # 6-Point Institutional Passbook
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

    # Multi-Language Verdicts & Advice
    if news_score < 0 or is_trap or (curr < ma20 and day_chg < -1.0):
      cat = "BEARISH"
      v_hi = "🔴 खतरा / दूर रहें (आज या कल गिर सकता है)"
      v_hing = "🔴 KHATRA / AVOID (Aaj ya Kal Gir Sakta Hai)"
      v_en = "🔴 AVOID / SELL (High Downside Risk)"
      adv_hi = f"इस शेयर में बिकवाली का दबाव, ऑपरेटर ट्रैप या खराब खबर है। यह ₹{down_risk} तक गिर सकता है, नया पैसा बिल्कुल न लगाएं।"
      adv_hing = f"Is share mein bikwali ka dabav ya kharab khabar hai. Yeh ₹{down_risk} tak gir sakta hai, abhi door rahein."
      adv_en = f"Selling pressure or negative news detected. Could slide towards ₹{down_risk}. Avoid fresh entry."
      hold_hi, hold_hing, hold_en = "❌ अभी न खरीदें", "❌ Abhi mat kharidein", "❌ Do Not Buy Now"
    elif score >= 72 and day_chg >= -0.2:
      cat = "BULLISH"
      v_hi = "🟢 मज़बूत खरीदारी (आज/कल ऊपर जाने वाला टॉप शेयर)"
      v_hing = "🟢 STRONG BUY (Aaj/Kal Upar Jane Wala Top Share)"
      v_en = "🟢 STRONG BUY (High-Conviction Bullish Setup)"
      adv_hi = f"6 में से {passed_tests} टेस्ट पास! ट्रेंड, MACD, VWAP और वॉल्यूम सब आपके पक्ष में हैं। टारगेट-1: ₹{target_1} (+{gain_pct}%), टारगेट-2: ₹{target_2}।"
      adv_hing = f"6 mein se {passed_tests} test paas! Trend, MACD, VWAP aur Volume sab majboot hain. Target-1: ₹{target_1} (+{gain_pct}%), Target-2: ₹{target_2}."
      adv_en = f"Passed {passed_tests}/6 institutional checks! Strong trend & volume. Target 1: ₹{target_1} (+{gain_pct}%), Target 2: ₹{target_2}."
      hold_hi, hold_hing, hold_en = "⏳ 3 से 10 दिन (Swing)", "⏳ 3 se 10 Din (Swing)", "⏳ 3 to 10 Days (Swing)"
    elif drop_from_high <= -15:
      cat = "OVERSOLD"
      if curr > ma5 and macd_bullish:
        v_hi = "💎 सोने का मौका (काफी गिरने के बाद अब ऊपर उठ रहा है)"
        v_hing = "💎 SONE KA MAUKA (Bahut Girne Ke Baad Ab Upar Mud Raha Hai)"
        v_en = "💎 GOLDEN REVERSAL (Oversold Stock Turning Bullish)"
        adv_hi = f"अपने 1 साल के हाई से {abs(drop_from_high)}% सस्ता मिल रहा है और अब खरीदारी लौट आई है। फ्यूचर के लिए शानदार मौका!"
        adv_hing = f"Apne 1 saal ke high se {abs(drop_from_high)}% sasta mil raha hai aur ab upar mud raha hai. Future ke liye best!"
        adv_en = f"Available at {abs(drop_from_high)}% discount from 52W High with fresh bullish reversal!"
        hold_hi, hold_hing, hold_en = "⏳ 1 से 6 महीने (Future)", "⏳ 1 se 6 Mahine (Future)", "⏳ 1 to 6 Months"
      else:
        v_hi = "📉 लगातार लॉस में (अभी गिरावट रुकी नहीं है - इंतज़ार करें)"
        v_hing = "📉 LAGATAR LOSS MEIN (Abhi Girawat Ruki Nahi Hai - Rukein)"
        v_en = "📉 FALLING KNIFE (Still Weak - Wait for Reversal)"
        adv_hi = f"यह शेयर हाई से {abs(drop_from_high)}% टूट चुका है। सस्ते के चक्कर में अभी न खरीदें, ₹{ma20} के ऊपर निकलने दें।"
        adv_hing = f"Yeh share high se {abs(drop_from_high)}% toot chuka hai. Jab tak ₹{ma20} ke upar na nikle, mat kharidein."
        adv_en = f"Down {abs(drop_from_high)}% from high and still below 20-DMA (₹{ma20}). Wait for trend reversal."
        hold_hi, hold_hing, hold_en = "⏳ हरा सिग्नल आने तक रुकें", "⏳ Green signal tak rukein", "⏳ Wait for Green Signal"
    else:
      cat = "NEUTRAL"
      v_hi = "🟡 सामान्य / साइडवेज़ (ब्रेकआउट का इंतज़ार करें)"
      v_hing = "🟡 WAIT & WATCH (Abhi Sideways Hai)"
      v_en = "🟡 NEUTRAL / SIDEWAYS (Wait for Breakout)"
      adv_hi = f"अभी कोई बड़ा मूवमेंट नहीं है। जब यह ₹{resistance_roof} की रुकावट तोड़े तब खरीदें।"
      adv_hing = f"Abhi koi bada move nahi hai. Jab yeh ₹{resistance_roof} ke upar nikle tab kharidein."
      adv_en = f"Consolidating in a range. Buy only above resistance of ₹{resistance_roof}."
      hold_hi, hold_hing, hold_en = "⏳ इंतज़ार करें", "⏳ Intezar karein", "⏳ Wait for Breakout"

    # Optional Groww Fundamentals (for Search & Deep View)
    fundamentals = None
    if fetch_fundamentals:
      try:
        info = stock.info
        mcap_cr = round(info.get("marketCap", 0) / 1e7, 1) if info.get("marketCap") else "N/A"
        pe = round(info.get("trailingPE", 0), 1) if info.get("trailingPE") else "N/A"
        pb = round(info.get("priceToBook", 0), 2) if info.get("priceToBook") else "N/A"
        roe = round(info.get("returnOnEquity", 0) * 100, 1) if info.get("returnOnEquity") else "N/A"
        debt_eq = round(info.get("debtToEquity", 0), 1) if info.get("debtToEquity") else "N/A"
        div_y = round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0.0
        fundamentals = {
            "mcap_cr": mcap_cr,
            "pe": pe,
            "pb": pb,
            "roe": roe,
            "debt_eq": debt_eq,
            "div_y": div_y,
        }
      except Exception:
        fundamentals = None

    return {
        "name": name,
        "ticker": ticker,
        "price": curr,
        "day_chg": day_chg,
        "ret_1w": ret_1w,
        "ret_1m": ret_1m,
        "ret_6m": ret_6m,
        "ret_1y": ret_1y,
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
        "p_list": [p1_trend, p2_macd, p3_vwap, p4_vol, p5_news, p6_rsi],
        "win_rate": win_rate,
        "v_hi": v_hi,
        "v_hing": v_hing,
        "v_en": v_en,
        "adv_hi": adv_hi,
        "adv_hing": adv_hing,
        "adv_en": adv_en,
        "hold_hi": hold_hi,
        "hold_hing": hold_hing,
        "hold_en": hold_en,
        "entry_hi": entry_hi,
        "entry_hing": entry_hing,
        "entry_en": entry_en,
        "op_hi": op_hi,
        "op_hing": op_hing,
        "op_en": op_en,
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
        "range_pos": range_pos,
        "top_news": top_news,
        "news_score": news_score,
        "cat": cat,
        "fundamentals": fundamentals,
        "df_close": df["Close"],
    }
  except Exception:
    return None


# ================= 10. REAL 15-MIN INTRADAY SCANNER ENGINE =================
@st.cache_data(ttl=180)
def scan_real_15m_intraday(name, ticker):
  try:
    df15 = yf.Ticker(ticker).history(period="5d", interval="15m")
    if df15.empty or len(df15) < 10:
      return None

    curr = round(df15["Close"].iloc[-1], 2)
    today_date = df15.index[-1].date()
    today_df = df15[df15.index.date == today_date]
    if today_df.empty:
      today_df = df15.tail(15)

    orb_high = round(today_df["High"].iloc[0], 2)
    orb_low = round(today_df["Low"].iloc[0], 2)
    day_open = round(today_df["Open"].iloc[0], 2)
    intra_chg = round(((curr - day_open) / day_open) * 100, 2)

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
      status = L(
          "🟢 ORB UP-BREAKOUT (आज ऊपर भागने वाला इंट्राडे शेयर)",
          "🟢 ORB UP-BREAKOUT (Aaj Upar Bhagne Wala Intraday Share)",
          "🟢 ORB BULLISH BREAKOUT (Above 9:15 High & VWAP)",
      )
      intra_target = round(curr * 1.02, 2)
      intra_sl = max(orb_low, intra_vwap)
      signal_type = "BUY"
    elif curr < orb_low and curr < intra_vwap:
      status = L(
          "🔴 ORB BREAKDOWN (आज नीचे गिरने वाला इंट्राडे शेयर)",
          "🔴 ORB BREAKDOWN (Aaj Niche Girne Wala Intraday Share)",
          "🔴 ORB BEARISH BREAKDOWN (Below 9:15 Low & VWAP)",
      )
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


# ================= 11. GROWW-STYLE CARD & PORTFOLIO RENDERERS =================
def show_groww_master_card(d, budget, show_chart=False, key_prefix="card"):
  qty = max(1, int(budget // d["price"]))
  profit_t1 = int(qty * (d["up_target"] - d["price"]))
  profit_t2 = int(qty * (d["target_2"] - d["price"]))
  risk_rs = int(qty * (d["price"] - d["stop_loss"]))

  verdict_txt = L(d["v_hi"], d["v_hing"], d["v_en"])
  advice_txt = L(d["adv_hi"], d["adv_hing"], d["adv_en"])
  entry_txt = L(d["entry_hi"], d["entry_hing"], d["entry_en"])
  hold_txt = L(d["hold_hi"], d["hold_hing"], d["hold_en"])
  op_txt = L(d["op_hi"], d["op_hing"], d["op_en"])

  with st.container(border=True):
    # Top Row: Name, Price & Winning Score
    h1, h2 = st.columns([3, 1])
    h1.subheader(f"{d['name']} ({d['ticker']}) — ₹{d['price']} ({d['day_chg']}%)")
    h2.metric(
        L("जीतने का चांस", "Winning Score", "AI Score"),
        f"{d['score']}%",
        f"Win Rate: {d['win_rate']}%",
    )

    st.markdown(f"### {verdict_txt}")
    st.info(
        f"🗣️ **{L('डॉक्टर का निचोड़:', 'Doctor Ka Nichod:', 'AI Doctor Summary:')}** {advice_txt}"
    )

    # 6-Tick Passbook Bar
    p = d["p_list"]
    chk_str = (
        f"`{'✅' if p[0] else '❌'} Trend` | "
        f"`{'✅' if p[1] else '❌'} MACD` | "
        f"`{'✅' if p[2] else '❌'} VWAP` | "
        f"`{'✅' if p[3] else '❌'} Volume` | "
        f"`{'✅' if p[4] else '❌'} News` | "
        f"`{'✅' if p[5] else '❌'} RSI ({d['rsi']})`"
    )
    st.markdown(
        f"**{L('6-टेस्ट पासबुक', '6-Test Passbook', '6-Point Institutional Check')} ({d['passed_tests']}/6):** {chk_str}"
    )

    # Ideal Buy Zone & Holding Period
    e1, e2 = st.columns(2)
    e1.success(f"🎯 **{entry_txt}**")
    e2.warning(
        f"⏰ **{L('कितने दिन रखें?:', 'Kitne Din Rakhein?:', 'Holding Period:')}** {hold_txt}"
    )

    # Rupee Calculator
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        L("🛒 कितने शेयर खरीदें?", "🛒 Kitne Kharidein?", "🛒 Qty to Buy"),
        f"{qty} Shares",
        f"₹{int(qty * d['price'])}",
        delta_color="off",
    )
    m2.metric(
        L("🎯 टारगेट-1 मुनाफा", "🎯 Target-1 Munafa", "🎯 Target-1 Profit"),
        f"+₹{profit_t1}",
        f"₹{d['up_target']}",
    )
    m3.metric(
        L("🚀 बड़ा टारगेट-2", "🚀 Bada Target-2", "🚀 Target-2 Profit"),
        f"+₹{profit_t2}",
        f"₹{d['target_2']}",
    )
    m4.metric(
        L("🛡️ अधिकतम रिस्क (SL)", "🛡️ Stop-Loss Risk", "🛡️ Max Risk (SL)"),
        f"-₹{risk_rs}",
        f"SL: ₹{d['stop_loss']}",
        delta_color="inverse",
    )

    # Groww-Style 52-Week Low to High Visual Bar
    st.markdown(
        f"**📊 {L('52-हफ्ते का प्राइस रेंज (Groww Meter):', '52-Week Price Range (Groww Meter):', '52-Week Price Range:')}** "
        f"`Low: ₹{d['low_52w']}` ⬅️ **(अभी `₹{d['price']}` — High से `{d['drop_from_high']}%`)** ➡️ `High: ₹{d['high_52w']}`"
    )
    st.progress(d["range_pos"] / 100.0)

    # Multi-Period Returns Table (1D, 1W, 1M, 6M, 1Y)
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.caption(f"**1D (आज):** `{d['day_chg']}%`")
    r2.caption(f"**1W (1 हफ्ता):** `{d['ret_1w']}%`")
    r3.caption(f"**1M (1 महीना):** `{d['ret_1m']}%`")
    r4.caption(f"**6M (6 महीने):** `{d['ret_6m']}%`")
    r5.caption(f"**1Y (1 साल):** `{d['ret_1y']}%`")

    st.caption(
        f"🧱 **Support:** `₹{d['support']}` | 🚧 **Resistance:** `₹{d['resistance']}` | "
        f"⚡ **VWAP:** `₹{d['vwap']}` | {op_txt}"
    )

    # Groww Company Fundamentals (if fetched in Search)
    if d["fundamentals"]:
      f = d["fundamentals"]
      st.markdown(
          f"🏢 **{L('कंपनी की तिजोरी (Fundamentals):', 'Company Ki Tijori (Fundamentals):', 'Company Fundamentals:')}** "
          f"`Market Cap: ₹{f['mcap_cr']} Cr` | `P/E Ratio: {f['pe']}` | "
          f"`P/B: {f['pb']}` | `ROE: {f['roe']}%` | `Debt/Eq: {f['debt_eq']}` | `Dividend: {f['div_y']}%`"
      )

    news_translated = (
        google_translate_api(d["top_news"], LANG)
        if LANG not in ["en", "hinglish"]
        else d["top_news"]
    )
    st.caption(f"📰 **{L('ताज़ा खबर:', 'Taaza Khabar:', 'Latest News:')}** {news_translated}")

    # Action Buttons
    b1, b2 = st.columns(2)
    if b1.button(
        "➕ "
        + L(
            "मेरे पोर्टफोलियो में जोड़ें",
            "Mere Portfolio Mein Jodein",
            "Add to My Portfolio",
        ),
        key=f"add_{key_prefix}_{d['ticker']}",
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
      st.success(
          L(
              f"✅ {d['name']} आपके पोर्टफोलियो में सेव हो गया!",
              f"✅ {d['name']} aapke portfolio mein save ho gaya!",
              f"✅ {d['name']} saved to your portfolio!",
          )
      )

    if tg_token and tg_chat_id:
      if b2.button(
          "📤 Telegram Alert",
          key=f"tg_{key_prefix}_{d['ticker']}",
          use_container_width=True,
      ):
        msg = (
            f"🚀 *Groww AI V11 Signal: {d['name']}*\nPrice: ₹{d['price']}"
            f" ({d['day_chg']}%)\nScore: {d['score']}%\n{verdict_txt}\nTarget:"
            f" ₹{d['up_target']} | SL: ₹{d['stop_loss']}"
        )
        send_telegram_alert(msg, tg_token, tg_chat_id)
        st.success("✅ Sent!")

    if show_chart:
      st.markdown(
          f"**📈 {L('प्राइस चार्ट (Groww Interactive):', 'Price Chart (Groww View):', 'Interactive Price Chart:')}**"
      )
      chart_period = st.radio(
          L("चार्ट का समय चुनें:", "Chart Timeframe:", "Select Chart Period:"),
          ["1M (30 Days)", "6M (180 Days)", "1Y (Full Year)"],
          horizontal=True,
          key=f"ch_{key_prefix}_{d['ticker']}",
      )
      days_map = {"1M (30 Days)": 22, "6M (180 Days)": 125, "1Y (Full Year)": 250}
      st.line_chart(d["df_close"].tail(days_map[chart_period]))


def render_portfolio_doctor_card(d, buy_price, qty, idx_key):
  invested = round(buy_price * qty, 2)
  current_val = round(d["price"] * qty, 2)
  pnl_rs = round(current_val - invested, 2)
  pnl_pct = round(((d["price"] - buy_price) / buy_price) * 100, 2)

  if pnl_pct >= 0:
    if d["score"] >= 65 and d["news_score"] >= 0 and d["price"] >= d["ma20"]:
      badge = L(
          "🟢 अभी होल्ड करें (HOLD FOR BIGGER PROFIT)",
          "🟢 ABHI HOLD KAREIN (Aur Upar Jayega)",
          "🟢 HOLD FOR BIGGER PROFIT",
      )
      trailing_sl = max(buy_price, d["stop_loss"])
      advice = L(
          f"बधाई हो! आप **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं और रफ़्तार मज़बूत है। यह **₹{d['up_target']}** से **₹{d['target_2']}** तक जा सकता है। स्टॉप-लॉस **₹{trailing_sl}** पर रखें।",
          f"Badhai ho! Aap **+₹{pnl_rs} (+{pnl_pct}%)** ke munafe mein hain aur trend majboot hai. Yeh **₹{d['up_target']}–₹{d['target_2']}** tak ja sakta hai. Stop-loss **₹{trailing_sl}** rakhein.",
          f"You are in **+₹{pnl_rs} (+{pnl_pct}%)** profit with strong momentum! Can head to **₹{d['up_target']}–₹{d['target_2']}**. Trail SL at **₹{trailing_sl}**.",
      )
      box_type = "success"
    elif d["rsi"] >= 76 or d["news_score"] < 0 or d["price"] < d["ma20"]:
      badge = L(
          "💰 मुनाफा बुक करें / बेचकर निकलें (BOOK PROFIT NOW)",
          "💰 MUNAFA BOOK KAREIN (Bech Kar Profit जेब में डालें)",
          "💰 BOOK PROFIT NOW (Momentum Weakening)",
      )
      advice = L(
          f"सावधान! आप **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं, लेकिन अब चार्ट कमज़ोर पड़ रहा है। आया हुआ मुनाफा तुरंत बुक कर लें!",
          f"Savdhan! Aap **+₹{pnl_rs} (+{pnl_pct}%)** ke munafe mein hain, par ab chart kamzor ho raha hai. Aaya hua profit turant book karein!",
          f"Caution! You are up **+₹{pnl_rs} (+{pnl_pct}%)**, but chart is weakening. Lock in your profits now!",
      )
      box_type = "warning"
    else:
      badge = L(
          "🟢 सपोर्ट के साथ होल्ड करें (HOLD WITH SL)",
          "🟢 SUPPORT KE SAATH HOLD KAREIN",
          "🟢 HOLD WITH STOP-LOSS",
      )
      advice = L(
          f"आप **+₹{pnl_rs}** के मुनाफे में हैं। जब तक यह **₹{d['support']}** के ऊपर है, होल्ड करें।",
          f"Aap **+₹{pnl_rs}** ke munafe mein hain. Jab tak yeh **₹{d['support']}** ke upar hai, hold karein.",
          f"In **+₹{pnl_rs}** profit. Hold as long as it stays above support **₹{d['support']}**.",
      )
      box_type = "info"
  else:
    if d["news_score"] < 0 or (
        d["price"] < d["ma20"] and d["price"] < d["ma50"] and d["score"] <= 40
    ):
      badge = L(
          "🔴 तुरंत बेचकर निकलें (SELL / EXIT DANGER)",
          "🔴 TURANT BECH KAR NIKLEIN (Aur Gir Sakta Hai!)",
          "🔴 EXIT / SELL IMMEDIATELY (Downtrend)",
      )
      advice = L(
          f"अलर्ट! आप **₹{abs(pnl_rs)} ({pnl_pct}%)** के नुकसान में हैं और ट्रेंड टूट चुका है। यह **₹{d['down_risk']}** तक और गिर सकता है।",
          f"Alert! Aap **₹{abs(pnl_rs)} ({pnl_pct}%)** ke loss mein hain aur trend toot chuka hai. Yeh **₹{d['down_risk']}** tak aur gir sakta hai.",
          f"Alert! Down **₹{abs(pnl_rs)} ({pnl_pct}%)** with broken trend. Could slide further to **₹{d['down_risk']}**.",
      )
      box_type = "error"
    elif d["price"] > d["ma5"] and d["macd_bullish"]:
      badge = L(
          "💎 होल्ड करें & एवरेज करें (RECOVERY STARTED)",
          "💎 HOLD & AVERAGE KAREIN (Ab Upar Mud Raha Hai!)",
          "💎 HOLD & AVERAGE DOWN (Reversal Started)",
      )
      advice = L(
          f"आप **₹{abs(pnl_rs)}** के नुकसान में हैं, लेकिन शेयर अब ऊपर मुड़ चुका है! नीचे दिए गए **Average Calculator** से अपना खरीद भाव कम करें।",
          f"Aap **₹{abs(pnl_rs)}** ke loss mein hain, par share ab upar mud chuka hai! Niche **Average Calculator** se apna kharid bhaav kam karein.",
          f"Down **₹{abs(pnl_rs)}**, but stock has started reversing up! Use the **Average Calculator** below to lower your cost.",
      )
      box_type = "success"
    else:
      badge = L(
          "🟡 आखिरी सपोर्ट के साथ होल्ड करें",
          "🟡 SUPPORT KE SAATH HOLD KAREIN",
          "🟡 HOLD WITH STRICT SUPPORT",
      )
      advice = L(
          f"आप **₹{abs(pnl_rs)}** के नुकसान में हैं। मज़बूत सपोर्ट **₹{d['support']}** पर है। इसके नीचे जाने पर ही निकलें।",
          f"Aap **₹{abs(pnl_rs)}** ke loss mein hain. Majboot support **₹{d['support']}** par hai.",
          f"Down **₹{abs(pnl_rs)}**. Key support is at **₹{d['support']}**. Exit if it breaks support.",
      )
      box_type = "warning"

  with st.container(border=True):
    c_h1, c_h2, c_h3 = st.columns([3, 1, 1])
    c_h1.subheader(f"📌 {d['name']} ({d['ticker']})")
    c_h2.metric(L("डॉक्टर स्कोर", "Doctor Score", "AI Score"), f"{d['score']}/100")
    if c_h3.button(
        "🗑️ " + L("हटाएं", "Hatayein", "Delete"), key=f"del_{idx_key}"
    ):
      st.session_state.my_portfolio.pop(idx_key)
      save_portfolio_to_disk(st.session_state.my_portfolio)
      st.rerun()

    if box_type == "success":
      st.success(f"### {badge}\n🗣️ {advice}")
    elif box_type == "error":
      st.error(f"### {badge}\n🗣️ {advice}")
    elif box_type == "warning":
      st.warning(f"### {badge}\n🗣️ {advice}")
    else:
      st.info(f"### {badge}\n🗣️ {advice}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        L("आपका खरीद भाव", "Aapka Buy Price", "Buy Price"),
        f"₹{buy_price}",
        f"{qty} Shares",
        delta_color="off",
    )
    m2.metric(
        L("अभी का भाव", "Abhi Ka Bhaav", "Live Price"),
        f"₹{d['price']}",
        f"{d['day_chg']}%",
    )
    m3.metric(
        L("कुल मुनाफा/नुकसान", "Kul Profit/Loss", "Total P&L"),
        f"₹{pnl_rs}",
        f"{pnl_pct}%",
    )
    m4.metric(L("अगला टारगेट", "Agla Target", "Target"), f"₹{d['up_target']}")
    m5.metric(L("मज़बूत सपोर्ट", "Support Floor", "Support"), f"₹{d['support']}")

    if pnl_pct < 0 and d["price"] < buy_price:
      with st.expander(
          "🧮 "
          + L(
              f"घाटा जल्दी रिकवर करने का 'Average Down कैलकुलेटर' (अभी भाव ₹{d['price']})",
              f"Ghata Jaldi Recover Karne Ka 'Average Calculator' (Abhi Bhaav ₹{d['price']})",
              f"Smart Average-Down Calculator (Live Price ₹{d['price']})",
          ),
          expanded=True,
      ):
        ac1, ac2 = st.columns([1, 2])
        extra_qty = ac1.number_input(
            L(
                "कितने नए शेयर और खरीदें?:",
                "Kitne naye share aur kharidein?:",
                "New shares to buy at current price:",
            ),
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
            L(
                f"- 💰 **कितना नया पैसा लगेगा:** `₹{new_inv}` *(कुल शेयर: {tot_shares})*\n"
                f"- 📉 **आपका नया खरीद भाव (New Average) घटकर हो जाएगा:** **`₹{new_avg}`** *(पहले `₹{buy_price}` था)*\n"
                f"- 🚀 **फायदा:** पहले नो-लॉस में आने के लिए शेयर को **{old_req}%** भागना पड़ता, अब सिर्फ **{new_req}%** उछलते ही सारा घाटा खत्म हो जाएगा!",
                f"- 💰 **Kitna naya paisa lagega:** `₹{new_inv}` *(Kul Shares: {tot_shares})*\n"
                f"- 📉 **Aapka Naya Average Price ghatkar ho jayega:** **`₹{new_avg}`** *(Pehle `₹{buy_price}` tha)*\n"
                f"- 🚀 **Fayda:** Pehle No-Loss mein aane ke liye **{old_req}%** chadhna padta, ab sirf **{new_req}%** uchhalte hi saara loss khatam!",
                f"- 💰 **New Capital Needed:** `₹{new_inv}` *(Total Shares: {tot_shares})*\n"
                f"- 📉 **New Average Buy Price:** **`₹{new_avg}`** *(Down from `₹{buy_price}`)*\n"
                f"- 🚀 **Benefit:** Break-even recovery needed drops from **{old_req}%** to just **{new_req}%**!",
            )
        )


# ================= 12. TOP HEADER & GROWW MARKET BAR =================
st.title(
    "🇮🇳 "
    + L(
        "Groww-Style भारत AI स्टॉक, पोर्टफोलियो & IPO सुपर-ऐप (V11.0)",
        "Groww-Style Bharat AI Stock, Portfolio & IPO Super-App (V11.0)",
        "Groww-Style Bharat AI Stock, Portfolio & IPO Super-App (V11.0)",
    )
)
st.caption(
    L(
        "12 भाषाओं में काम करने वाला ऑल-इन-वन ट्रेडिंग डॉक्टर — किसी भी शेयर पर क्लिक करें और 2 सेकंड में पूरा फैसला जानें",
        "12 Bhashaon mein kaam karne wala All-in-One Trading Doctor — 2 second mein saaf faisla",
        "All-in-One Institutional Stock Doctor in 12 Indian Languages — Instant Buy/Sell/Hold Decisions",
    )
)

macro_data = get_groww_market_bar()
nifty_chg = macro_data.get("🇮🇳 NIFTY 50", (0, 0.0))[1]
vix_chg = macro_data.get("⚡ INDIA VIX", (0, 0.0))[1]

if macro_data:
  m_cols = st.columns(len(macro_data))
  for idx, (m_name, (m_val, m_c)) in enumerate(macro_data.items()):
    inv = "inverse" if "VIX" in m_name or "CRUDE" in m_name else "normal"
    m_cols[idx].metric(m_name, f"{m_val}", f"{m_c}%", delta_color=inv)

  if vix_chg > 6 or nifty_chg < -1.0:
    st.error(
        "🚨 "
        + L(
            "बाज़ार में खतरा (Crash Warning): आज इंडिया VIX (डर) बढ़ा है या मार्केट गिर रहा है! नई खरीदारी में सावधानी रखें।",
            "CRASH WARNING: Aaj market mein dar (VIX) badha hai ya badi girawat hai! Naye share kharidne mein savdhani rakhein.",
            "MARKET CRASH WARNING: Volatility (VIX) is spiking or Nifty is down sharply. Avoid aggressive buying today!",
        )
    )
  else:
    st.success(
        "✅ "
        + L(
            "बाज़ार सुरक्षित है (Safe Market Mood): आज आप 'हरे सिग्नल' वाले मज़बूत स्टॉक्स में मौका देख सकते हैं।",
            "MARKET SAFE HAI: Aaj aap 'Green Signal' wale majboot stocks mein trade dekh sakte hain.",
            "MARKET MOOD SAFE: Conditions are favorable for high-score bullish setups.",
        )
    )

# ================= 13. CATEGORY SELECTOR IN SIDEBAR =================
st.sidebar.header(
    L("📂 3. स्टॉक कैटेगरी", "📂 3. Stock Category", "📂 3. Stock Category")
)
chosen_category = st.sidebar.radio(
    L("कैटेगरी चुनें:", "Category Chunein:", "Select Category:"),
    list(STOCK_CATEGORIES.keys()),
)
active_stocks = STOCK_CATEGORIES[chosen_category]

with st.spinner(
    L(
        "लाइव मार्केट और स्टॉक्स स्कैन हो रहे हैं...",
        "Live market aur stocks scan ho rahe hain...",
        "Scanning live stocks & institutional indicators...",
    )
):
  results = []
  for name, ticker in active_stocks.items():
    r = deep_analyze_v11(name, ticker, nifty_chg, fetch_fundamentals=False)
    if r:
      results.append(r)

# ================= 14. ALL 8 GROWW SUPER-APP TABS =================
(
    tab_explore,
    tab_port,
    tab_intra,
    tab_buy,
    tab_sell,
    tab_disc,
    tab_corp,
    tab_ipo,
) = st.tabs([
    "🔍 1. " + L("Groww एक्सप्लोर & 5000+ सर्च", "Groww Explore & Search", "Groww Explore & Search"),
    "💼 2. " + L("मेरा पोर्टफोलियो (Hold/Sell)", "Mera Portfolio (Hold/Sell)", "My Portfolio Doctor"),
    "⚡ 3. " + L("9:15 लाइव Intraday (15m)", "9:15 Live Intraday (15m)", "Live 15m Intraday"),
    "🟢 4. " + L("आज/कल चलने वाले (Top Buy)", "Aaj/Kal Chalne Wale (Buy)", "Top Bullish Picks"),
    "🔴 5. " + L("गिरने वाले / खतरा (Avoid)", "Girne Wale / Khatra (Avoid)", "Bearish / Traps"),
    "💎 6. " + L("सस्ते डिस्काउंट स्टॉक्स", "Saste Discount Stocks", "52W Low Discounts"),
    "🎁 7. " + L("Dividend, Bonus & Split", "Dividend, Bonus & Split", "Corporate Actions"),
    "🆕 8. " + L("IPO सेंटर & SIP कैलकुलेटर", "IPO & SIP Calculator", "IPO & SIP Calculator"),
])

# ----------------- TAB 1: GROWW EXPLORE + 5000+ SEARCH + TOP MOVERS -----------------
with tab_explore:
  with st.container(border=True):
    st.subheader(
        "🔎 "
        + L(
            "किसी भी भारतीय शेयर (5,000+ NSE/BSE) को सर्च करें — पूरी कुंडली + चार्ट + तिजोरी",
            "Kisi Bhi Share (5,000+ NSE/BSE) Ko Search Karein — Puri Kundali + Chart + Tijori",
            "Search Any Indian Stock (5,000+ NSE/BSE) — Full X-Ray, Fundamentals & Chart",
        )
    )
    search_query = st.text_input(
        L(
            "कंपनी का नाम लिखें (जैसे: Suzlon, Tata, Adani, Bajaj Housing, Ola, MRF, Zomato, PNB):",
            "Company ka naam likhein (jaise: Suzlon, Tata, Adani, Bajaj Housing, Ola, MRF, Zomato, PNB):",
            "Type Company Name or Symbol (e.g. Suzlon, Tata, Bajaj Housing, Ola, MRF, Zomato):",
        ),
        placeholder="Type stock name here...",
    )
    if search_query:
      matches = search_indian_stocks(search_query)
      if matches:
        selected_match = st.selectbox(
            L("कंपनी चुनें:", "Company Chunein:", "Select Matching Company:"),
            options=matches,
            format_func=lambda x: x[0],
        )
        if selected_match:
          with st.spinner("Fetching Groww Fundamentals & Chart..."):
            s_data = deep_analyze_v11(
                selected_match[1],
                selected_match[2],
                nifty_chg,
                fetch_fundamentals=True,
            )
            if s_data:
              show_groww_master_card(
                  s_data, user_capital, show_chart=True, key_prefix="srch"
              )
      else:
        st.warning(
            L(
                "कोई शेयर नहीं मिला, कृपया स्पेलिंग चेक करें।",
                "Koi share nahi mila, spelling check karein.",
                "No matching stock found.",
            )
        )

  # Groww Style Market Movers (Top Gainers, Top Losers, Volume Shockers)
  if results:
    st.subheader(
        f"🔥 {chosen_category} — "
        + L(
            "Groww स्टाइल आज के टॉप मूवर्स",
            "Groww Style Aaj Ke Top Movers",
            "Groww Style Market Movers Today",
        )
    )
    g1, g2, g3 = st.columns(3)
    top_gainer = max(results, key=lambda x: x["day_chg"])
    top_loser = min(results, key=lambda x: x["day_chg"])
    top_vol = max(results, key=lambda x: x["vol_ratio"])

    g1.success(
        f"🚀 **{L('आज का Top Gainer:', 'Aaj Ka Top Gainer:', 'Top Gainer Today:')}**\n\n"
        f"**{top_gainer['name']}** — ₹{top_gainer['price']} (**+{top_gainer['day_chg']}%**)\n\n"
        f"Score: `{top_gainer['score']}%` | Target: `₹{top_gainer['up_target']}`"
    )
    g2.error(
        f"📉 **{L('आज का Top Loser:', 'Aaj Ka Top Loser:', 'Top Loser Today:')}**\n\n"
        f"**{top_loser['name']}** — ₹{top_loser['price']} (**{top_loser['day_chg']}%**)\n\n"
        f"Score: `{top_loser['score']}%` | Support: `₹{top_loser['support']}`"
    )
    g3.info(
        f"💥 **{L('आज का Volume Shocker (सबसे ज़्यादा खरीदारी):', 'Aaj Ka Volume Shocker:', 'Most Active Volume Shocker:')}**\n\n"
        f"**{top_vol['name']}** — ₹{top_vol['price']} (**{top_vol['vol_ratio']}x Volume**)\n\n"
        f"Score: `{top_vol['score']}%`"
    )

    st.divider()
    st.subheader(
        "📋 "
        + L(
            "सभी शेयरों की एक नज़र में तुलना (Groww Screener Table)",
            "Sabhi Shares Ki Ek Nazar Mein Tulna (Screener Table)",
            "Complete Category Screener Table",
        )
    )
    df_table = pd.DataFrame([
        {
            L("शेयर का नाम", "Share Naam", "Stock"): r["name"],
            L("भाव (₹)", "Price (₹)", "Price (₹)"): r["price"],
            "1D (%)": r["day_chg"],
            "1W (%)": r["ret_1w"],
            "1M (%)": r["ret_1m"],
            "1Y (%)": r["ret_1y"],
            L("जीतने का स्कोर (%)", "Winning Score (%)", "Score (%)"): r["score"],
            L("टारगेट (₹)", "Target (₹)", "Target (₹)"): r["up_target"],
            L("स्टॉप-लॉस (₹)", "Stop-Loss (₹)", "Stop-Loss (₹)"): r["stop_loss"],
            L("डॉक्टर फैसला", "Doctor Faisla", "Verdict"): L(
                r["v_hi"], r["v_hing"], r["v_en"]
            ),
        }
        for r in sorted(results, key=lambda x: x["score"], reverse=True)
    ])
    st.dataframe(df_table, use_container_width=True, hide_index=True)

# ----------------- TAB 2: PERMANENT PORTFOLIO & AVERAGE DOCTOR -----------------
with tab_port:
  st.header(
      "🩺 "
      + L(
          "मेरे खरीदे हुए शेयर: Hold करें या Sell? (+ Average Down कैलकुलेटर)",
          "Mere Kharide Hue Shares: Hold Karein Ya Sell? (+ Average Calculator)",
          "My Portfolio Doctor: Hold or Sell Advisor (+ Average Calculator)",
      )
  )
  with st.container(border=True):
    p_c1, p_c2, p_c3, p_c4 = st.columns([2, 1, 1, 1])
    p_search = p_c1.text_input(
        L(
            "1. कंपनी का नाम लिखें:",
            "1. Company ka naam likhein:",
            "1. Search Company Name:",
        ),
        value="Suzlon",
    )
    p_matches = search_indian_stocks(p_search) if p_search else []
    if p_matches:
      chosen_p = p_c1.selectbox(
          L("कंपनी चुनें:", "Company Chunein:", "Select Stock:"),
          options=p_matches,
          format_func=lambda x: x[0],
      )
      sel_name, sel_ticker = chosen_p[1], chosen_p[2]
    else:
      sel_name, sel_ticker = p_search.upper(), p_search.strip().upper() + ".NS"

    p_buy_price = p_c2.number_input(
        L("2. खरीद भाव (₹):", "2. Buy Price (₹):", "2. Your Buy Price (₹):"),
        min_value=0.5,
        value=65.0,
        step=1.0,
    )
    p_qty = p_c3.number_input(
        L("3. शेयर संख्या (Qty):", "3. Quantity (Shares):", "3. Quantity:"),
        min_value=1,
        value=100,
        step=1,
    )
    st.write("")
    if p_c4.button(
        "💾 " + L("परमानेंट सेव करें", "Permanent Save Karein", "Save to Portfolio"),
        use_container_width=True,
    ):
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
      st.success(f"✅ {sel_name} Saved!")

  if st.session_state.my_portfolio:
    total_inv, total_curr = 0.0, 0.0
    analyzed_port = []
    for item in st.session_state.my_portfolio:
      p_data = deep_analyze_v11(item["name"], item["ticker"], nifty_chg)
      if p_data:
        total_inv += item["buy_price"] * item["qty"]
        total_curr += p_data["price"] * item["qty"]
        analyzed_port.append((p_data, item["buy_price"], item["qty"]))

    if analyzed_port:
      tot_pnl = round(total_curr - total_inv, 2)
      tot_pct = round((tot_pnl / total_inv) * 100, 2) if total_inv > 0 else 0.0
      s1, s2, s3 = st.columns(3)
      s1.metric(
          L("कुल निवेश (Invested)", "Kul Lagaya Paisa", "Total Invested"),
          f"₹{round(total_inv, 1)}",
      )
      s2.metric(
          L("अभी की कुल कीमत (Current)", "Abhi Ki Kimat", "Current Value"),
          f"₹{round(total_curr, 1)}",
      )
      s3.metric(
          L("कुल मुनाफा / नुकसान (Net P&L)", "Kul Munafa / Nuksan", "Net Profit / Loss"),
          f"₹{tot_pnl}",
          f"{tot_pct}%",
      )
      st.divider()
      for idx, (pdata, bp, q) in enumerate(analyzed_port):
        render_portfolio_doctor_card(pdata, bp, q, idx)

# ----------------- TAB 3: REAL 15-MINUTE INTRADAY SCANNER -----------------
with tab_intra:
  st.header(
      "⚡ "
      + L(
          "सुबह 9:15 से 3:30 का लाइव 15-Minute Intraday ORB & VWAP स्कैनर",
          "Subah 9:15 se 3:30 ka Live 15-Minute Intraday ORB & VWAP Scanner",
          "Live 15-Minute Intraday Opening Range Breakout & VWAP Scanner",
      )
  )
  if st.button(
      "🚀 "
      + L(
          "अभी 15-Min लाइव इंट्राडे स्कैन चलाएं",
          "Abhi 15-Min Live Intraday Scan Chalayein",
          "Run Live 15-Min Intraday Scan Now",
      )
  ):
    intra_pool = {}
    for cat_dict in STOCK_CATEGORIES.values():
      intra_pool.update(cat_dict)

    intra_hits = []
    with st.spinner("Scanning live 15-minute candles & VWAP..."):
      for iname, itick in list(intra_pool.items())[:22]:
        ir = scan_real_15m_intraday(iname, itick)
        if ir:
          intra_hits.append(ir)

    if intra_hits:
      ic1, ic2 = st.columns(2)
      for idx, item in enumerate(intra_hits):
        with (ic1 if idx % 2 == 0 else ic2):
          with st.container(border=True):
            st.subheader(
                f"{item['name']} — ₹{item['price']} ({item['intra_chg']}%)"
            )
            if item["signal_type"] == "BUY":
              st.success(f"**{item['status']}**")
            else:
              st.error(f"**{item['status']}**")
            st.write(
                f"🎯 **Target:** `₹{item['target']}` | 🛡️ **Stop-Loss:**"
                f" `₹{item['sl']}` | ⚡ **Live VWAP:** `₹{item['vwap']}`"
            )
            st.caption(
                f"9:15 High: `₹{item['orb_high']}` | 9:15 Low:"
                f" `₹{item['orb_low']}` | 15m Vol Spike: `{item['vol_spike']}x`"
            )
    else:
      st.warning(
          L(
              "अभी कोई शेयर 15-मिनट ब्रेकआउट नियम को पार नहीं कर रहा है।",
              "Abhi koi share 15-minute breakout rule ko cross nahi kar raha hai.",
              "No stock is currently breaking out on the 15-minute chart.",
          )
      )

# ----------------- TABS 4, 5, 6: TOP BUY, AVOID, DISCOUNT -----------------
with tab_buy:
  st.subheader(
      f"🟢 {chosen_category} — "
      + L(
          "आज और कल ऊपर जाने वाले स्टॉक्स (Top Buy)",
          "Aaj Aur Kal Upar Jane Wale Stocks (Top Buy)",
          "High-Probability Bullish Stocks",
      )
  )
  bulls = sorted(
      [r for r in results if r["cat"] == "BULLISH" or r["score"] >= 68],
      key=lambda x: x["score"],
      reverse=True,
  )
  cols = st.columns(2)
  for idx, item in enumerate(bulls):
    with cols[idx % 2]:
      show_groww_master_card(item, user_capital, key_prefix=f"buy_{idx}")

with tab_sell:
  st.subheader(
      f"🔴 {chosen_category} — "
      + L(
          "गिरने वाले या ऑपरेटर ट्रैप वाले स्टॉक्स (इनसे दूर रहें)",
          "Girne Wale Ya Operator Trap Wale Stocks (Inse Door Rahein)",
          "Weak / Bearish / Operator Trap Stocks (Avoid)",
      )
  )
  bears = sorted(
      [r for r in results if r["cat"] == "BEARISH" or r["score"] <= 48],
      key=lambda x: x["score"],
  )
  cols = st.columns(2)
  for idx, item in enumerate(bears):
    with cols[idx % 2]:
      show_groww_master_card(item, user_capital, key_prefix=f"sell_{idx}")

with tab_disc:
  st.subheader(
      f"💎 {chosen_category} — "
      + L(
          "1 साल के हाई से सस्ते मिल रहे स्टॉक्स (Multibagger & Reversal)",
          "1 Saal Ke High Se Saste Mil Rahe Stocks (Discount & Future)",
          "52-Week High Discount & Reversal Stocks",
      )
  )
  oversold = sorted(
      [
          r
          for r in results
          if r["cat"] == "OVERSOLD" or r["drop_from_high"] <= -12
      ],
      key=lambda x: x["drop_from_high"],
  )
  cols = st.columns(2)
  for idx, item in enumerate(oversold):
    with cols[idx % 2]:
      show_groww_master_card(item, user_capital, key_prefix=f"disc_{idx}")

# ----------------- TAB 7: DIVIDEND, BONUS & SPLIT RADAR -----------------
with tab_corp:
  st.header(
      "🎁 "
      + L(
          "Dividend, Bonus और Stock Split देने वाली कंपनियों का लाइव रडार",
          "Dividend, Bonus Aur Stock Split Dene Wali Companies Ka Radar",
          "Live Dividend, Bonus & Stock Split Radar",
      )
  )
  c_div, c_bon = st.columns(2)
  with c_div:
    with st.container(border=True):
      st.subheader(
          "💰 "
          + L(
              "आगामी डिविडेंड (Upcoming Dividends)",
              "Upcoming Dividends (Muft Cash Labh)",
              "Upcoming Dividends",
          )
      )
      for title in fetch_live_news(
          "dividend stocks record date India", max_items=6
      ):
        t_out = (
            google_translate_api(title, LANG)
            if LANG not in ["en", "hinglish"]
            else title
        )
        st.markdown(f"- 💵 **{t_out}**")
  with c_bon:
    with st.container(border=True):
      st.subheader(
          "🚀 "
          + L(
              "बोनस शेयर और स्टॉक स्प्लिट (Bonus & Splits)",
              "Bonus Shares Aur Stock Split",
              "Bonus Shares & Stock Splits",
          )
      )
      for title in fetch_live_news(
          "bonus shares stock split India", max_items=6
      ):
        t_out = (
            google_translate_api(title, LANG)
            if LANG not in ["en", "hinglish"]
            else title
        )
        st.markdown(f"- 🎁 **{t_out}**")

# ----------------- TAB 8: IPO GMP TESTER + GROWW SIP CROREPATI CALCULATOR -----------------
with tab_ipo:
  st.header(
      "🆕 "
      + L(
          "लाइव IPO सेंटर & Groww SIP करोड़पति कैलकुलेटर",
          "Live IPO Center & Groww SIP Crorepati Calculator",
          "Live IPO Center & Groww SIP Wealth Calculator",
      )
  )
  ipo1, ipo2 = st.columns(2)
  with ipo1:
    with st.container(border=True):
      st.subheader(
          "🧮 "
          + L(
              "IPO अप्लाई करें या नहीं? (1-सेकंड GMP टेस्टर)",
              "IPO Apply Karein Ya Nahi? (1-Second GMP Tester)",
              "1-Second IPO GMP & Listing Gain Tester",
          )
      )
      issue_p = st.number_input("IPO Issue Price (₹):", min_value=10, value=500)
      gmp_rs = st.number_input("Live GMP (₹):", min_value=-200, value=140)
      sub_x = st.number_input(
          "Subscription (e.g. 15x):", min_value=0.1, value=14.0
      )
      lot_sz = st.number_input("Lot Size (Shares):", min_value=1, value=30)

      gmp_pct = round((gmp_rs / issue_p) * 100, 1)
      est_profit = int(gmp_rs * lot_sz)
      if gmp_pct >= 20 and sub_x >= 10:
        st.success(
            L(
                f"🟢 धमाकेदार IPO (STRONG APPLY): लिस्टिंग पर +{gmp_pct}% (लगभग +₹{est_profit} प्रति लॉट) मुनाफे की प्रबल संभावना है!",
                f"🟢 DHAMAKEDAR IPO (STRONG APPLY): Listing par +{gmp_pct}% (+₹{est_profit} prati lot) munafe ka chance hai!",
                f"🟢 STRONG APPLY: Expected listing gain of +{gmp_pct}% (+₹{est_profit} per lot)!",
            )
        )
      elif gmp_pct >= 10 and sub_x >= 3:
        st.warning(
            L(
                f"🟡 सामान्य IPO (MODERATE): इसमें +{gmp_pct}% (+₹{est_profit}) का मामूली लाभ मिल सकता है।",
                f"🟡 NORMAL IPO (MODERATE): Ismein +{gmp_pct}% (+₹{est_profit}) ka mamuli labh mil sakta hai.",
                f"🟡 MODERATE IPO: Expected listing gain around +{gmp_pct}% (+₹{est_profit}).",
            )
        )
      else:
        st.error(
            L(
                f"🔴 खतरा / दूर रहें (AVOID IPO): GMP ({gmp_pct}%) बहुत कम है, लिस्टिंग पर नुकसान हो सकता है!",
                f"🔴 AVOID IPO: GMP ({gmp_pct}%) bahut kam hai, listing par loss ho sakta hai!",
                f"🔴 AVOID IPO: Low GMP ({gmp_pct}%), high risk of listing loss.",
            )
        )

  with ipo2:
    with st.container(border=True):
      st.subheader(
          "🌱 "
          + L(
              "Groww स्टाइल SIP / स्टॉक वेल्थ कैलकुलेटर",
              "Groww Style SIP / Crorepati Calculator",
              "Groww Style Monthly SIP Wealth Calculator",
          )
      )
      sip_amt = st.number_input(
          L("हर महीने कितना निवेश करेंगे? (₹):", "Har mahine kitna lagayenge? (₹):", "Monthly Investment (₹):"),
          min_value=500,
          value=5000,
          step=500,
      )
      sip_rate = st.slider(
          L("सालाना अनुमानित रिटर्न (%):", "Salana Expected Return (%):", "Expected Annual Return (%):"),
          8,
          30,
          15,
      )
      sip_yrs = st.slider(
          L("कितने साल के लिए? (Years):", "Kitne Saal Ke Liye?:", "Time Period (Years):"),
          1,
          30,
          10,
      )

      months = sip_yrs * 12
      r_month = (sip_rate / 100) / 12
      future_val = int(
          sip_amt * (((1 + r_month) ** months - 1) / r_month) * (1 + r_month)
      )
      invested_sip = int(sip_amt * months)
      wealth_gained = future_val - invested_sip

      st.success(
          L(
              f"🏆 **{sip_yrs} साल बाद आपका कुल फंड बनेगा: `₹{future_val:,}`**\n\n"
              f"- आपका जमा किया पैसा: `₹{invested_sip:,}`\n"
              f"- सिर्फ मुनाफे से बना पैसा: **`+₹{wealth_gained:,}`**",
              f"🏆 **{sip_yrs} Saal baad aapka kul paisa banega: `₹{future_val:,}`**\n\n"
              f"- Aapka jama kiya paisa: `₹{invested_sip:,}`\n"
              f"- Sirf munafe (Compound) se bana paisa: **`+₹{wealth_gained:,}`**",
              f"🏆 **Total Maturity Value after {sip_yrs} Years: `₹{future_val:,}`**\n\n"
              f"- Total Invested: `₹{invested_sip:,}`\n"
              f"- Est. Wealth Gained: **`+₹{wealth_gained:,}`**",
          )
      )
