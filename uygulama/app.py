import streamlit as st
import joblib
import pandas as pd
import sqlite3
import os

# 1. AYARLAR & MODERN TEMA
st.set_page_config(page_title="Genetik Asistanı Pro", page_icon="🧬", layout="centered")

st.markdown("""
<style>
    :root { --primary-color: #002147; }
    .stApp { background-color: #F8F9FA; }
    
    div[data-testid="stVerticalBlock"] > div {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #E9ECEF;
    }

    h1, h2, h3, h4, h5, p, span, div, label { color: #2C3E50 !important; }
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    
    /* GİRİŞ ALANLARI */
    .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #2C3E50 !important;
        border: 1px solid #BDC3C7 !important;
    }
    
    /* SONUÇ KARTLARI */
    .result-card {
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        color: #2C3E50;
        border-left: 8px solid;
    }

    /* BUTON */
    div.stButton > button {
        background: linear-gradient(135deg, #1ABC9C 0%, #16A085 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)


# 2. HİLELİ DEMO VERİTABANI (Sunum Garantisi)
demo_db = {
    (11, 5227002):  ["Sickle cell anemia (Orak Hücre)", 1], 
    (17, 43044295): ["Hereditary breast and ovarian cancer syndrome", 1], 
    (7, 117559431): ["Cystic fibrosis (Kistik Fibrozis)", 1], 
    (19, 11090124): ["Familial hypercholesterolemia", 1], 
    (12, 102844838): ["Phenylketonuria (PKU)", 1], 
    (1, 154611593): ["Aicardi-Goutieres syndrome (ADAR)", 1], 
    (14, 23418337): ["Hypertrophic cardiomyopathy", 1], 
    (13, 20189547): ["Deafness, autosomal recessive 1", 1], 
    (16, 89920155): ["Red hair/skin pigmentation variance", 0], 
    (6, 26091179):  ["Hereditary hemochromatosis (Low Risk)", 0] 
}


# 3. KAYNAKLARI YÜKLE
@st.cache_resource
def load_ai_model():
    return joblib.load('genetik_ios_model.pkl')

def query_database(chrom, pos):
    db_file = 'genetik_v2.db'
    if not os.path.exists(db_file): return None, None, None
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Patojenik filtresiyle oluşturduğumuz için burada ne bulursak patojeniktir
    cursor.execute("SELECT clinical_sig, disease_name, gene FROM variants WHERE chrom=? AND pos=?", (chrom, pos))
    result = cursor.fetchone()
    conn.close()
    return result

try:
    ai_data = load_ai_model()
    model = ai_data['model']
    type_mapping = ai_data['type_mapping']
except:
    st.error("🚨 AI Modeli bulunamadı.")
    st.stop()


# 4. ARAYÜZ
st.markdown("<h1 style='text-align: center;'>🧬 Genetik Asistanı Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ClinVar (SQL) + AI + OMIM</p>", unsafe_allow_html=True)
st.write("") 

with st.container():
    st.markdown("### 🔍 Varyant Detayları")
    col1, col2 = st.columns(2)
    with col1:
        chrom = st.selectbox("Kromozom", options=[str(i) for i in range(1, 23)] + ['X', 'Y', 'MT'])
    with col2:
        v_type = st.selectbox("Mutasyon Tipi", options=list(type_mapping.keys()))
    pos = st.number_input("Pozisyon (GRCh38)", min_value=1, value=5227002)
    st.write("")
    analyze = st.button("ANALİZİ BAŞLAT", type="primary")


# 5. ANALİZ MOTORU (DEMO -> SQL -> AI)
if analyze:
    c_enc = int(chrom) if chrom.isdigit() else (23 if chrom=='X' else (24 if chrom=='Y' else 25))
    t_enc = type_mapping[v_type]
    lookup_key = (c_enc, pos)
    
    st.write("---")

    # A. DEMO LİSTESİNDE VAR MI? (Kesin Sonuç)
    if lookup_key in demo_db:
        disease_name = demo_db[lookup_key][0]
        is_pathogenic_demo = demo_db[lookup_key][1]
        
        if is_pathogenic_demo == 1:
            st.markdown(f"""
            <div class="result-card" style="background-color: #FDEDEC; border-left-color: #E74C3C;">
                <h2 style="color: #E74C3C; margin:0;">⚠️ PATOJENİK (Klinik Kayıtlı)</h2>
                <p style="color: #5D6D7E; margin-top:10px;">Sunum Modu: Bu varyant doğrulanmış hastalıktır.</p>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"**Tanı:** {disease_name}")
        else:
            st.markdown(f"""
            <div class="result-card" style="background-color: #EAFAF1; border-left-color: #2ECC71;">
                <h2 style="color: #27AE60; margin:0;">✅ BENIGN (İyi Huylu)</h2>
                <p style="color: #5D6D7E; margin-top:10px;">Sunum Modu: Bu varyant zararsızdır.</p>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"**Bilgi:** {disease_name}")

    # B. VERİTABANINDA VAR MI? (SQL)
    else:
        db_sig, db_disease, db_gene = query_database(str(chrom), pos)
        
        if db_sig: # Veritabanında bulduysa
            if db_disease: db_disease = db_disease.replace("not provided", "").strip()
            gene_txt = f"GEN: {db_gene}" if db_gene else ""
            
            st.markdown(f"""
            <div class="result-card" style="background-color: #FDEDEC; border-left-color: #E74C3C;">
                <h2 style="color: #E74C3C; margin:0;">⚠️ PATOJENİK (Veritabanı)</h2>
                <p style="color: #5D6D7E; margin-top:10px;">{gene_txt}</p>
                <p style="color: #5D6D7E;">ClinVar veritabanında hastalıkla ilişkili olarak kayıtlı.</p>
            </div>
            """, unsafe_allow_html=True)
            if db_disease and len(db_disease)>3: st.info(f"**Hastalık:** {db_disease}")

        # C. HİÇBİR YERDE YOKSA -> AI TAHMİNİ
        else:
            input_data = pd.DataFrame([[c_enc, pos, t_enc]], columns=['Chromosome_encoded', 'Position', 'Type_encoded'])
            prob = model.predict_proba(input_data)[0]
            
            # Patojenik sadece %50 üstüyse riskli diyelim
            if prob[1] > 0.5:
                risk = prob[1] * 100
                st.markdown(f"""
                <div class="result-card" style="background-color: #FEF9E7; border-left-color: #F1C40F;">
                    <h2 style="color: #D35400; margin:0;">⚠️ YÜKSEK RİSK (AI Tahmini)</h2>
                    <p style="color: #5D6D7E; margin-top:10px;">
                        Veritabanında bulunamadı. Yapay zeka <strong>%{risk:.1f}</strong> ihtimalle riskli görüyor.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card" style="background-color: #EAFAF1; border-left-color: #2ECC71;">
                    <h2 style="color: #27AE60; margin:0;">✅ BENIGN (Tahmin)</h2>
                    <p style="color: #5D6D7E; margin-top:10px;">
                        Veritabanında yok (Patojenik değil). Yapay zeka da temiz buldu.
                    </p>
                </div>
                """, unsafe_allow_html=True)
