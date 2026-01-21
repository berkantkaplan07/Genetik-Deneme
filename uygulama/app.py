import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- IOS STİLİ VE RENK DÜZELTME (GÜNCELLENDİ) ---
st.markdown("""
    <style>
    /* 1. Ana Arkaplanı Açık Gri Yap (Karanlık modu ez) */
    .stApp {
        background-color: #F2F2F7 !important;
    }
    
    /* 2. Tüm Yazıları Siyah Yap (Görünmezliği engelle) */
    h1, h2, h3, h4, h5, p, span, div, label {
        color: #1C1C1E !important;
    }
    
    /* 3. Kart Görünümü (Beyaz Kutular) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 4. Butonlar (Mavi) */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* 5. Giriş Kutularının İçi (Dropdown vb.) */
    .stSelectbox div[data-baseweb="select"] > div, 
    .stNumberInput div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e5e5e5 !important;
    }
    /* Dropdown açılınca çıkan menü */
    ul[data-baseweb="menu"] {
        background-color: white !important;
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
    st.error("Model yüklenemedi. Lütfen dosyanın GitHub'da olduğundan emin olun.")
    st.stop()

# --- ARAYÜZ ---
st.markdown("<h1 style='text-align: center;'>Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>Genetik varyant analizi ve sendrom eşleştirme sistemi</p>", unsafe_allow_html=True)

# Kart: Veri Girişi
st.markdown("### 🧬 Varyant Bilgileri")

# Kromozom ve Mutasyon Tipi
col1, col2 = st.columns(2)
with col1:
    chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])
with col2:
    v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))

# Pozisyon
pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=43044295)

st.write("") 
analyze = st.button("Analiz Et")

# --- SONUÇ MANTIĞI ---
if analyze:
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]
    
    lookup_key = (c_enc, pos)
    known_disease = variant_db.get(lookup_key, None)
    
    input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
    prob = model.predict_proba(input_data)[0]
    is_pathogenic = prob[1] > 0.5
    
    st.divider()
    
    if known_disease:
        st.markdown(f"""
        <div style='background-color: #ffe5e5; padding: 15px; border-radius: 15px; border-left: 5px solid #ff3b30;'>
            <h3 style='color: #ff3b30 !important; margin:0;'>⚠️ PATOJENİK (Kayıtlı)</h3>
            <p style='color: #333 !important;'>Bu varyant ClinVar veritabanında mevcuttur.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"**İlişkili Hastalık:** {known_disease}")
    else:
        if is_pathogenic:
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 15px; border-radius: 15px; border-left: 5px solid #ffc107;'>
                <h3 style='color: #d39e00 !important; margin:0;'>⚠️ YÜKSEK RİSK (Tahmin)</h3>
                <p style='color: #333 !important;'>Literatürde yok ama yapay zeka <strong>%{prob[1]*100:.1f}</strong> ihtimalle patojenik buldu.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color: #d4edda; padding: 15px; border-radius: 15px; border-left: 5px solid #28a745;'>
                <h3 style='color: #155724 !important; margin:0;'>✅ BENIGN (İyi Huylu)</h3>
                <p style='color: #333 !important;'>Yapay zeka <strong>%{prob[0]*100:.1f}</strong> ihtimalle zararsız olduğunu düşünüyor.</p>
            </div>
            """, unsafe_allow_html=True)
