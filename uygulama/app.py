import streamlit as st
import joblib
import pandas as pd

# Sayfa ayarı
st.set_page_config(page_title="Genetik Asistanı", page_icon="🧬", layout="centered")

# --- CSS KODUNU AYRI BİR DEĞİŞKENE ALIYORUZ (HATA RİSKİNİ AZALTMAK İÇİN) ---
css_kodu = """
<style>
    /* 1. Tüm Sayfa Arkaplanı */
    .stApp {
        background-color: #F2F2F7 !important;
    }
    
    /* 2. Tüm Ana Metinler SİYAH */
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
    
    /* --- MENÜ VE GİRİŞ KUTULARI DÜZELTME --- */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
    }
    
    div[data-baseweb="popover"] div, 
    div[data-baseweb="popover"] span,
    div[data-baseweb="popover"] li,
    ul[data-baseweb="menu"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    ul[data-baseweb="menu"] li:hover {
        background-color: #F2F2F7 !important;
    }
    
    .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    .stNumberInput div[data-baseweb="input"] {
        background-color: #ffffff !important;
    }
</style>
"""

# CSS'i Uygula
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
    st.error("⚠️ Model dosyası bulunamadı. GitHub'a 'genetik_ios_model.pkl' dosyasını yüklediğinden emin ol.")
    st.stop()

# --- ARAYÜZ ---
st.markdown("<h1 style='text-align: center;'>🧬 Tıbbi Genetik Asistanı</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666 !important;'>Yapay Zeka Destekli Varyant Analizi</p
