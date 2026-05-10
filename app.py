import streamlit as st
from openai import OpenAI
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PharmAI — Eczacılık Asistanı",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — Warm Academic (Lora + JetBrains Mono) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:           #f7f4ef;
  --surface:      #ffffff;
  --surface2:     #f0ece4;
  --border:       #ddd8ce;
  --accent:       #1a7a4a;
  --accent2:      #2563eb;
  --accent3:      #dc2626;
  --accent-light: #e8f5ee;
  --text:         #2d2a24;
  --text-dim:     #8a8070;
  --text-bright:  #1a1712;
  --mono:         'JetBrains Mono', monospace;
  --sans:         'DM Sans', sans-serif;
  --serif:        'Lora', serif;
  --radius:       12px;
}

/* ── Global ── */
html, body, [class*="css"] {
  font-family: var(--sans) !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}
.main .block-container {
  background: var(--bg);
  padding: 1.5rem 2rem 3rem;
  max-width: 900px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Header ── */
.pharmai-header {
  display: flex; align-items: center; gap: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 20px;
  margin-bottom: 1rem;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.pharmai-logo {
  width: 40px; height: 40px;
  background: var(--accent);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--serif);
  font-size: 14px; font-weight: 600;
  color: white; flex-shrink: 0;
}
.pharmai-title {
  font-family: var(--serif);
  font-size: 1.3rem;
  color: var(--text-bright);
  margin: 0 0 2px;
}
.pharmai-sub {
  font-family: var(--mono);
  font-size: .7rem;
  color: var(--text-dim);
  margin: 0;
}

/* ── Mode pills ── */
.mode-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 1rem; }
.mode-pill {
  font-family: var(--mono); font-size: .72rem;
  padding: 5px 11px; border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--surface); color: var(--text-dim);
  cursor: pointer; display: inline-block;
}
.mode-pill.active {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent); font-weight: 600;
}

/* ── Chat messages ── */
.chat-wrap { display: flex; flex-direction: column; gap: 16px; margin-bottom: 1rem; }
.msg-row { display: flex; gap: 10px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.av {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: .72rem; flex-shrink: 0; margin-top: 2px;
}
.av.ai   { background: var(--accent-light); color: var(--accent);  border: 1px solid rgba(26,122,74,.2); }
.av.user { background: #eff6ff;             color: var(--accent2); border: 1px solid rgba(37,99,235,.2); }

.bubble {
  max-width: 78%; padding: 11px 15px; border-radius: var(--radius);
  font-size: .9rem; line-height: 1.7;
}
.bubble.ai {
  background: var(--surface); border: 1px solid var(--border);
  border-top-left-radius: 2px; color: var(--text);
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.bubble.user {
  background: #eff6ff; border: 1px solid rgba(37,99,235,.15);
  border-top-right-radius: 2px; color: var(--text-bright);
}
.bubble strong { color: var(--accent); }
.bubble code {
  font-family: var(--mono); font-size: .8em;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 4px; padding: .1rem .3rem;
}
.msg-time { font-family: var(--mono); font-size: .65rem; color: var(--text-dim); margin-top: 4px; }
.msg-row.user .msg-time { text-align: right; }

/* ── Quick grid (welcome) ── */
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; max-width: 560px; margin: 0 auto; }
.welcome-box { text-align: center; padding: 28px 16px; }
.welcome-box h2 { font-family: var(--serif); font-size: 1.6rem; color: var(--text-bright); margin-bottom: 6px; }
.welcome-box h2 em { color: var(--accent); font-style: italic; }
.welcome-box p { font-size: .85rem; color: var(--text-dim); margin-bottom: 20px; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text-bright) !important;
  font-family: var(--sans) !important;
  font-size: .9rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(26,122,74,.12) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--accent) !important;
  color: white !important; border: none !important;
  border-radius: 9px !important;
  font-family: var(--sans) !important;
  font-weight: 500 !important;
  transition: background .18s !important;
}
.stButton > button:hover { background: #155f39 !important; }

/* ── Selectbox / Radio ── */
[data-testid="stSelectbox"] * { color: var(--text) !important; font-size: .88rem !important; }
[data-testid="stRadio"] label { color: var(--text-dim) !important; font-size: .85rem !important; }

/* ── Sidebar metric card ── */
.s-metric {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 9px; padding: .6rem .9rem; margin-bottom: .5rem;
  display: flex; justify-content: space-between; align-items: center;
}
.s-metric-label { font-size: .73rem; color: var(--text-dim); }
.s-metric-value { font-family: var(--mono); font-size: .82rem; color: var(--accent); font-weight: 600; }

/* ── Disclaimer ── */
.disclaimer {
  font-family: var(--mono); font-size: .68rem; color: var(--text-dim);
  text-align: center; padding: .6rem 0;
  border-top: 1px solid var(--border); margin-top: .5rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── MODES & MODELS ────────────────────────────────────────────────────────────
MODES = {
    "🔬 Genel": (
        "Sen PharmAI'sin — eczacılık öğrencilerine yardımcı olan uzman bir yapay zeka asistanısın. "
        "PubMed, NIH, FDA, EMA, TİTCK, Medscape, WHO, Drugs.com gibi güvenilir kaynaklara dayalı bilgi sun. "
        "Yanıtlarını Türkçe ver. Bilimsel terimlerin İngilizce karşılıklarını parantez içinde ekle. "
        "Önemli bilgilerde kaynak adı belirt. Başlıklar ve listeler kullan."
    ),
    "💊 Farmakoloji": (
        "Sen bir farmakoloji uzmanısın. Etki mekanizması (MOA), ADME, farmakodinamik, reseptör "
        "etkileşimleri, ilaç etkileşimleri, yan etkiler, kontrendikasyonlar hakkında kanıta dayalı "
        "bilgi ver. Türkçe yanıtla, terimlerin İngilizcesini ekle."
    ),
    "⚗️ Farmasötik Kimya": (
        "Sen bir farmasötik kimya uzmanısın. Kimyasal yapı, SAR (yapı-aktivite ilişkisi), sentez "
        "yolları, stabilite, formülasyon prensipleri, fizikokimyasal özellikler hakkında detaylı bilgi "
        "ver. IUPAC isimlendirmesi ve fonksiyonel grupları açıkla. Türkçe yanıtla."
    ),
    "🏥 Klinik Eczacılık": (
        "Sen bir klinik eczacılık uzmanısın. İlaç seçimi, dozaj optimizasyonu, ilaç-ilaç etkileşimleri, "
        "hasta izlemi, eczacının klinik rolü konularında bilgi ver. Güncel klinik kılavuzlara (ESC, AHA, "
        "GOLD vb.) ve EMA/FDA/TİTCK onaylarına atıfta bulun. Türkçe yanıtla."
    ),
    "🧬 Biyokimya": (
        "Sen bir biyokimya ve farmakogenetik uzmanısın. Enzim kinetiği, metabolik yolaklar, CYP "
        "polimorfizmleri, farmakogenetik, biyotransformasyon ve moleküler hedefler konularında bilgi "
        "ver. Türkçe yanıtla."
    ),
    "🎯 Sınav Modu": (
        "Sen bir eczacılık sınav koçusun. Her yanıtında bir çoktan seçmeli soru (A-D seçenekleri) sor, "
        "ardından doğru cevabı ve detaylı açıklamayı ver. Yanlış seçeneklerin neden yanlış olduğunu da "
        "açıkla. TUS/Eczacılık lisans sınav formatında hazırla. Türkçe."
    ),
}

MODELS = {
    "openrouter/auto": "OpenRouter Auto — Otomatik en iyi model ⭐",
    "openai/gpt-oss-120b:free": "GPT OSS 120B — OpenAI açık kaynak",
    "nvidia/nemotron-3-super-120b-a12b:free": "NVIDIA Nemotron 120B",
    "google/gemma-4-31b-it:free": "Gemma 4 31B — Google",
    "qwen/qwen3-coder:free": "Qwen3 Coder",
    "deepseek/deepseek-r1:free": "DeepSeek R1 — Analitik",
    "google/gemini-pro-1.5": "Gemini 1.5 Pro (ücretli)",
}

QUICK_QUESTIONS = [
    ("💊", "Metforminin etki mekanizması ve farmakokinetik profili"),
    ("🦠", "Beta-laktam antibiyotiklerde direnç mekanizmaları"),
    ("⚗️", "CYP450 inhibisyonu ve ilaç etkileşim örnekleri"),
    ("❤️", "ACE inhibitörleri vs ARB farkları ve klinik kullanım"),
]

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "mode"      not in st.session_state: st.session_state.mode      = "🔬 Genel"
if "api_key"   not in st.session_state: st.session_state.api_key   = ""
if "model"     not in st.session_state: st.session_state.model     = "openrouter/auto"
if "pending"   not in st.session_state: st.session_state.pending   = None

# ── API CALL ──────────────────────────────────────────────────────────────────
def call_api(api_key: str, model: str, mode: str, history: list) -> str:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    messages = [{"role": "system", "content": MODES[mode]}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    try:
        resp = client.chat.completions.create(
            model=model, messages=messages,
            max_tokens=1500, temperature=0.4,
            extra_headers={
                "HTTP-Referer": "https://pharmai.app",
                "X-Title": "PharmAI"
            }
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ Hata: {str(e)}"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:.4rem 0 1rem;'>
      <div style='font-family:Lora,serif;font-size:1.1rem;color:#1a7a4a;font-weight:600;'>⚕️ PharmAI</div>
      <div style='font-family:JetBrains Mono,monospace;font-size:.68rem;color:#8a8070;margin-top:3px;'>
        Eczacılık Asistanı
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**API Anahtarı**")
    api_input = st.text_input(
        "OpenRouter API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-or-v1-...",
        label_visibility="collapsed",
    )
    if api_input:
        st.session_state.api_key = api_input

    st.markdown("**Model**")
    model_choice = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        format_func=lambda x: MODELS[x],
        index=list(MODELS.keys()).index(st.session_state.model),
        label_visibility="collapsed",
    )
    st.session_state.model = model_choice

    st.divider()

    st.markdown("**Mod Seç**")
    for mode_name in MODES:
        is_active = (st.session_state.mode == mode_name)
        label = f"{'✓ ' if is_active else ''}{mode_name}"
        if st.button(label, key=f"mode_{mode_name}", use_container_width=True):
            st.session_state.mode = mode_name
            st.rerun()

    st.divider()

    # Stats
    total = len(st.session_state.messages)
    user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f"""
    <div class='s-metric'>
      <span class='s-metric-label'>Toplam Mesaj</span>
      <span class='s-metric-value'>{total}</span>
    </div>
    <div class='s-metric'>
      <span class='s-metric-label'>Soru Sayısı</span>
      <span class='s-metric-value'>{user_count}</span>
    </div>
    <div class='s-metric'>
      <span class='s-metric-label'>Aktif Mod</span>
      <span class='s-metric-value'>{st.session_state.mode.split()[0]}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Geçmişi Temizle", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()

    st.markdown("""
    <div class='disclaimer'>⚕️ Eğitim amaçlıdır<br>Klinik karar için kullanmayın</div>
    """, unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
model_label = MODELS.get(st.session_state.model, st.session_state.model).split("—")[0].strip()
status = "🟢" if st.session_state.api_key else "⚫"

st.markdown(f"""
<div class='pharmai-header'>
  <div class='pharmai-logo'>Rx</div>
  <div>
    <div class='pharmai-title'>PharmAI</div>
    <div class='pharmai-sub'>OpenRouter · Eczacılık Asistanı</div>
  </div>
  <div style='margin-left:auto;display:flex;align-items:center;gap:10px;'>
    <span style='font-family:JetBrains Mono,monospace;font-size:.72rem;
         background:#e8f5ee;border:1px solid rgba(26,122,74,.3);
         color:#1a7a4a;border-radius:4px;padding:3px 8px;'>
      {model_label}
    </span>
    <span style='font-size:.8rem;'>{status}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── MODE PILLS ────────────────────────────────────────────────────────────────
pills_html = "<div class='mode-row'>"
for m in MODES:
    active_cls = "active" if m == st.session_state.mode else ""
    pills_html += f"<span class='mode-pill {active_cls}'>{m}</span>"
pills_html += "</div>"
st.markdown(pills_html, unsafe_allow_html=True)

# ── CHAT ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class='welcome-box'>
      <div style='font-size:2.4rem;margin-bottom:10px;'>⚕️</div>
      <h2>Merhaba, <em>Damla!</em></h2>
      <p>Farmakoloji, klinik eczacılık, farmasötik kimya ve daha fazlası için yardıma hazırım.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick question buttons
    cols = st.columns(2)
    for i, (icon, q) in enumerate(QUICK_QUESTIONS):
        with cols[i % 2]:
            if st.button(f"{icon} {q}", key=f"quick_{i}", use_container_width=True):
                st.session_state.pending = q
                st.rerun()
else:
    for msg in st.session_state.messages:
        role_cls = "user" if msg["role"] == "user" else "ai"
        av_label = "D" if msg["role"] == "user" else "Rx"
        content  = msg["content"].replace("\n", "<br>")
        t = msg.get("time", "")
        st.markdown(f"""
        <div class='msg-row {role_cls}'>
          <div class='av {role_cls}'>{av_label}</div>
          <div>
            <div class='bubble {role_cls}'>{content}</div>
            <div class='msg-time'>{t}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_inp, col_btn = st.columns([5, 1])
with col_inp:
    user_input = st.text_input(
        "Mesaj",
        placeholder=f"{st.session_state.mode} modunda soru sor...",
        label_visibility="collapsed",
        key="user_input_field",
    )
with col_btn:
    send = st.button("Gönder →", use_container_width=True, type="primary")

# ── SEND LOGIC ────────────────────────────────────────────────────────────────
def process_message(text: str):
    if not st.session_state.api_key:
        st.error("⚠️ Lütfen sol menüden OpenRouter API anahtarınızı girin.")
        return
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": text, "time": ts})
    if len(st.session_state.messages) > 24:
        st.session_state.messages = st.session_state.messages[-20:]
    with st.spinner("Yanıt hazırlanıyor..."):
        reply = call_api(
            st.session_state.api_key,
            st.session_state.model,
            st.session_state.mode,
            st.session_state.messages,
        )
    st.session_state.messages.append({
        "role": "assistant", "content": reply,
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()

if st.session_state.pending:
    text = st.session_state.pending
    st.session_state.pending = None
    process_message(text)
elif send and user_input.strip():
    process_message(user_input.strip())

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1.5rem 0 .5rem;
     font-family:JetBrains Mono,monospace;font-size:.68rem;color:#a09880;'>
  PharmAI · OpenRouter · Eczacılık Fakültesi Eğitim Platformu
</div>
""", unsafe_allow_html=True)
