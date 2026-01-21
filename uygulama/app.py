import streamlit as st
import joblib
import pandas as pd

# --------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI (MODERN AYARLAR)
# --------------------------------------------------------
st.set_page_config(
    page_title="Genetik Asistanı Pro",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------
# 2. MODERN CSS TASARIMI (TURKUAZ & ARDUVAZ)
# --------------------------------------------------------
# Not: Input kutularının içine müdahale etmiyoruz, böylece 
# Karanlık/Aydınlık modda yazıların kaybolma riski SIFIRLANIYOR.
st.markdown("""
<style>
    /* GENEL SAYFA ARKAPLANI (Hafif Gri - Göz Yormaz) */
    .stApp {
        background-color: #F8F9FA;
    }

    /* MODERN KARTLAR (Veri Giriş Alanları) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); /* Yumuşak gölge */
        border: 1px solid #E9ECEF;
    }

    /* BAŞLIKLAR (Arduvaz Grisi - Modern ve Okunaklı) */
    h1 {
        color: #2C3E50 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    h3 {
        color: #34495E !important;
        font-weight: 600;
        border-bottom: 2px solid #1ABC9C; /* Altına Turkuaz Çizgi */
        padding-bottom: 10px;
        display: inline-block;
    }
    p {
        color: #7F8C8D !important;
        font-size: 1.1rem;
    }

    /* ÖZEL BUTON TASARIMI (Gradient Turkuaz) */
    div.stButton > button {
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0 5px 15px rgba(26, 188, 156, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(26, 188, 156, 0.6) !important;
    }

    /* SONUÇ KUTULARI İÇİN ÖZEL STİL */
    .result-card {
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        color: #2C3E50;
        border-left: 8px solid;
    }

    /* GİRİŞ KUTULARI ETİKETLERİ */
    label {
        color: #2C3E50 !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------
# 3. MODEL YÜKLEME (GÜVENLİ MOD)
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
    st.error("🚨 Sistem Hatası: Model dosyası ('genetik_ios_model.pkl') bulunamadı.")
    st.stop()


# --------------------------------------------------------
# 4. ARAYÜZ (UI)
# --------------------------------------------------------

# Başlık Bölümü
st.markdown("<h1 style='text-align: center;'>🧬 Genetik Asistanı Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Yapay Zeka Destekli Varyant & Sendrom Analizi</p>", unsafe_allow_html=True)
st.write("") # Boşluk

# Ana Kart (Konteyner)
with st.container():
    st.markdown("### 🔍 Varyant Detayları")
    st.write("")
    
    # Grid Sistemi (2 Kolon)
    col1, col2 = st.columns(2)
    
    with col1:
        chrom = st.selectbox(
            "Kromozom", 
            options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'],
            help="Varyantın bulunduğu kromozomu seçin."
        )
    
    with col2:
        v_type = st.selectbox(
            "Mutasyon Tipi", 
            options=list(type_mapping.keys()),
            help="Mutasyonun moleküler tipini seçin."
        )
    
    # Pozisyon Kutusu (Tam Genişlik)
    pos = st.number_input(
        "Pozisyon (GRCh38)", 
        min_value=1, 
        value=5227002,
        help="Genom üzerindeki tam koordinat."
    )
    
    st.write("")
    analyze = st.button("ANALİZİ BAŞLAT", type="primary")


# --------------------------------------------------------
# 5. ANALİZ MOTORU
# --------------------------------------------------------
if analyze:
    # Veri Hazırlığı
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]
    lookup_key = (c_enc, pos)
    
    # 1. Veritabanı Kontrolü
    known_disease = variant_db.get(lookup_key, None)
    
    # 2. AI Tahmini
    input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
    prob = model.predict_proba(input_data)[0]
    is_pathogenic = prob[1] > 0.5
    
    # Metin Temizliği
    if known_disease:
        known_disease = known_disease.replace("|", ", ").replace("not provided", "").strip()
        if known_disease.endswith(","): known_disease = known_disease[:-1]

    st.write("---") # Ayırıcı Çizgi

    # SONUÇ GÖSTERİMİ (MODERN KARTLARLA)
    
    if known_disease:
        # SENARYO 1: BİLİNEN HASTALIK (KIRMIZI/MERCAN KART)
        st.markdown(f"""
        <div class="result-card" style="background-color: #FDEDEC; border-left-color: #E74C3C;">
            <h2 style="color: #E74C3C; margin:0; display:flex; align-items:center;">
                ⚠️ PATOJENİK (Klinik Kayıtlı)
            </h2>
            <p style="color: #5D6D7E; margin-top:10px;">
                Bu varyant ClinVar veritabanında tanımlanmıştır ve hastalıkla ilişkilidir.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Hastalık İsmi Kutusu
        st.info(f"**Tanımlı Sendrom / Hastalık:**\n\n{known_disease}")

    else:
        # SENARYO 2: AI TAHMİNİ
        if is_pathogenic:
            risk_score = prob[1] * 100
            st.markdown(f"""
            <div class="result-card" style="background-color: #FEF9E7; border-left-color: #F1C40F;">
                <h2 style="color: #D35400; margin:0;">
                    ⚠️ YÜKSEK RİSK (AI Tahmini)
                </h2>
                <p style="color: #5D6D7E; margin-top:10px;">
                    Literatürde kayıt bulunamadı ancak yapay zeka <strong>%{risk_score:.1f}</strong> ihtimalle patojenik olduğunu öngörüyor.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            safe_score = prob[0] * 100
            st.markdown(f"""
            <div class="result-card" style="background-color: #EAFAF1; border-left-color: #2ECC71;">
                <h2 style="color: #27AE60; margin:0;">
                    ✅ BENIGN (İyi Huylu)
                </h2>
                <p style="color: #5D6D7E; margin-top:10px;">
                    Yapay zeka bu varyantın <strong>%{safe_score:.1f}</strong> ihtimalle zararsız olduğunu düşünüyor.
                </p>
            </div>
            """, unsafe_allow_html=True)
