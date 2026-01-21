import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS: NÜKLEER ++ RENK VE DÜZEN DÜZELTME ---
css_kodu = """
<style>
    /* 1. Ana Arkaplan ve Yazılar */
    .stApp { background-color: #F2F2F7 !important; }
    h1, h2, h3, h4, h5, p, span, div, label, .stMarkdown { color: #1C1C1E !important; }
    
    /* 2. Beyaz Kartlar (Dış Çerçeveler) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        border-radius: 16px; /* Biraz daha keskin köşeler */
        padding: 16px;       /* İç boşluğu azalttık */
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* 3. Butonlar */
    div.stButton > button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* --- KRİTİK: DROPDOWN MENÜ (AÇILIR LİSTE) --- */
    /* Kapalı haldeki kutunun içi */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #e5e5e5 !important;
    }
    /* Açılan listenin çerçevesi (Popover) */
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
    /* Listenin içindeki her bir seçenek (Seçilmemiş) */
    ul[data-baseweb="menu"] li {
        background-color: #ffffff !important;
        color: #000000 !important; /* Yazıyı zorla siyah yap */
    }
    /* Seçeneğin üzerine gelince (Hover) */
    ul[data-baseweb="menu"] li:hover {
        background-color: #F2F2F7 !important;
        color: #000000 !important;
    }
    /* Seçilmiş olan seçenek */
    li[aria-selected="true"] {
        background-color: #E5F1FF !important;
        color: #007AFF !important; /* Seçili olan mavi olsun */
    }
    
    /* Sayı Kutusu */
    .stNumberInput input { color: #000000 !important; background-color: #ffffff !important; }
    .stNumberInput div[data-baseweb="input"] { background-color: #ffffff !important; }

    /* Gereksiz boşlukları gizle */
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
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
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🧬 Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important; margin-top: 5px;'>Yapay Zeka Destekli Varyant Analizi</p>", unsafe_allow_html=True)

st.write("") # Başlıkla kutular arasına az mesafe

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
    
    # st.divider() # <-- BOŞ KUTU YAPAN BU SATIRI SİLDİK
    st.write("") # Sadece küçük bir boşluk bırakalım
    
    # SONUÇ GÖSTERİMİ (Marginler sıfırlandı)
    if known_disease:
        html = f"""
        <div style='background-color: #ffe5e5; padding: 12px; border-radius: 12px; border-left: 6px solid #ff3b30; margin: 0;'>
            <h3 style='color: #ff3b30 !important; margin:0; font-size: 1.1rem;'>⚠️ PATOJENİK (Kayıtlı)</h3>
            <p style='color: #333 !important; margin-top: 5px; margin-bottom: 0;'>Bu varyant ClinVar veritabanında tanımlıdır.</p>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        st.write("")
        st.info(f"**İlişkili Hastalık:** {known_disease}")
        
    else:
        if is_pathogenic:
            risk = prob[1] * 100
            html = f"""
            <div style='background-color: #fff3cd; padding: 12px; border-radius: 12px; border-left: 6px solid #ffc107; margin: 0;'>
                <h3 style='color: #d39e00 !important; margin:0; font-size: 1.1rem;'>⚠️ YÜKSEK RİSK (Tahmin)</h3>
                <p style='color: #333 !important; margin-top: 5px; margin-bottom: 0;'>
                    Yapay zeka <strong>%{risk:.1f}</strong> ihtimalle patojenik buldu.
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
        else:
            safe = prob[0] * 100
            html = f"""
            <div style='background-color: #d4edda; padding: 12px; border-radius: 12px; border-left: 6px solid #28a745; margin: 0;'>
                <h3 style='color: #155724 !important; margin:0; font-size: 1.1rem;'>✅ BENIGN (İyi Huylu)</h3>
                <p style='color: #333 !important; margin-top: 5px; margin-bottom: 0;'>
                    Yapay zeka <strong>%{safe:.1f}</strong> ihtimalle zararsız olduğunu düşünüyor.
                </p>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
