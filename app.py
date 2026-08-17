import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.3", layout="wide")

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

if 'receteler' not in st.session_state:
    st.session_state.receteler = []

if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

# --- ANLIK STOK HESAPLAYICI ---
def toplam_hammadde_stok():
    df = pd.DataFrame(st.session_state.hammadde_depo)
    ham_listesi = ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"]
    if df.empty: 
        return {h: 0.0 for h in ham_listesi}
    grup_toplamlari = df.groupby("Hammadde")["Miktar (Ton)"].sum().to_dict()
    for h in ham_listesi:
        if h not in grup_toplamlari:
            grup_toplamlari[h] = 0.0
    return grup_toplamlari

def toplam_mamul_stok():
    df = pd.DataFrame(st.session_state.mamul_depo)
    if df.empty: return {}
    return df.groupby("Ürün")["Miktar (Ton)"].sum().to_dict()

# 3. YAN PANEL MENÜ SİSTEMİ
st.sidebar.title("🧪 PET Resin ERP v2.3")
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
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PTA Stoku", f"{h_stok.get('PTA', 0.0):.2f} Ton")
    col2.metric("MEG Stoku", f"{h_stok.get('MEG', 0.0):.2f} Ton")
    col3.metric("Antimon Stoku", f"{h_stok.get('Antimon', 0.0):.2f} Ton")
    col4.metric("Fosforik Asit Stoku", f"{h_stok.get('Fosforik Asit', 0.0):.2f} Ton")
    
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
        h_lot = st.text_input("Hammadde LOT Numarası")
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
    st.write("Tüm hammadde ve kimyasalların 1 Ton PET Resin üretimi için gereken standart (teorik) miktarlarını girin.")
    
    with st.form("recete_form"):
        r_adi = st.text_input("Reçete / Ürün Adı", placeholder="Örn: Şişelik PET Resin (IV 0.80)")
        
        st.subheader("🧪 1 Ton Ürün İçin Gereken Hammadde Oranları (Ton Cinsinden)")
        c1, c2, c3, c4 = st.columns(4)
        r_pta = c1.number_input("PTA (Ton)", min_value=0.0, value=0.860, format="%.3f")
        r_meg = c2.number_input("MEG (Ton)", min_value=0.0, value=0.340, format="%.3f")
        r_ant = c3.number_input("Antimon (Ton)", min_value=0.0, value=0.001, format="%.4f")
        r_fos = c4.number_input("Fosforik Asit (Ton)", min_value=0.0, value=0.001, format="%.4f")
        
        c5, c6, c7, c8 = st.columns(4)
        r_mav = c5.number_input("Mavi Boya (Ton)", min_value=0.0, value=0.0001, format="%.5f")
        r_kir = c6.number_input("Kırmızı Boya (Ton)", min_value=0.0, value=0.0001, format="%.5f")
        r_ipa = c7.number_input("IPA (Ton)", min_value=0.0, value=0.005, format="%.3f")
        r_deg = c8.number_input("DEG (Ton)", min_value=0.0, value=0.010, format="%.3f")
        
        submit = st.form_submit_button("Tüm Hammaddelerle Reçeteyi Kaydet")
        if submit:
            if r_adi == "":
                st.error("Reçete adı boş olamaz.")
            else:
                st.session_state.receteler.append({
                    "Reçete Adı": r_adi, "PTA": r_pta, "MEG": r_meg, "Antimon": r_ant, 
                    "Fosforik Asit": r_fos, "Mavi Boya": r_mav, "Kırmızı Boya": r_kir, "IPA": r_ipa, "DEG": r_deg
                })
                st.success(f"🎉 Tüm hammaddeleri içeren '{r_adi}' reçetesi başarıyla havuza eklendi.")
    
    if st.session_state.receteler:
        st.subheader("📋 Sistemde Kayıtlı Reçeteler ve Oranları")
        st.dataframe(pd.DataFrame(st.session_state.receteler), use_container_width=True)

# ==========================================
# SAYFA: ÜRETİM EMRİ VE GİRİŞİ
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Emri Girişi ve Fiili Miktar Düzenleme")
    
    if not st.session_state.receteler:
        st.warning("⚠️ Lütfen önce 'Reçete Oluşturma Sayfası' üzerinden bir ürün tanımlayın.")
    else:
        recete_listesi = [r["Reçete Adı"] for r in st.session_state.receteler]
        
        u_secilen_recete = st.selectbox("Üretilecek Mamul Seçin", recete_listesi)
        u_lot = st.text_input("Üretim LOT Numarası", value=f"PR-{datetime.now().strftime('%M%S')}")
        u_miktar = st.number_input("Üretilecek Miktar (Ton)", min_value=0.1, value=10.0, step=1.0)
        
        recete_detay = next(r for r in st.session_state.receteler if r["Reçete Adı"] == u_secilen_recete)
        
        st.write("---")
        st.subheader("📋 Fiili Tüketim Miktarlarını Girin")
        st.info("💡 Değerleri reaktörden gelen gerçekleşen rakamlara göre elle düzeltebilirsiniz.")
        
        with st.form("fiili_tuketim_form"):
            col1, col2, col3, col4 = st.columns(4)
            f_pta = col1.number_input("Fiili PTA (Ton)", value=u_miktar * recete_detay["PTA"], format="%.3f")
            f_meg = col2.number_input("Fiili MEG (Ton)", value=u_miktar * recete_detay["MEG"], format="%.3f")
            f_ant = col3.number_input("Fiili Antimon (Ton)", value=u_miktar * recete_detay["Antimon"], format="%.4f")
            f_fos = col4.number_input("Fiili Fosforik Asit (Ton)", value=u_miktar * recete_detay["Fosforik Asit"], format="%.4f")
            
            col5, col6, col7, col8 = st.columns(4)
            f_mav = col5.number_input("Fiili Mavi Boya (Ton)", value=u_miktar * recete_detay["Mavi Boya"], format="%.5f")
            f_kir = col6.number_input("Fiili Kırmızı Boya (Ton)", value=u_miktar * recete_detay["Kırmızı Boya"], format="%.5f")
            f_ipa = col7.number_input("Fiili IPA (Ton)", value=u_miktar * recete_detay["IPA"], format="%.3f")
            f_deg = col8.number_input("Fiili DEG (Ton)", value=u_miktar * recete_detay["DEG"], format="%.3f")
            
            st.write("")
            onayla_sekmesi = st.form_submit_button("Üretimi Onayla ve Depoya Ekle")
            
            if onayla_sekmesi:
                fiili_tuketimler = {
                    "PTA": f_pta, "MEG": f_meg, "Antimon": f_ant, "Fosforik Asit": f_fos,
                    "Mavi Boya": f_mav, "Kırmızı Boya": f_kir, "IPA": f_ipa, "DEG": f_deg
                }
                
                current_h_stok = toplam_hammadde_stok()
                yetersiz_maddeler = []
                
                for madde, miktar in fiili_tuketimler.items():
                    if current_h_stok.get(madde, 0.0) < miktar:
                        yetersiz_maddeler.append(f"{madde} (Gereken: {miktar:.3f}, Stok: {current_h_stok.get(madde, 0.0):.3f})")
                
                if yetersiz_maddeler:
                    st.error(f"❌ Stok Yetersiz! Girdiğiniz fiili miktarlara göre depoda yeterli hammadde yok:\n" + "\n".join(yetersiz_maddeler))
                else:
                    for madde, dusulecek_miktar in fiili_tuketimler.items():
                        kalan_dusulecek = dusulecek_miktar
                        for h_kayit in st.session_state.hammadde_depo:
                            if h_kayit["Hammadde"] == madde and kalan_dusulecek > 0:
                                fark = min(h_kayit["Miktar (Ton)"], kalan_dusulecek)
                                h_kayit["Miktar (Ton)"] -= fark
                                kalan_dusulecek -= fark
                    
                    st.session_state.mamul_depo.append({
                        "Üretim Tarihi": datetime.now().strftime("%Y-%m-%d"),
                        "Ürün": u_secilen_recete,
                        "Üretim LOT": u_lot,
                        "Miktar (Ton)": u_miktar
                    })
                    st.success(f"🚀 Üretim Başarıyla Onaylandı! Girdiğiniz fiili miktarlar depodan düşüldü ve {u_lot} lotlu {u_miktar} Ton mamul depoya eklendi.")
