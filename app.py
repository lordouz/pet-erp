import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.2", layout="wide")

# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar (Ton)": 100.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "MEG", "LOT No": "MEG-LOT-001", "Miktar (Ton)": 50.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Antimon", "LOT No": "ANT-LOT-001", "Miktar (Ton)": 5.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Fosforik Asit", "LOT No": "FOS-LOT-001", "Miktar (Ton)": 2.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Mavi Boya", "LOT No": "BOY-M-001", "Miktar (Ton)": 0.5},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Kırmızı Boya", "LOT No": "BOY-K-001", "Miktar (Ton)": 0.3},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "IPA", "LOT No": "IPA-LOT-001", "Miktar (Ton)": 1.5},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "DEG", "LOT No": "DEG-LOT-001", "Miktar (Ton)": 4.0}
    ]

# Reçeteleri boş başlatıyoruz, tamamen siz panelden oluşturacaksınız
if 'receteler' not in st.session_state:
    st.session_state.receteler = []

if 'uretim_emirleri' not in st.session_state:
    st.session_state.uretim_emirleri = []

# Mamul deposunu boş başlatıyoruz, ürettikçe listeniz kendiliğinden oluşacak
if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

# --- ANLIK STOK HESAPLAYICILAR ---
def toplam_hammadde_stok():
    df = pd.DataFrame(st.session_state.hammadde_depo)
    if df.empty: 
        return {h: 0.0 for h in ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"]}
    grup_toplamlari = df.groupby("Hammadde")["Miktar (Ton)"].sum().to_dict()
    return grup_toplamlari

def toplam_mamul_stok():
    df = pd.DataFrame(st.session_state.mamul_depo)
    if df.empty: return {}
    return df.groupby("Ürün")["Miktar (Ton)"].sum().to_dict()

# 3. YAN PANEL MENÜ SİSTEMİ (Satış Sayfası Çıkarıldı)
st.sidebar.title("🧪 PET Resin ERP v2.2")
st.sidebar.write("---")
sayfa = st.sidebar.radio("Gitmek İstediğiniz Sayfa:", [
    "📊 Genel Depo & Stok Durumu",
    "📥 1. Hammadde Giriş Sayfası",
    "📝 2. Reçete Oluşturma Sayfası",
    "🏭 3. Üretim Emri & Giriş Sayfası"
])

# ==========================================
# SAYFA: GENEL DEPO VE STOK DURUMU
# ==========================================
if sayfa == "📊 Genel Depo & Stok Durumu":
    st.header("📊 Fabrika Anlık Stok ve Depo Paneli")
    
    h_stok = toplam_hammadde_stok()
    m_stok = toplam_mamul_stok()
    
    st.subheader("💡 Kritik Hammadde Stok Özetleri")
    
    # 1. Satır Stok Özetleri
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PTA Stoku", f"{h_stok.get('PTA', 0.0):.2f} Ton")
    col2.metric("MEG Stoku", f"{h_stok.get('MEG', 0.0):.2f} Ton")
    col3.metric("Antimon Stoku", f"{h_stok.get('Antimon', 0.0):.2f} Ton")
    col4.metric("Fosforik Asit Stoku", f"{h_stok.get('Fosforik Asit', 0.0):.2f} Ton")
    
    # 2. Satır Stok Özetleri
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Mavi Boya", f"{h_stok.get('Mavi Boya', 0.0):.2f} Ton")
    col6.metric("Kırmızı Boya", f"{h_stok.get('Kırmızı Boya', 0.0):.2f} Ton")
    col7.metric("IPA Stoku", f"{h_stok.get('IPA', 0.0):.2f} Ton")
    col8.metric("DEG Stoku", f"{h_stok.get('DEG', 0.0):.2f} Ton")
    
    st.write("---")
    mamul_toplam = sum(m_stok.values()) if m_stok else 0.0
    st.metric("📦 Toplam Satışa Hazır Mamul (Ürün) Stoku", f"{mamul_toplam:.2f} Ton")
    
    t1, t2 = st.tabs(["📋 Detaylı Hammadde Lot Listesi", "📦 Detaylı Mamul Depo Listesi"])
    with t1:
        st.dataframe(pd.DataFrame(st.session_state.hammadde_depo), use_container_width=True)
    with t2:
        if st.session_state.mamul_depo:
            st.dataframe(pd.DataFrame(st.session_state.mamul_depo), use_container_width=True)
        else:
            st.info("Mamul deposu boş. Listenizi oluşturmak için lütfen önce üretim yapın.")

# ==========================================
# SAYFA: HAMMADDE GİRİŞİ
# ==========================================
elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Lot Numaralı Hammadde Girişi")
    
    with st.form("hammadde_form"):
        g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
        h_turu = st.selectbox("Hammadde Türü", ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"])
        h_lot = st.text_input("Hammadde LOT Numarası (Örn: LOT-ANT-2026)")
        h_miktar = st.number_input("Gelen Miktar (Ton)", min_value=0.001, step=0.5, format="%.3f")
        
        submit = st.form_submit_button("Hammaddeyi Depoya Kabul Et")
        if submit:
            if h_lot == "":
                st.error("Lütfen hammadde lot numarasını boş bırakmayın!")
            else:
                st.session_state.hammadde_depo.append({
                    "Giriş Tarihi": str(g_tarih), "Hammadde": h_turu, "LOT No": h_lot, "Miktar (Ton)": h_miktar
                })
                st.success(f"✅ {h_miktar} Ton {h_turu} ({h_lot}) depoya alındı.")

# ==========================================
# SAYFA: REÇETE OLUŞTURMA
# ==========================================
elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Yeni Ürün Reçetesi (BOM) Tanımlama")
    st.write("Kendi mamul listenizi oluşturmak için ilk olarak buradan reçete ismi ve kimyasal oranları belirleyin.")
    
    with st.form("recete_form"):
        r_adi = st.text_input("Reçete / Ürün Adı", placeholder="Örn: Şişelik PET Resin (IV 0.80)")
        r_pta = st.number_input("1 Ton PET için gereken PTA (Ton)", min_value=0.0, value=0.86)
        r_meg = st.number_input("1 Ton PET için gereken MEG (Ton)", min_value=0.0, value=0.34)
        
        submit = st.form_submit_button("Reçeteyi Sisteme Kaydet")
        if submit:
            if r_adi == "":
                st.error("Reçete adı boş olamaz.")
            else:
                st.session_state.receteler.append({
                    "Reçete Adı": r_adi, "Gereken PTA (Ton/1 Ton Ürün)": r_pta, "Gereken MEG (Ton/1 Ton Ürün)": r_meg
                })
                st.success(f"🎉 '{r_adi}' reçetesi başarıyla oluşturuldu.")
    
    if st.session_state.receteler:
        st.subheader("📋 Kayıtlı Reçeteleriniz (Mamul Havuzunuz)")
        st.dataframe(pd.DataFrame(st.session_state.receteler), use_container_width=True)

# ==========================================
# SAYFA: ÜRETİM EMRİ VE GİRİŞİ
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Emri Girişi ve Otomatik Stok Düşümü")
    
    if not st.session_state.receteler:
        st.warning("⚠️ Kendi mamul listenizi oluşturmak için lütfen önce 'Reçete Oluşturma Sayfası' üzerinden en az bir ürün tanımlayın.")
    else:
        recete_listesi = [r["Reçete Adı"] for r in st.session_state.receteler]
        
        with st.form("uretim_form"):
            u_secilen_recete = st.selectbox("Üretilecek Mamul Seçin", recete_listesi)
            u_lot = st.text_input("Üretim LOT Numarası", value=f"PR-{datetime.now().strftime('%M%S')}")
            u_miktar = st.number_input("Üretilecek Miktar (Ton)", min_value=0.1, value=10.0)
            
            submit = st.form_submit_button("Üretimi Tamamla (Depoya Ekle)")
            if submit:
                recete_detay = next(r for r in st.session_state.receteler if r["Reçete Adı"] == u_secilen_recete)
                toplam_gereken_pta = u_miktar * recete_detay["Gereken PTA (Ton/1 Ton Ürün)"]
                toplam_gereken_meg = u_miktar * recete_detay["Gereken MEG (Ton/1 Ton Ürün)"]
                
                current_h_stok = toplam_hammadde_stok()
                
                if current_h_stok.get("PTA", 0.0) >= toplam_gereken_pta and current_h_stok.get("MEG", 0.0) >= toplam_gereken_meg:
                    pta_dusulecek = toplam_gereken_pta
                    meg_dusulecek = toplam_gereken_meg
                    
                    for h_kayit in st.session_state.hammadde_depo:
                        if h_kayit["Hammadde"] == "PTA" and pta_dusulecek > 0:
                            fark = min(h_kayit["Miktar (Ton)"], pta_dusulecek)
                            h_kayit["Miktar (Ton)"] -= fark
                            pta_dusulecek -= fark
                        if h_kayit["Hammadde"] == "MEG" and meg_dusulecek > 0:
                            fark = min(h_kayit["Miktar (Ton)"], meg_dusulecek)
                            h_kayit["Miktar (Ton)"] -= fark
                            meg_dusulecek -= fark
                    
                    # Mamul listesine ekleme yapılıyor
                    st.session_state.mamul_depo.append({
                        "Üretim Tarihi": datetime.now().strftime("%Y-%m-%d"),
                        "Ürün": u_secilen_recete,
                        "Üretim LOT": u_lot,
                        "Miktar (Ton)": u_miktar
                    })
                    st.success(f"🚀 Üretim Başarıyla Tamamlandı! {u_secilen_recete} ürünü {u_lot} lotu ile mamul listenize eklendi.")
                else:
                    st.error("❌ Yetersiz Hammadde! Üretim gerçekleştirilemedi.")
