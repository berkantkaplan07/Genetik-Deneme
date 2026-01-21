import streamlit as st
import joblib
import pandas as pd

# --------------------------------------------------------
# 1. AYARLAR
# --------------------------------------------------------
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --------------------------------------------------------
# 2. TASARIM (CSS) - SENİN İSTEDİĞİN RENK KOMBİNASYONU
# --------------------------------------------------------
css_tasarim = """
<style>
    /* GENEL ARKAPLAN */
    .stApp { background-color: #F2F2F7 !important; }
    h1, h2, h3, h4, h5, p, span, div, label { color: #1C1C1E !important; }

    /* BEYAZ KARTLAR */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* --- 1. KAPALI KUTU (SARI OK) -> BEYAZ OLSUN --- */
    /* Kutunun kendisi */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;  /* BEYAZ ZEMİN */
        color: #000000 !important;             /* SİYAH YAZI */
        border: 1px solid #d1d1d6 !important;
        border-radius: 8px !important;
    }
    
    /* İçindeki yazı */
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* Sağdaki ok simgesi */
    .stSelectbox svg {
        fill: #000000 !important;
    }

    /* --- 2. AÇILAN LİSTE (KIRMIZI OK) -> MAVİ OLSUN --- */
    
    /* Listenin Dış Çerçevesi (Popover) - Zorla Mavi Yap */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div {
        background-color: #007AFF !important;
        border: none !important;
    }

    /* Listenin İçindeki Tüm Satırlar */
    ul[data-baseweb="menu"] {
        background-color: #007AFF !important;
    }
    
    ul[data-baseweb="menu"] li {
        background-color: #007AFF !important; /* Mavi Zemin */
        color: white !important;              /* BEYAZ YAZI */
    }
    
    /* Satırların içindeki yazı span'ları da beyaz olsun */
    ul[data-baseweb="menu"] li span {
        color: white !important;
    }
    
    /* Üzerine gelince (Hover) veya Seçilince */
    ul[data-baseweb="menu"] li:hover,
    ul[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #0056b3 !important; /* Koyu Mavi */
        color: white !important;
    }

    /* --- SAYI GİRİŞ KUTUSU --- */
    .stNumberInput div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d1d6 !important;
        border-radius: 8px !important;
    }
    .stNumberInput input {
        color: #000000 !important;
    }
    
    /* --- ANALİZ BUTONU --- */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
    }
</style>
"""
st.markdown(css_tasarim, unsafe_allow_html=True)


# --------------------------------------------------------
# 3. MODELİ YÜKLE
# --------------------------------------------------------
@st.cache_resource
def load_data():
    return joblib.load('genetik_ios_model.pkl')

try:
    data = load_data()
    model = data['model']
    type_mapping = data['type_mapping']
    variant_db = data['variant_db']
except:
    st.error("⚠️ Model dosyası yüklenemedi.")
    st.stop()


# --------------------------------------------------------
# 4. ARAYÜZ
# --------------------------------------------------------
st.markdown("<h1 style='text-align: center;'>🧬 Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>Yapay Zeka Destekli Varyant Analizi</p>", unsafe_allow_html=True)
st.write("") 

# Giriş Kartı
st.markdown("### Varyant Bilgileri")
col1, col2 = st.columns(2)

with col1:
    chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])

with col2:
    v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))

pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=5227002)

st.write("") 
analyze = st.button("ANALİZ ET 🚀", type="primary")


# --------------------------------------------------------
# 5. SONUÇ MANTIĞI
# --------------------------------------------------------
if analyze:
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]
    lookup_key = (c_enc, pos)
    known_disease = variant_db.get(lookup_key, None)
    
    if known_disease:
        known_disease = known_disease.replace("|", ", ").replace("not provided", "").strip()
        if known_disease.endswith(","): known_disease = known_disease[:-1]
    
    input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
    prob = model.predict_proba(input_data)[0]
    is_pathogenic = prob[1] > 0.5
    
    st.write("") 
    
    if known_disease:
        st.markdown(f"""
        <div style='background-color: #ffe5e5; padding: 15px; border-radius: 10px; border-left: 6px solid #ff3b30;'>
            <h3 style='color: #ff3b30 !important; margin:0;'>⚠️ PATOJENİK (Kayıtlı)</h3>
            <p style='color: #333 !important; margin-top: 5px;'>Bu varyant ClinVar veritabanında mevcuttur.</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"**İlişkili Hastalık:** {known_disease}")
        
    else:
        if is_pathogenic:
            risk = prob[1] * 100
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 6px solid #ffc107;'>
                <h3 style='color: #d39e00 !important; margin:0;'>⚠️ YÜKSEK RİSK (Tahmin)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>Yapay zeka <strong>%{risk:.1f}</strong> ihtimalle patojenik buldu.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            safe = prob[0] * 100
            st.markdown(f"""
            <div style='background-color: #d4edda; padding: 15px; border-radius: 10px; border-left: 6px solid #28a745;'>
                <h3 style='color: #155724 !important; margin:0;'>✅ BENIGN (İyi Huylu)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>Yapay zeka <strong>%{safe:.1f}</strong> ihtimalle zararsız olduğunu düşünüyor.</p>
            </div>
            """, unsafe_allow_html=True)
