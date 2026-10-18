import urllib.parse
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Pro AI Stock Radar", layout="wide")
st.title("🎯 All-in-One Smart Trading & Crisis Radar")
st.caption(
    "शॉर्ट-फॉर्म सिग्नल: 2 सेकंड में जानें कौन सा स्टॉक ऊपर जाएगा, कौन सा"
    " गिरेगा, और किसमें खतरा है"
)

# 1. प्रमुख स्टॉक्स की लिस्ट
STOCKS = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "State Bank (SBI)": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "Larsen & Toubro": "LT.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Tata Steel": "TATASTEEL.NS",
    "NTPC": "NTPC.NS",
    "Axis Bank": "AXISBANK.NS",
    "Coal India": "COALINDIA.NS",
}

# 2. सेक्टर इंडेक्स लिस्ट
SECTORS = {
    "🏦 Banking": "^NSEBANK",
    "💻 IT": "^CNXIT",
    "🚗 Auto": "^CNXAUTO",
    "💊 Pharma": "^CNXPHARMA",
    "🛒 FMCG": "^CNXFMCG",
    "🏗️ Metal": "^CNXMETAL",
}


# --- ग्लोबल और मार्केट क्रैश मीटर फंक्शन ---
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
    return None, 0, None, 0


# --- सेक्टर रोटेशन फंक्शन ---
@st.cache_data(ttl=300)
def get_sector_performance():
  sec_data = {}
  for name, ticker in SECTORS.items():
    try:
      df = yf.Ticker(ticker).history(period="5d")
      if len(df) >= 2:
        chg = round(
            ((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2])
            * 100,
            2,
        )
        sec_data[name] = chg
    except Exception:
      pass
  return sec_data


# --- मुख्य स्टॉक एनालाइजर इंजन ---
@st.cache_data(ttl=300)
def analyze_stock(name, ticker):
  try:
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")
    if df.empty or len(df) < 30:
      return None

    curr = round(df["Close"].iloc[-1], 2)
    prev = round(df["Close"].iloc[-2], 2)
    day_chg = round(((curr - prev) / prev) * 100, 2)

    # Moving Averages & 6-Month Drawdown (लॉस चेक)
    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    high_6m = df["High"].max()
    low_6m = df["Low"].min()
    drop_from_high = round(((curr - high_6m) / high_6m) * 100, 1)

    # RSI (14 दिनों की ताकत: 30 से नीचे = बहुत गिरा हुआ, 60 से ऊपर = मज़बूत रफ़्तार)
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = round(100 - (100 / (1 + rs.iloc[-1])), 1)

    # Volume Surge
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    curr_vol = df["Volume"].iloc[-1]
    vol_ratio = round(curr_vol / avg_vol, 1) if avg_vol > 0 else 1.0

    # ATR (आज/कल कितना रिटर्न या गिरावट संभव है)
    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
    up_target = round(curr + (atr * 1.3), 2)
    stop_loss = round(curr - (atr * 0.8), 2)
    down_target = round(curr - (atr * 1.3), 2)
    potential_gain_pct = round(((up_target - curr) / curr) * 100, 1)

    # Live Google News Crisis & Profit Scanner
    query = urllib.parse.quote(f"{name} stock India")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:2]]
    top_news = headlines[0] if headlines else "कोई बड़ी ताज़ा खबर नहीं"

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

    # Master Score (0 to 100)
    score = 20
    if curr > ma20:
      score += 20
    if curr > ma50:
      score += 20
    if vol_ratio >= 1.2:
      score += 15
    if 55 <= rsi <= 75:
      score += 15
    if news_score > 0:
      score += 10
    elif news_score < 0:
      score -= 25
    score = max(0, min(100, score))

    # Category & Short Explanation
    if news_score < 0 or (curr < ma20 and day_chg < -1.0):
      category = "BEARISH"
      badge = "🔴 नीचे गिरने का खतरा (AVOID / SELL)"
      summary = (
          f"चार्ट कमज़ोर है या नेगेटिव खबर का दबाव है। यह ₹{down_target} तक"
          " फिसल सकता है।"
      )
    elif score >= 70 and day_chg >= 0:
      category = "BULLISH"
      badge = "🟢 आज/कल ऊपर जाने के मज़बूत संकेत (STRONG BUY)"
      summary = (
          f"ट्रेंड ऊपर है, RSI ({rsi}) मज़बूत है और {vol_ratio}x वॉल्यूम है।"
          f" संभावित रिटर्न: +{potential_gain_pct}%।"
      )
    elif drop_from_high <= -15 or rsi < 38:
      category = "OVERSOLD"
      if curr > ma20:
        badge = "💎 लगातार लॉस के बाद अब रिकवरी शुरू (REVERSAL)"
        summary = (
            f"हाई से {abs(drop_from_high)}% गिरा था, लेकिन अब 20-MA के ऊपर"
            " निकल रहा है (फ्यूचर के लिए अच्छा मौका)।"
        )
      else:
        badge = "📉 बहुत दिनों से लगातार लॉस में (WEAK / WAIT)"
        summary = (
            f"अपने हाई से {abs(drop_from_high)}% नीचे है और अभी भी गिरावट"
            " रुकी नहीं है। सस्ते के चक्कर में अभी न खरीदें।"
        )
    else:
      category = "NEUTRAL"
      badge = "🟡 सामान्य / साइडवेज़ (WAIT)"
      summary = "अभी न बड़ी तेज़ी है और न बड़ा खतरा। ब्रेकआउट का इंतज़ार करें।"

    return {
        "name": name,
        "ticker": ticker,
        "price": curr,
        "day_chg": day_chg,
        "score": score,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "drop_from_high": drop_from_high,
        "up_target": up_target,
        "stop_loss": stop_loss,
        "potential_gain_pct": potential_gain_pct,
        "news_score": news_score,
        "top_news": top_news,
        "category": category,
        "badge": badge,
        "summary": summary,
    }
  except Exception:
    return None


# --- कार्ड दिखाने का शॉर्ट-फॉर्म डिज़ाइन ---
def render_card(d):
  with st.container(border=True):
    c_top1, c_top2 = st.columns([3, 1])
    c_top1.subheader(f"{d['name']} — ₹{d['price']} ({d['day_chg']}%)")
    c_top2.metric("मास्टर स्कोर", f"{d['score']}/100")

    st.markdown(f"**फैसला:** {d['badge']}")
    st.info(f"💡 **शॉर्ट समरी:** {d['summary']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 टारगेट (ऊपर)", f"₹{d['up_target']}", f"+{d['potential_gain_pct']}%")
    m2.metric("🛡️ सुरक्षा स्टॉप-लॉस", f"₹{d['stop_loss']}")
    m3.metric("📊 खरीदारी वॉल्यूम", f"{d['vol_ratio']}x गुना")
    m4.metric("📉 हाई से दूरी", f"{d['drop_from_high']}%")

    news_icon = (
        "🟢 पॉजिटिव खबर"
        if d["news_score"] > 0
        else ("🔴 नेगेटिव खबर" if d["news_score"] < 0 else "⚪ सामान्य खबर")
    )
    st.caption(f"**{news_icon}:** {d['top_news']} | **RSI ताकत:** `{d['rsi']}`")


# ================= टॉप बार: मार्केट मूड और सेक्टर रडार =================
nifty_val, nifty_chg, vix_val, vix_chg = get_market_mood()
if nifty_val:
  st.subheader("🌍 1. लाइव बाज़ार मूड और क्रैश प्रोटेक्शन मीटर")
  mc1, mc2, mc3 = st.columns(3)
  mc1.metric("🇮🇳 Nifty 50", f"{nifty_val}", f"{nifty_chg}%")
  mc2.metric(
      "⚡ India VIX (डर का मीटर)",
      f"{vix_val}",
      f"{vix_chg}%",
      delta_color="inverse",
  )
  if vix_chg > 6 or nifty_chg < -1.0:
    mc3.error(
        "🚨 **सावधान (Crash Alert):** आज बाज़ार में डर (VIX) बढ़ा हुआ है या"
        " भारी बिकवाली है। नई खरीदारी में सावधानी बरतें!"
    )
  elif nifty_chg > 0.4 and vix_chg <= 0:
    mc3.success(
        "✅ **Safe Market:** आज बाज़ार का मूड सकारात्मक है और डर कम हो रहा है।"
    )
  else:
    mc3.warning(
        "⚖️ **Normal Market:** बाज़ार सामान्य दायरे में है, सिर्फ मज़बूत"
        " स्टॉक्स ही चुनें।"
    )

st.subheader("🧭 2. आज पैसा किस सेक्टर में जा रहा है? (Sector Radar)")
sec_perf = get_sector_performance()
if sec_perf:
  scols = st.columns(len(sec_perf))
  for i, (sname, schg) in enumerate(sec_perf.items()):
    scols[i].metric(sname, f"{schg}%", delta=f"{schg}%")

st.divider()

# ================= मुख्य टैब्स: 4 आसान बॉक्स =================
tab1, tab2, tab3, tab4 = st.tabs([
    "🟢 आज/कल ऊपर जाने वाले (Top Buy)",
    "🔴 आज गिरने वाले / खतरा (Avoid/Sell)",
    "📉 बहुत दिनों से लॉस में (Oversold & Future)",
    "🔍 कोई भी स्टॉक सर्च करें",
])

with st.spinner("सभी स्टॉक्स, चार्ट्स और लाइव न्यूज़ का विश्लेषण हो रहा है..."):
  all_results = []
  for name, ticker in STOCKS.items():
    res = analyze_stock(name, ticker)
    if res:
      all_results.append(res)

with tab1:
  st.markdown(
      "### 🚀 मज़बूत रफ़्तार और पॉजिटिव संकेत वाले स्टॉक्स (High-Probability)"
  )
  bulls = [
      r for r in all_results if r["category"] == "BULLISH" or r["score"] >= 65
  ]
  bulls = sorted(bulls, key=lambda x: x["score"], reverse=True)
  if not bulls:
    st.write("अभी कोई स्टॉक कड़े बाय-फ़िल्टर को पार नहीं कर रहा है।")
  else:
    cols = st.columns(2)
    for idx, item in enumerate(bulls):
      with cols[idx % 2]:
        render_card(item)

with tab2:
  st.markdown("### ⚠️ कमज़ोर चार्ट या नेगेटिव खबर वाले स्टॉक्स (इनसे दूर रहें)")
  bears = [
      r for r in all_results if r["category"] == "BEARISH" or r["score"] <= 40
  ]
  bears = sorted(bears, key=lambda x: x["score"])
  if not bears:
    st.write("अभी लिस्ट के किसी स्टॉक में बड़ा खतरा नहीं दिख रहा है।")
  else:
    cols = st.columns(2)
    for idx, item in enumerate(bears):
      with cols[idx % 2]:
        render_card(item)

with tab3:
  st.markdown(
      "### 📉 अपने हाई से काफी गिरे हुए स्टॉक्स (पता करें कौन सा उठेगा और"
      " कौन सा अभी और गिरेगा)"
  )
  oversold = [
      r
      for r in all_results
      if r["category"] == "OVERSOLD" or r["drop_from_high"] <= -12
  ]
  oversold = sorted(oversold, key=lambda x: x["drop_from_high"])
  if not oversold:
    st.write("अभी कोई स्टॉक भारी गिरावट (Oversold) ज़ोन में नहीं है।")
  else:
    cols = st.columns(2)
    for idx, item in enumerate(oversold):
      with cols[idx % 2]:
        render_card(item)

with tab4:
  st.markdown("### 🔎 किसी भी भारतीय शेयर (NSE) का नाम लिखकर तुरंत कुंडली निकालें")
  col_s1, col_s2 = st.columns([2, 1])
  custom_symbol = col_s1.text_input(
      "NSE स्टॉक सिंबल लिखें (जैसे: ZOMATO, IRFC, SUZLON, TATAPOWER, PNB):",
      "TATAPOWER",
  )
  custom_name = col_s2.text_input("कंपनी का नाम (न्यूज़ खोजने के लिए):", "Tata Power")
  if st.button("अभी चेक करें"):
    clean_sym = custom_symbol.strip().upper()
    if not clean_sym.endswith(".NS"):
      clean_sym += ".NS"
    custom_data = analyze_stock(custom_name, clean_sym)
    if custom_data:
      render_card(custom_data)
    else:
      st.error("स्टॉक का डेटा नहीं मिला। कृपया सही NSE सिंबल लिखें (जैसे SBIN, ITC)।")