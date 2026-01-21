import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS: MAVİ TASARIM (BLUE THEME) ---
css_kodu = """
<style>
    /* 1. Arkaplan */
    .stApp { background-color: #F2F2F7 !important; }
    h1, h2, h3, h4, h5, p, span, div, label, .stMarkdown { color: #1C1C1E !important; }
    
    /* 2. Beyaz Kartlar */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 3. Butonlar */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }
    
    /* --- MENÜ KUTULARI (MAVİ OLSUN) --- */
    
    /* Seçim Kutusunun Kendisi (Kapalıyken) - SENİN İSTEDİĞİN MAVİ YER */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #007AFF !important; /* Arkaplan MAVİ */
        color: white !important;              /* Yazı BEYAZ */
        border: none !important;
        border-radius: 10px !important;
    }
    
    /* Kutusunun içindeki yazı (Seçilen öğe) */
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
    }
    
    /* Sağdaki Ok İşareti (Onu da beyaz yapalım ki görünsün) */
    .stSelectbox svg {
        fill: white !important;
    }
    
    /* --- AÇILAN LİSTE (POPOVER) --- */
    div[data-baseweb="popover"] {
        background-color: white !important;
        border: 1px solid #eee !important;
    }
    
    /* Listenin içindeki seçenekler */
    ul[data-baseweb="menu"] li {
        background-color: white !important;
        color: black !important; /* Liste içi siyah olsun okunsun */
    }
    
    /* Seçeneğin üzerine gelince */
    ul[data-baseweb="menu"] li:hover {
        background-color: #E5F1FF !important; /* Açık mavi */
        color: #007AFF !important;
    }
    
    /* --- SAYI KUTUSU (POZİSYON) --- */
    /* Onu da hafif mavi yapalım uyumlu dursun */
    .stNumberInput div[data-baseweb="input"] {
        background-color: #E5F1FF !important;
        border-radius: 10px !important;
        border: 1px solid #007AFF !important;
    }
    .stNumberInput input {
        color: #007AFF !important; /* Yazısı mavi olsun */
    }
    
    /* Sonuç Kutusu Ayarı */
    .sonuc-kutusu {
        padding: 15px !important;
        margin-top: 10px !important;
        border-radius: 12px !important;
        border-left-width: 6px !important;
        border-left-style: solid !important;
    }
</style>
"""
st.markdown(css_kodu, unsafe_allow_html=True)

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
    st.error("⚠️ Model dosyası bulunamadı. GitHub'a dosya yüklediğinden emin ol.")
    st.stop()

# --- ARAYÜZ ---
st.markdown("<h1 style='text-align: center; margin-bottom: 5px;'>🧬 Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>Yapay Zeka Destekli Varyant Analizi</p>", unsafe_allow_html=True)

st.write("") 

st.markdown("### Varyant Bilgileri")

col1, col2 = st.columns(2)
with col1:
    chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])
with col2:
    v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))

pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=5227002)

st.write("") 
analyze = st.button("Analiz Et", type="primary")

# --- SONUÇ MANTIĞI ---
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
        html = f"""
        <div class="sonuc-kutusu" style='background-color: #ffe5e5; border-left-color: #ff3b30;'>
            <h3 style='color: #ff3b30 !important; margin:0; font-size: 1.1rem;'>⚠️ PATOJENİK (Kayıtlı)</h3>
            <p style='color: #333 !important; margin-top: 5px;'>Bu varyant ClinVar veritabanında tanımlıdır.</p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        st.info(f"**İlişkili Hastalık:** {known_disease}")
        
    else:
        if is_pathogenic:
            risk = prob[1] * 100
            html = f"""
            <div class="sonuc-kutusu" style='background-color: #fff3cd; border-left-color: #ffc107;'>
                <h3 style='color: #d39e00 !important; margin:0; font-size: 1.1rem;'>⚠️ YÜKSEK RİSK (Tahmin)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>
                    Yapay zeka <strong>%{risk:.1f}</strong> ihtimalle patojenik buldu.
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        else:
            safe = prob[0] * 100
            html = f"""
            <div class="sonuc-kutusu" style='background-color: #d4edda; border-left-color: #28a745;'>
                <h3 style='color: #155724 !important; margin:0; font-size: 1.1rem;'>✅ BENIGN (İyi Huylu)</h3>
                <p style='color: #333 !important; margin-top: 5px;'>
                    Yapay zeka <strong>%{safe:.1f}</strong> ihtimalle zararsız olduğunu düşünüyor.
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
