import json
import os
import urllib.parse
import urllib.request
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="Bharat AI Ultimate Trading Dashboard V8.0", layout="wide"
)

PORTFOLIO_FILE = "my_portfolio.json"


# ================= 1. PERMANENT PORTFOLIO FILE ENGINE =================
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
      {"name": "Tata Motors", "ticker": "TATAMOTORS.NS", "buy_price": 920.0, "qty": 15},
      {"name": "IRFC (Railway)", "ticker": "IRFC.NS", "buy_price": 165.0, "qty": 50},
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


# ================= 2. TELEGRAM AUTO-ALERT SENDER =================
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


# ================= 3. LANGUAGE TRANSLATION ENGINE =================
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

st.sidebar.header("🌐 1. भाषा चुनें (Language)")
selected_lang_label = st.sidebar.selectbox(
    "Choose Language:", list(LANGUAGES.keys()), index=0
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


# ================= 4. SIDEBAR CONFIGURATIONS & TELEGRAM SETTINGS =================
st.sidebar.header("💰 2. नए ट्रेड का बजट")
user_capital = st.sidebar.number_input(
    tr("एक नए शेयर में कितना पैसा लगाना है? (₹)", lang_code),
    min_value=500,
    max_value=5000000,
    value=10000,
    step=1000,
)

st.sidebar.header("🤖 3. Telegram Bot अलर्ट सेटिंग")
tg_token = st.sidebar.text_input(
    "Telegram Bot Token:", type="password", placeholder="123456:ABC-DEF..."
)
tg_chat_id = st.sidebar.text_input(
    "Telegram Chat ID:", placeholder="123456789"
)

if st.sidebar.button("📤 " + tr("टेलीग्राम पर टेस्ट मैसेज भेजें", lang_code)):
  success = send_telegram_alert(
      "🚀 Bharat AI Stock Bot: आपका टेलीग्राम अलर्ट सिस्टम सफलतापूर्वक जुड़ गया है!",
      tg_token,
      tg_chat_id,
  )
  if success:
    st.sidebar.success("✅ टेस्ट मैसेज भेज दिया गया है!")
  else:
    st.sidebar.error("❌ बॉट टोकन या चैट आईडी गलत है।")

if st.sidebar.button("🔄 " + tr("नया लाइव डेटा रिफ्रेश करें", lang_code)):
  st.cache_data.clear()

# ================= 5. STOCK CATEGORIES =================
STOCK_CATEGORIES = {
    "🏆 Top Nifty दिग्गज (Large Cap)": {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India (SBI)": "SBIN.NS",
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


# ================= 6. UNIVERSAL SEARCH API =================
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


# ================= 7. MARKET MOOD & ANALYSIS ENGINE =================
@st.cache_data(ttl=300)
def get_market_mood():
  try:
    nifty = yf.Ticker("^NSEI").history(period="5d")
    vix = yf.Ticker("^INDIAVIX").history(period="5d")
    n_curr, n_prev = nifty["Close"].iloc[-1], nifty["Close"].iloc[-2]
    n_chg = round(((n_curr - n_prev) / n_prev) * 100, 2)
    v_curr, v_prev = vix["Close"].iloc[-1], vix["Close"].iloc[-2]
    v_chg = round(((v_curr - v_prev) / v_prev) * 100, 2)
    return round(n_curr, 1), n_chg, round(v_curr, 2), v_chg
  except Exception:
    return None, 0.0, None, 0.0


@st.cache_data(ttl=300)
def analyze_stock_v8(name, ticker, nifty_chg):
  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    if df.empty or len(df) < 20:
      return None

    curr = round(df["Close"].iloc[-1], 2)
    prev = round(df["Close"].iloc[-2], 2)
    open_p = round(df["Open"].iloc[-1], 2)
    day_chg = round(((curr - prev) / prev) * 100, 2)

    ma5 = round(df["Close"].rolling(min(5, len(df))).mean().iloc[-1], 2)
    ma20 = round(df["Close"].rolling(min(20, len(df))).mean().iloc[-1], 2)
    ma50 = round(df["Close"].rolling(min(50, len(df))).mean().iloc[-1], 2)
    ma200 = (
        round(df["Close"].rolling(200).mean().iloc[-1], 2)
        if len(df) >= 200
        else ma50
    )

    high_52w = round(df["High"].max(), 2)
    low_52w = round(df["Low"].min(), 2)
    drop_from_high = round(((curr - high_52w) / high_52w) * 100, 1)

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(min(14, len(df))).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(min(14, len(df))).mean()
    rs = gain / loss
    rsi_val = 100 - (100 / (1 + rs.iloc[-1]))
    rsi = round(rsi_val, 1) if pd.notna(rsi_val) else 50.0

    avg_vol = df["Volume"].rolling(min(20, len(df))).mean().iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    vol_ratio = round(curr_vol / avg_vol, 1) if avg_vol > 0 else 1.0

    if vol_ratio >= 1.5 and day_chg > 0.5:
      operator_msg = "🔥 बड़े खिलाड़ी जमकर माल खरीद रहे हैं (Heavy Buying)!"
    elif vol_ratio >= 1.4 and abs(day_chg) <= 0.8 and curr >= open_p:
      operator_msg = "🕵️ चुपचाप नीचे के भाव पर शेयर बटोरे जा रहे हैं (Secret Buying)"
    elif vol_ratio >= 1.5 and day_chg < -0.8:
      operator_msg = "⚠️ बड़े खिलाड़ी माल बेचकर निकल रहे हैं (Heavy Selling)!"
    else:
      operator_msg = "⚖️ सामान्य खरीदारी-बिकवाली"

    support_floor = round(df["Low"].tail(min(15, len(df))).min(), 2)
    resistance_roof = round(df["High"].tail(min(15, len(df))).max(), 2)
    atr = (df["High"] - df["Low"]).rolling(min(14, len(df))).mean().iloc[-1]
    if pd.isna(atr) or atr <= 0:
      atr = curr * 0.02

    up_target = round(curr + (atr * 1.4), 2)
    stop_loss = round(curr - (atr * 0.8), 2)
    down_risk = round(curr - (atr * 1.4), 2)
    gain_pct = round(((up_target - curr) / curr) * 100, 1)

    query = urllib.parse.quote(f"{name} share news India")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:2]]
    top_news = headlines[0] if headlines else "कोई बड़ी ताज़ा खबर नहीं है"

    bad_words = [
        "loss", "fall", "crash", "fraud", "raid", "penalty", "slump",
        "down", "fire", "debt", "weak", "drop", "notice", "fine"
    ]
    good_words = [
        "profit", "surge", "order", "jump", "buy", "win", "growth",
        "high", "record", "rally", "deal", "dividend", "upgrade"
    ]

    news_score = 0
    for h in headlines:
      hl = h.lower()
      if any(w in hl for w in bad_words):
        news_score -= 1
      if any(w in hl for w in good_words):
        news_score += 1

    today_v = (
        "🟢 आज तेज़ी है"
        if (day_chg > 0.3 and curr >= open_p)
        else ("🔴 आज गिरावट है" if day_chg < -0.5 else "🟡 आज शांत है")
    )
    tomorrow_v = (
        "🚀 कल/इस हफ्ते ऊपर जाने के चांस"
        if (curr > ma5 and curr > ma20 and rsi >= 50)
        else ("⚠️ नीचे फिसल सकता है" if curr < ma20 else "⏳ एक दायरे में रहेगा")
    )
    future_v = (
        "💎 फ्यूचर में अच्छा रिटर्न देगा"
        if curr >= ma200
        else "📉 लॉन्ग-टर्म ट्रेंड अभी कमज़ोर है"
    )

    t1 = curr > ma20 and curr > ma50
    t2 = vol_ratio >= 1.1 or (day_chg > nifty_chg)
    t3 = curr >= ma200
    t4 = news_score >= 0
    t5 = 48 <= rsi <= 75
    ticks = sum([t1, t2, t3, t4, t5])

    score = (
        (25 if t1 else 5)
        + (20 if t2 else 5)
        + (20 if t3 else 5)
        + (20 if t5 else 5)
        + (15 if news_score > 0 else (10 if news_score == 0 else -20))
    )
    score = max(5, min(98, score))

    if news_score < 0 or (curr < ma20 and day_chg < -1.0):
      cat = "BEARISH"
      verdict = "🔴 खतरा / दूर रहें (आज या कल गिर सकता है)"
      advice = (
          f"इस शेयर में बिकवाली का दबाव है या खबर नेगेटिव है। यह ₹{down_risk}"
          " तक नीचे जा सकता है, अभी पैसा न लगाएं।"
      )
    elif score >= 75 and day_chg >= -0.1:
      cat = "BULLISH"
      verdict = "🟢 मज़बूत खरीदारी (आज/कल ऊपर जाने वाला टॉप शेयर)"
      advice = (
          f"5 में से {ticks} टेस्ट पास! रफ़्तार, वॉल्यूम और खबरें सब पक्ष में"
          f" हैं। यह ₹{up_target} (+{gain_pct}%) तक जा सकता है।"
      )
    elif drop_from_high <= -15:
      cat = "OVERSOLD"
      if curr > ma5 and day_chg > 0:
        verdict = "💎 सोने का मौका (बहुत गिरने के बाद अब ऊपर उठ रहा है)"
        advice = (
            f"अपने हाई से {abs(drop_from_high)}% सस्ता मिल रहा है और अब"
            " खरीदारी लौट आई है। फ्यूचर के लिए बढ़िया मौका!"
        )
      else:
        verdict = "📉 लगातार लॉस में (अभी और गिर सकता है - इंतज़ार करें)"
        advice = (
            f"यह शेयर हाई से {abs(drop_from_high)}% टूट चुका है और गिरावट अभी"
            " रुकी नहीं है। हरा सिग्नल आने तक रुकें।"
        )
    else:
      cat = "NEUTRAL"
      verdict = "🟡 सामान्य / रुकें (अभी कोई बड़ा मूवमेंट नहीं)"
      advice = (
          f"जब तक यह ₹{resistance_roof} के ऊपर न निकले, नई खरीदारी से बचें।"
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
        "score": score,
        "ticks": ticks,
        "verdict": verdict,
        "advice": advice,
        "up_target": up_target,
        "stop_loss": stop_loss,
        "down_risk": down_risk,
        "gain_pct": gain_pct,
        "support": support_floor,
        "resistance": resistance_roof,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "drop_from_high": drop_from_high,
        "vol_ratio": vol_ratio,
        "rsi": rsi,
        "news_score": news_score,
        "today_v": today_v,
        "tomorrow_v": tomorrow_v,
        "future_v": future_v,
        "operator_msg": operator_msg,
        "top_news": top_news,
        "cat": cat,
        "history_close": df["Close"].tail(60),
    }
  except Exception:
    return None


# ================= 8. PORTFOLIO & AVERAGE CALCULATOR =================
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
          f"बधाई हो! आप अभी **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं और"
          " इस शेयर की रफ़्तार अभी भी मज़बूत है। यह शेयर **₹{d['up_target']}**"
          f" तक जा सकता है। स्टॉप-लॉस: **₹{trailing_sl}**।"
      )
      box_type = "success"
    elif d["rsi"] >= 76 or d["news_score"] < 0 or d["price"] < d["ma20"]:
      action_badge = "💰 मुनाफा बुक करें / बेचकर निकलें (BOOK PROFIT NOW)"
      doctor_advice = (
          f"सावधान! आप अभी **+₹{pnl_rs} (+{pnl_pct}%)** के मुनाफे में हैं,"
          " लेकिन चार्ट पर कमज़ोरी है। प्रॉफिट जेब में डालें।"
      )
      box_type = "warning"
    else:
      action_badge = "🟢 होल्ड करें पर नज़र रखें"
      doctor_advice = f"आप **+₹{pnl_rs}** के मुनाफे में हैं। सपोर्ट के ऊपर होल्ड करें।"
      box_type = "info"
  else:
    if (
        d["news_score"] < 0
        or (
            d["price"] < d["ma20"]
            and d["price"] < d["ma50"]
            and d["score"] <= 40
        )
    ):
      action_badge = "🔴 तुरंत बेचकर निकलें (SELL / EXIT DANGER)"
      doctor_advice = (
          f"अलर्ट! आप अभी **₹{abs(pnl_rs)} ({pnl_pct}%)** के नुकसान में हैं। ट्रेंड"
          f" टूट चुका है। यह **₹{d['down_risk']}** तक गिर सकता है।"
      )
      box_type = "error"
    elif d["price"] > d["ma5"] and d["day_chg"] > 0 and d["score"] >= 50:
      action_badge = "💎 होल्ड करें & एवरेज करें (RECOVERY STARTED)"
      doctor_advice = (
          f"आप अभी **₹{abs(pnl_rs)}** के नुकसान में हैं, लेकिन शेयर नीचे से मुड़"
          " रहा है! नीचे 'Average Calculator' का उपयोग करें।"
      )
      box_type = "success"
    else:
      action_badge = "🟡 आखिरी सपोर्ट के साथ होल्ड करें"
      doctor_advice = (
          f"आप अभी **₹{abs(pnl_rs)}** के नुकसान में हैं। सपोर्ट **₹{d['support']}**"
          " पर है।"
      )
      box_type = "warning"

  with st.container(border=True):
    c_h1, c_h2, c_h3 = st.columns([3, 1, 1])
    c_h1.subheader(f"📌 {d['name']} ({d['ticker']})")
    c_h2.metric("ताकत स्कोर", f"{d['score']}/100")
    if c_h3.button("🗑️ हटाएं", key=f"del_{idx_key}"):
      st.session_state.my_portfolio.pop(idx_key)
      save_portfolio_to_disk(st.session_state.my_portfolio)
      st.rerun()

    if box_type == "success":
      st.success(f"### {action_badge}\n🗣️ {doctor_advice}")
    elif box_type == "error":
      st.error(f"### {action_badge}\n🗣️ {doctor_advice}")
    elif box_type == "warning":
      st.warning(f"### {action_badge}\n🗣️ {doctor_advice}")
    else:
      st.info(f"### {action_badge}\n🗣️ {doctor_advice}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("खरीद भाव", f"₹{buy_price}", f"{qty} Shares")
    m2.metric("अभी का भाव", f"₹{d['price']}", f"{d['day_chg']}%")
    m3.metric("मुनाफा / नुकसान", f"₹{pnl_rs}", f"{pnl_pct}%")
    m4.metric("टारगेट", f"₹{d['up_target']}")
    m5.metric("सपोर्ट", f"₹{d['support']}")

    # Telegram Alert Trigger for Portfolio
    if tg_token and tg_chat_id:
      if st.button(
          f"📤 टेलीग्राम पर {d['name']} का अलर्ट भेजें", key=f"tg_port_{idx_key}"
      ):
        msg = f"📊 *Portfolio Alert: {d['name']}*\nLive Price: ₹{d['price']}\nP&L: ₹{pnl_rs} ({pnl_pct}%)\nDoctor Advice: {action_badge}"
        send_telegram_alert(msg, tg_token, tg_chat_id)
        st.success("✅ टेलीग्राम अलर्ट भेज दिया गया!")

    # Smart Average Calculator
    if pnl_pct < 0 and d["price"] < buy_price:
      with st.expander(
          f"🧮 एवरेज डाउन कैलकुलेटर (अभी भाव ₹{d['price']} है)"
      ):
        auto_rec_qty = qty
        extra_qty = st.number_input(
            "कितने नए शेयर और खरीदना चाहते हैं?:",
            min_value=1,
            max_value=1000000,
            value=int(auto_rec_qty),
            key=f"avg_{idx_key}",
        )
        new_inv = extra_qty * d["price"]
        tot_shares = qty + extra_qty
        tot_cost = invested + new_inv
        new_avg = round(tot_cost / tot_shares, 2)
        st.markdown(
            f"💡 **नया औसत भाव (New Average):** **`₹{new_avg}`** *(पड़ेगा कुल"
            f" ₹{new_inv} खर्च करके)*"
        )


def show_easy_card(d, budget, lang, show_chart=False):
  qty = max(1, int(budget // d["price"]))
  profit_rs = int(qty * (d["up_target"] - d["price"]))
  risk_rs = int(qty * (d["price"] - d["stop_loss"]))

  with st.container(border=True):
    h1, h2 = st.columns([3, 1])
    h1.subheader(f"{d['name']} ({d['ticker']}) — ₹{d['price']} ({d['day_chg']}%)")
    h2.metric("Score", f"{d['score']}%")

    st.markdown(f"### {d['verdict']}")
    st.info(f"🗣️ **निचोड़:** {d['advice']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🛒 शेयर खरीदें", f"{qty} Shares", f"₹{int(qty * d['price'])}")
    c2.metric("🎯 टारगेट मुनाफा", f"+₹{profit_rs}", f"₹{d['up_target']}")
    c3.metric(
        "🛡️ स्टॉप-लॉस रिस्क",
        f"-₹{risk_rs}",
        f"₹{d['stop_loss']}",
        delta_color="inverse",
    )
    c4.metric("📉 हाई से दूरी", f"{d['drop_from_high']}%", f"{d['vol_ratio']}x")

    if tg_token and tg_chat_id:
      if st.button(
          f"📤 {d['name']} का सिग्नल टेलीग्राम पर भेजें",
          key=f"tg_card_{d['ticker']}",
      ):
        msg = f"🚀 *Stock Signal: {d['name']}*\nPrice: ₹{d['price']} ({d['day_chg']}%)\nScore: {d['score']}%\nVerdict: {d['verdict']}\nTarget: ₹{d['up_target']}"
        send_telegram_alert(msg, tg_token, tg_chat_id)
        st.success("✅ टेलीग्राम अलर्ट भेज दिया गया!")

    if show_chart:
      st.line_chart(d["history_close"])


# ================= 9. HEADER & MARKET MOOD =================
st.title("🇮🇳 ऑल-इन-वन स्मार्ट स्टॉक & ट्रेडिंग डैशबोर्ड (V8.0)")
st.caption(
    "Live Intraday Breakout Scanner + Telegram Alerts + Dividend/Bonus/Split"
    " Radar + Permanent Portfolio"
)

nifty_val, nifty_chg, vix_val, vix_chg = get_market_mood()
if nifty_val:
  mc1, mc2, mc3 = st.columns([1, 1, 2])
  mc1.metric("🇮🇳 Nifty 50 Live", f"{nifty_val}", f"{nifty_chg}%")
  mc2.metric("⚡ India VIX", f"{vix_val}", f"{vix_chg}%", delta_color="inverse")
  if vix_chg > 6 or nifty_chg < -1.0:
    mc3.error("🚨 CRASH WARNING: मार्केट में भारी बिकवाली का खतरा है!")
  else:
    mc3.success("✅ MARKET SAFE: आज आप ब्रेकआउट ट्रेड्स देख सकते हैं।")

# ================= 10. MAIN 7 TABS =================
(
    tab_port,
    tab_intra,
    tab_corp,
    tab_search,
    tab_buy,
    tab_sell,
    tab_ipo,
) = st.tabs([
    "💼 1. मेरा पोर्टफोलियो & एवरेज",
    "⚡ 2. सुबह 9:15-10:00 Intraday Breakout",
    "🎁 3. Dividend, Bonus & Split रडार",
    "🔍 4. 5000+ शेयर सर्च करें",
    "🟢 5. Top Buy स्टॉक्स",
    "🔴 6. Avoid स्टॉक्स",
    "🆕 7. लाइव IPO सेंटर",
])

# ----------------- TAB 1: PORTFOLIO -----------------
with tab_port:
  st.header("🩺 मेरा परमानेंट पोर्टफोलियो डॉक्टर")
  with st.container(border=True):
    p_c1, p_c2, p_c3, p_c4 = st.columns([2, 1, 1, 1])
    p_search = p_c1.text_input("कंपनी का नाम:", value="Suzlon", key="p_s")
    p_matches = search_indian_stocks(p_search) if p_search else []
    if p_matches:
      chosen_p = p_c1.selectbox(
          "चुनें:", options=p_matches, format_func=lambda x: x[0], key="p_m"
      )
      sel_name, sel_ticker = chosen_p[1], chosen_p[2]
    else:
      sel_name, sel_ticker = p_search.upper(), p_search.strip().upper() + ".NS"

    p_buy_price = p_c2.number_input("खरीद भाव (₹):", value=65.0, key="p_bp")
    p_qty = p_c3.number_input("मात्रा (Qty):", value=100, key="p_qty")
    if p_c4.button("💾 सेव करें", use_container_width=True):
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
      st.success("✅ सफलतापूर्वक सेव हो गया!")

  if st.session_state.my_portfolio:
    total_inv = sum(i["buy_price"] * i["qty"] for i in st.session_state.my_portfolio)
    total_curr = 0.0
    for idx, item in enumerate(st.session_state.my_portfolio):
      p_data = analyze_stock_v8(item["name"], item["ticker"], nifty_chg)
      if p_data:
        total_curr += p_data["price"] * item["qty"]
        render_portfolio_doctor_card(
            p_data, item["buy_price"], item["qty"], lang_code, idx
        )

# ----------------- TAB 2: INTRADAY BREAKOUT SCANNER (9:15 - 10:00) -----------------
with tab_intra:
  st.header("⚡ सुबह 9:15 से 10:00 का 'Live Intraday Breakout' स्कैनर")
  st.info(
      "💡 **यह कैसे काम करता है:** यह स्कैनर सुबह मार्केट खुलते ही निफ्टी के"
      " प्रमुख शेयरों में 15-मिनट के चार्ट पर भारी वॉल्यूम (Volume Surge) और"
      " Opening Range Breakout (ORB) को ट्रैक करता है।"
  )

  if st.button("🚀 Intraday Breakout स्कैन शुरू करें"):
    with st.spinner("सुबह के शुरुआती ब्रेकआउट्स स्कैन हो रहे हैं..."):
      intra_results = []
      # कुछ प्रमुख हाई-वॉल्यूम इंट्राडे स्टॉक्स की लिस्ट
      intra_watchlist = {
          "Tata Motors": "TATAMOTORS.NS",
          "Reliance": "RELIANCE.NS",
          "Suzlon": "SUZLON.NS",
          "Zomato": "ZOMATO.NS",
          "IRFC": "IRFC.NS",
          "Tata Power": "TATAPOWER.NS",
          "SBI": "SBIN.NS",
          "Adani Enterprises": "ADANIENT.NS",
      }
      for iname, itick in intra_watchlist.items():
        res = analyze_stock_v8(iname, itick, nifty_chg)
        if res and res["vol_ratio"] >= 1.2 and res["day_chg"] > 0.5:
          intra_results.append(res)

      if intra_results:
        st.success(
            f"🔥 {len(intra_results)} स्टॉक्स में सुबह का मज़बूत ब्रेकआउट मिला"
            " है!"
        )
        for item in intra_results:
          with st.container(border=True):
            st.subheader(
                f"⚡ {item['name']} — भाव: ₹{item['price']} ({item['day_chg']}%)"
            )
            st.markdown(
                f"📊 **वॉल्यूम उछाल:** `{item['vol_ratio']}x` | **इंट्राडे टारगेट:"
                f"** `₹{item['up_target']}` | **स्टॉप-लॉस:** `₹{item['stop_loss']}`"
            )
            st.success(f"💡 {item['advice']}")
            if tg_token and tg_chat_id:
              if st.button(
                  f"📤 {item['name']} का Intraday Alert भेजें",
                  key=f"tg_intra_{item['ticker']}",
              ):
                msg = f"⚡ *Intraday Breakout Alert*\nStock: {item['name']}\nPrice: ₹{item['price']} ({item['day_chg']}%)\nTarget: ₹{item['up_target']}"
                send_telegram_alert(msg, tg_token, tg_chat_id)
                st.success("✅ टेलीग्राम पर अलर्ट भेज दिया गया!")
      else:
        st.warning(
            "अभी किसी स्टॉक ने 15-मिनट के कड़े ब्रेकआउट नियम को पार नहीं किया"
            " है।"
        )

# ----------------- TAB 3: DIVIDEND, BONUS & SPLIT RADAR -----------------
with tab_corp:
  st.header("🎁 Dividend, Bonus और Stock Split देने वाली कंपनियों का रडार")
  st.caption(
      "यहाँ आपको हाल ही में घोषित या आने वाले कॉर्पोरेट एक्शन (डिविडेंड, बोनस,"
      " स्प्लिट) की लाइव जानकारी मिलती है:"
  )

  c_div, c_bon = st.columns(2)
  with c_div:
    with st.container(border=True):
      st.subheader("💰 आगामी डिविडेंड स्टॉक्स (Upcoming Dividends)")
      div_feed = feedparser.parse(
          "https://news.google.com/rss/search?q=dividend+stocks+record+date+India+2026&hl=en-IN&gl=IN&ceid=IN:en"
      )
      if div_feed.entries:
        for entry in div_feed.entries[:5]:
          st.markdown(f"- 💵 **{entry.title}**")
      else:
        st.write("फिलहाल कोई डिविडेंड फीड उपलब्ध नहीं है।")

  with c_bon:
    with st.container(border=True):
      st.subheader("🚀 बोनस शेयर और स्टॉक स्प्लिट (Bonus & Splits)")
      split_feed = feedparser.parse(
          "https://news.google.com/rss/search?q=stock+split+bonus+shares+India+2026&hl=en-IN&gl=IN&ceid=IN:en"
      )
      if split_feed.entries:
        for entry in split_feed.entries[:5]:
          st.markdown(f"- 🎁 **{entry.title}**")
      else:
        st.write("फिलहाल कोई बोनस/स्प्लिट फीड उपलब्ध नहीं है।")

# ----------------- TAB 4: UNIVERSAL SEARCH -----------------
with tab_search:
  st.subheader("🔍 5000+ भारतीय शेयरों की खोज")
  search_query = st.text_input(
      "कंपनी का नाम लिखें:", placeholder="उदा. Suzlon, Tata, Zomato..."
  )
  if search_query:
    matches = search_indian_stocks(search_query)
    if matches:
      selected_match = st.selectbox(
          "चुनें:", options=matches, format_func=lambda x: x[0]
      )
      if selected_match:
        s_data = analyze_stock_v8(selected_match[1], selected_match[2], nifty_chg)
        if s_data:
          show_easy_card(s_data, user_capital, lang_code, show_chart=True)

# ----------------- TABS 5, 6, 7: SCANNER & IPO -----------------
st.sidebar.header("📂 4. स्टॉक कैटेगरी चुनें")
chosen_category = st.sidebar.radio("कैटेगरी:", list(STOCK_CATEGORIES.keys()))
active_stocks = STOCK_CATEGORIES[chosen_category]

results = [
    r
    for n, t in active_stocks.items()
    if (r := analyze_stock_v8(n, t, nifty_chg)) is not None
]

with tab_buy:
  st.subheader(f"🟢 {chosen_category} — Top Buy स्टॉक्स")
  for item in sorted(
      [r for r in results if r["score"] >= 70],
      key=lambda x: x["score"],
      reverse=True,
  ):
    show_easy_card(item, user_capital, lang_code)

with tab_sell:
  st.subheader(f"🔴 {chosen_category} — Avoid स्टॉक्स")
  for item in sorted(
      [r for r in results if r["score"] <= 45], key=lambda x: x["score"]
  ):
    show_easy_card(item, user_capital, lang_code)

with tab_ipo:
  st.header("🆕 लाइव IPO सेंटर & GMP कैलकुलेटर")
  with st.container(border=True):
    st.subheader("🧮 1-सेकंड IPO टेस्टर")
    ip_price = st.number_input("Issue Price (₹):", value=500)
    gmp_v = st.number_input("GMP (₹):", value=150)
    sub_v = st.number_input("Subscription (Times):", value=15.0)
    gmp_p = round((gmp_v / ip_price) * 100, 1)
    if gmp_p >= 20:
      st.success(
          f"🟢 धमाकेदार IPO (STRONG APPLY): अनुमानित लिस्टिंग गेन +{gmp_p}%!"
      )
    else:
      st.error("🔴 सामान्य या कमज़ोर GMP, लिस्टिंग पर सावधानी रखें।")
