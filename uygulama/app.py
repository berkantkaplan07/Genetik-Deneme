
import streamlit as st
import joblib
import pandas as pd

st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- IOS STİLİ İÇİN CSS (SİHİRLİ DOKUNUŞ) ---
st.markdown("""
    <style>
    /* Genel Arkaplan ve Font */
    .stApp {
        background-color: #F2F2F7; /* iOS Gri Arkaplan */
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Kart Görünümü (Beyaz kutular) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Başlıklar */
    h1 {
        color: #1C1C1E;
        font-weight: 700;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Butonlar (iOS Mavi) */
    div.stButton > button {
        background-color: #007AFF;
        color: white;
        border-radius: 14px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
        transform: scale(1.02);
    }

    /* Giriş Kutuları */
    .stSelectbox, .stNumberInput {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- MODELİ YÜKLE ---
@st.cache_resource
def load_data():
    return joblib.load('genetik_ios_model.pkl')

try:
    data = load_data()
    model = data['model']
    type_mapping = data['type_mapping']
    variant_db = data['variant_db']
except:
    st.error("Sistem yükleniyor, lütfen bekleyin...")
    st.stop()

# --- ARAYÜZ ---
st.title("Tıbbi Genetik Asistanı")
st.caption("Genetik varyant analizi ve sendrom eşleştirme sistemi")

# Kart 1: Veri Girişi
st.markdown("### 🧬 Varyant Bilgileri")
col1, col2 = st.columns(2)
with col1:
    chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])
    pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=43044295)

with col2:
    v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))
    st.write("") # Hizalama boşluğu
    st.write("")

analyze = st.button("Analiz Et")

# --- SONUÇ MANTIĞI ---
if analyze:
    # 1. Encoding
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]

    # 2. Önce Veritabanına Bak (BİLİNEN VARYANT MI?)
    # Tuple olarak anahtar oluşturuyoruz
    lookup_key = (c_enc, pos)
    known_disease = variant_db.get(lookup_key, None)

    # 3. Yapay Zeka Tahmini
    input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
    prob = model.predict_proba(input_data)[0]
    is_pathogenic = prob[1] > 0.5

    st.markdown("---")

    # SENARYO A: LİTERATÜRDE VARSA
    if known_disease:
        st.error("🚨 LİTERATÜRDE EŞLEŞME BULUNDU")
        st.markdown(f"""
        <div style='background-color: #ffe5e5; padding: 15px; border-radius: 15px; border-left: 5px solid #ff3b30;'>
            <h3 style='color: #ff3b30; margin:0;'>PATOJENİK VARYANT</h3>
            <p>Bu varyant ClinVar veritabanında kayıtlıdır.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🏥 İlişkili Hastalık / Sendrom:")
        st.info(known_disease)

        st.metric(label="Yapay Zeka Doğrulama Skoru", value=f"%{prob[1]*100:.1f}")

    # SENARYO B: LİTERATÜRDE YOKSA (AI TAHMİNİ)
    else:
        st.markdown("#### 🤖 Yapay Zeka Tahmini (Novel Varyant)")
        if is_pathogenic:
            st.warning("⚠️ YÜKSEK RİSK TESPİT EDİLDİ")
            st.write(f"Bu pozisyonda bilinen bir kayıt yok, ancak yapay zeka varyant özelliklerine göre **%{prob[1]*100:.1f}** ihtimalle Patojenik olduğunu düşünüyor.")
            st.markdown("*Olası Etkiler:* Protein fonksiyon kaybı veya yapısal bozukluk.")
        else:
            st.success("✅ İYİ HUYLU (BENIGN) GÖRÜNÜYOR")
            st.write(f"Yapay zeka bu varyantın **%{prob[0]*100:.1f}** ihtimalle zararsız olduğunu öngörüyor.")

