import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS: NÜKLEER RENK DÜZELTME ---
st.markdown("""
    <style>
    /* 1. Tüm Sayfa Arkaplanı */
    .stApp {
        background-color: #F2F2F7 !important;
    }
    
    /* 2. Tüm Ana Metinler */
    h1, h2, h3, h4, h5, p, span, div, label {
        color: #1C1C1E !important;
    }
    
    /* 3. Kartlar (Beyaz Kutular) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 4. Butonlar */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* --- DROPDOWN (AÇILIR MENÜ) DÜZELTME --- */
    
    /* Menü Kutusunun İçi (Kapalıyken) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Açılan Liste Penceresi (Popover) */
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
    }
    
    /* Listenin İçindeki Tüm Yazılar ve Arkaplanlar */
    div[data-baseweb="popover"] div, 
    div[data-baseweb="popover"] span,
    div[data-baseweb="popover"] li,
    ul[data-baseweb="menu"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Seçeneklerin üzerine gelince (Hover) hafif gri olsun */
    ul[data-baseweb="menu"] li:hover,
    ul[data-baseweb="menu"] li:focus {
        background-color: #F2F2F7 !important;
    }
    
    /* Seçili olan öğe */
    li[aria-selected="true"] {
        background-color: #E5F1FF !important;
        color: #007AFF !important;
    }

    /* Sayı Kutusu (Number Input) */
    .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .stNumberInput div[data-baseweb="input"] {
        background-color: #ffffff !important;
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
    st.error("⚠️ Model dosyası bulunamadı. GitHub'a 'genetik_ios_model.pkl' dosyasını yüklediğinden emin ol.")
    st.stop()

# --- ARAYÜZ ---
st.markdown("<h1 style='text-align: center;'>🧬 Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>Yapay Zeka Destekli Varyant Analizi</p>", unsafe_allow_html=True)

# Kart: Veri Girişi
st.markdown("### Varyant Bilgileri")

# Kromozom ve Mutasyon Tipi
col1, col2 = st.columns(2)
with col1:
    chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])
with col2:
    v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))

# Pozisyon
pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=5227002)

st.write("") 
analyze = st.button("Analiz Et", type="primary")

# --- SONUÇ MANTIĞI ---
if analyze:
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]
    
    lookup_key = (c_enc, pos)
    known_disease = variant_db.get(lookup_key, None)
    
    # Hastalık adını biraz temizleyelim (Clean Text)
    if known_disease:
        known_disease = known_disease.replace("|", ", ").replace("not provided", "").strip()
        if known_disease.endswith(","): known_disease = known_disease[:-1]
    
    input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
    prob = model.predict_proba(input_data)[0]
    is_pathogenic = prob[1] > 0.5
    
    st.divider()
    
    if known_disease:
        st.markdown(f"""
        <div style='background-color: #ffe5e5; padding: 15px; border-radius: 15px; border-left: 6px solid #ff3b30; margin-bottom: 10px;'>
            <h3 style='color: #ff3b30 !important; margin:0;'>⚠️ PATOJENİK (Kayıtlı)</h3>
            <p style='color: #333 !important; margin-top: 5px;'>Bu varyant ClinVar veritabanında tanımlıdır.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info(f"**İlişkili Hastalık / Sendrom:**\n\n{known_disease}")
        
    else:
        if is_pathogenic:
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 15px; border-radius: 15px; border-left: 6px solid #ffc107;'>
                <h3 style='color: #d39e00 !important; margin:0;'>⚠️ YÜKSEK RİSK (Tahmin)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>Literatürde yok ama yapay zeka <strong>%{prob[1]*100:.1f}</strong> ihtimalle patojenik buldu.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color: #d4edda; padding: 15px; border-radius: 15px; border-left: 6px solid #28a745;'>
                <h3 style='color: #155724 !important; margin:0;'>✅ BENIGN (İyi Huylu)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>Yapay zeka <strong>%{prob[0]*10
