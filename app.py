import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.6", layout="wide")

# MALZEME KARTLARI SABİT LİSTESİ (Operatörün elle yazmasını engelleyen rehber sözlük)
KATEGORI_MALZEMELERI = {
    "Hammadde": ["PTA", "MEG", "IPA", "DEG"],
    "Yardımcı Kimyasal": ["Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya"],
    "Ambalaj": ["PET Big Bag Çuval", "Ahşap Palet"],
    "Ara Mamul": ["Standart Amorf Chips"]
}

# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        # Hammaddeler
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar (Kg/Adet)": 100000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "MEG", "LOT No": "MEG-LOT-001", "Miktar (Kg/Adet)": 50000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "IPA", "LOT No": "IPA-LOT-001", "Miktar (Kg/Adet)": 1500.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "DEG", "LOT No": "DEG-LOT-001", "Miktar (Kg/Adet)": 4000.0},
        # Yardımcı Kimyasallar
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Antimon", "LOT No": "ANT-LOT-001", "Miktar (Kg/Adet)": 5000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Fosforik Asit", "LOT No": "FOS-LOT-001", "Miktar (Kg/Adet)": 2000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Mavi Boya", "LOT No": "BOY-M-001", "Miktar (Kg/Adet)": 500.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Kırmızı Boya", "LOT No": "BOY-K-001", "Miktar (Kg/Adet)": 300.0},
        # Ambalaj Malzemeleri
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ambalaj", "Hammadde": "PET Big Bag Çuval", "LOT No": "BB-LOT-01", "Miktar (Kg/Adet)": 500.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ambalaj", "Hammadde": "Ahşap Palet", "LOT No": "PLT-LOT-01", "Miktar (Kg/Adet)": 200.0},
        # Ara Mamuller
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ara Mamul", "Hammadde": "Standart Amorf Chips", "LOT No": "AMF-LOT-00", "Miktar (Kg/Adet)": 10000.0}
    ]

if 'hammadde_kullanilan_toplam' not in st.session_state:
    st.session_state.hammadde_kullanilan_toplam = {}

if 'receteler' not in st.session_state:
    st.session_state.receteler = [
        {
            "Reçete Adı": "Standart Amorf Chips (Reaktör)",
            "Tür": "Ara Mamul Reçetesi",
            "BOM": {"PTA": 0.850, "MEG": 0.135, "Antimon": 0.005, "Fosforik Asit": 0.002, "Mavi Boya": 0.001, "Kırmızı Boya": 0.001, "IPA": 0.004, "DEG": 0.002}
        },
        {
            "Reçete Adı": "Şişelik Kristalize PET Resin (SSP)",
            "Tür": "Mamul Reçetesi",
            "BOM": {"Standart Amorf Chips": 1.000, "PET Big Bag Çuval": 0.001, "Ahşap Palet": 0.001}
        }
    ]

if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

def segment_stok_getir():
    df = pd.DataFrame(st.session_state.hammadde_depo)
    if df.empty:
        return {}
    
    grup_toplamlari = df.groupby("Hammadde")["Miktar (Kg/Adet)"].sum().to_dict()
    güncel_stok = {}
    
    for h_adi, giren in grup_toplamlari.items():
        kullanilan = st.session_state.hammadde_kullanilan_toplam.get(h_adi, 0.0)
        güncel_stok[h_adi] = max(0.0, giren - kullanilan)
    return güncel_stok
# 3. YAN PANEL MENÜ SİSTEMİ
st.sidebar.title("🧪 PET Resin ERP v2.6")
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
    st.header("📊 Fabrika Segment Bazlı Anlık Depo Paneli")
    
    stok_dict = segment_stok_getir()
    df_merkez = pd.DataFrame(st.session_state.hammadde_depo)
    
    kat_rehber = df_merkez.set_index("Hammadde")["Kategori"].to_dict() if not df_merkez.empty else {}

    # 1) Hammaddeler
    st.markdown("### 🛠️ 1) Hammadde Stokları")
    c1, c2, c3, c4 = st.columns(4)
    cols1 = [c1, c2, c3, c4]
    ham_idx = 0
    for h, m in stok_dict.items():
        if kat_rehber.get(h) == "Hammadde":
            cols1[ham_idx % 4].metric(h, f"{m:,.1f} Kg")
            ham_idx += 1
    st.write("---")
    
    # 2) Yardımcı Kimyasallar
    st.markdown("### 🧪 2) Yardımcı Kimyasal Stokları")
    c5, c6, c7, c8 = st.columns(4)
    cols2 = [c5, c6, c7, c8]
    kim_idx = 0
    for h, m in stok_dict.items():
        if kat_rehber.get(h) == "Yardımcı Kimyasal":
            cols2[kim_idx % 4].metric(h, f"{m:,.1f} Kg")
            kim_idx += 1
    st.write("---")

    # 3) Ambalaj
    st.markdown("### 📦 3) Ambalaj Malzemesi Stokları")
    c9, c10 = st.columns(2)
    cols3 = [c9, c10]
    amb_idx = 0
    for h, m in stok_dict.items():
        if kat_rehber.get(h) == "Ambalaj":
            cols3[amb_idx % 2].metric(h, f"{m:,.0f} Adet")
            amb_idx += 1
    st.write("---")

    # 4) Ara Mamul
    st.markdown("### ⚙️ 4) Ara Mamul Stokları")
    for h, m in stok_dict.items():
        if kat_rehber.get(h) == "Ara Mamul":
            st.metric(h, f"{m:,.1f} Kg")
    st.write("---")

    # 5) Ürün Bazlı Gruplanmış Satışa Hazır Mamul Stokları
    st.markdown("### 🏭 5) Ürün Bazlı Gruplanmış Satışa Hazır Mamul Stokları")
    if st.session_state.mamul_depo:
        df_mamul = pd.DataFrame(st.session_state.mamul_depo)
        for urun_adi, urun_data in df_mamul.groupby("Ürün"):
            toplam_urun_stok = urun_data["Miktar (Kg)"].sum()
            benzersiz_lot = urun_data["Üretim LOT / Silo"].nunique()
            
            with st.expander(f"🔹 {urun_adi}  |  Stok: {toplam_urun_stok:,.1f} Kg"):
                m1, m2 = st.columns(2)
                m1.metric("Toplam Net Stok", f"{toplam_urun_stok:,.1f} Kg")
                m2.metric("Silo / LOT Çeşitliliği", f"{benzersiz_lot} LOT")
                st.dataframe(urun_data[["Üretim Tarihi", "Üretim LOT / Silo", "Miktar (Kg)"]].reset_index(drop=True), use_container_width=True)
    else:
        st.info("Satışa hazır bitmiş mamul stoku bulunmuyor.")
# ==========================================
# SAYFA: HAMMADDE / MALZEME GİRİŞİ (YENİLENDİ - SELECTBOX ENTEGRE EDİLDİ)
# ==========================================
elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Fabrika Depolarına Giriş Kabul Ekranı")
    
    # 1. Aşama: Kategori Seçimi (Form dışında, alt kutuyu anlık tetiklemesi için)
    kat_turu = st.selectbox("Malzeme Kategorisi Seçin", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul"])
    
    # Seçilen kategoriye ait tanımlı malzemeleri listeden çekiyoruz
    uygun_malzemeler = KATEGORI_MALZEMELERI.get(kat_turu, [])
    
    with st.form("hammadde_form"):
        g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
        
        # ARTIK ELLE YAZILMIYOR: Seçilen kategoriye ait kalemler selectbox olarak gelir
        h_turu = st.selectbox("Malzeme / Kalem Adı", uygun_malzemeler)
        
        h_lot = st.text_input("Gelen LOT / Parti Numarası", placeholder="Örn: LOT-PTA-2026-01")
        h_miktar = st.number_input("Gelen Miktar (Kg veya Adet)", min_value=0.1, step=50.0, format="%.1f")
        
        submit = st.form_submit_button("Malzemeyi Depoya Kabul Et")
        if submit:
            if not h_lot: 
                st.error("Lütfen LOT numarasını boş bırakmayın!")
            else:
                st.session_state.hammadde_depo.append({
                    "Giriş Tarihi": str(g_tarih), 
                    "Kategori": kat_turu, 
                    "Hammadde": h_turu, 
                    "LOT No": h_lot, 
                    "Miktar (Kg/Adet)": h_miktar
                })
                st.success(f"✅ {h_miktar:,.1f} ölçüsünde {h_turu} ({kat_turu}) depoya başarıyla kabul edildi.")
                st.rerun()

# ==========================================
# SAYFA: REÇETE OLUŞTURMA
# ==========================================
elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Yeni Ürün Reçetesi (BOM) Tanımlama")
    r_turu = st.selectbox("Reçete Sınıfı", ["Ara Mamul Reçetesi", "Mamul Reçetesi"])
    
    with st.form("recete_form"):
        r_adi = st.text_input("Reçete / Ürün Adı")
        st.write("1 Birim üretim için gerekli olan katsayıları girin (Kg/Kg veya Adet/Kg):")
        
        df_m = pd.DataFrame(st.session_state.hammadde_depo)
        mevcut_kalemler = df_m["Hammadde"].unique().tolist() if not df_m.empty else []
        
        secilen_bom = {}
        if mevcut_kalemler:
            st.write("**BOM Eleman Miktarları (Yoksa 0 bırakın):**")
            for m_kalem in mevcut_kalemler:
                val = st.number_input(f"{m_kalem} İhtiyacı", min_value=0.0, max_value=100.0, value=0.0, step=0.001, format="%.3f")
                if val > 0: secilen_bom[m_kalem] = val
                
        recete_submit = st.form_submit_button("Reçeteyi Sisteme Kaydet")
        if recete_submit and r_adi:
            st.session_state.receteler.append({"Reçete Adı": r_adi, "Tür": r_turu, "BOM": secilen_bom})
            st.success(f"✅ '{r_adi}' ({r_turu}) başarıyla kaydedildi!")

# ==========================================
# SAYFA: ÜRETİM EMRİ & GİRİŞİ
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Yönetim ve Reaktör Besleme Arayüzü")
    u_kategori = st.radio("Yapılacak Üretim Sınıfı:", [
        "1) Ara Mamul Üretimi (Hammadde + Yardımcı Kimyasal Tüketir, Ara Mamul Üretir)", 
        "2) Mamul Üretimi (Ara Mamul + Ambalaj Tüketir, Nihai Ürün Üretir)"
    ])
    
    hedef_tur = "Ara Mamul Reçetesi" if "1)" in u_kategori else "Mamul Reçetesi"
    uygun_receteler = [r for r in st.session_state.receteler if r.get("Tür")
    
    if not uygun_receteler:
        st.warning(f"⚠️ Bu kategoride kayıtlı bir reçete bulunamadı. Lütfen önce {hedef_tur} tanımlayın.")
    else:
        stok_dict = segment_stok_getir()
        secilen_recete_adi = st.selectbox("Kullanılacak Reçeteyi Seçin", [r["Reçete Adı"] for r in uygun_receteler])
        hedef_miktar = st.number_input("Hedef Üretim Hacmi (Kg)", min_value=1.0, value=1000.0, step=100.0, format="%.1f")
        u_lot = st.text_input("Üretim Parti / Silo LOT No", value=f"LOT-{datetime.now().strftime('%Y%m%d%H%M')}")
        
        secilen_recete = next(r for r in uygun_receteler if r["Reçete Adı"] == secilen_recete_adi)
        
        st.write("---")
        st.subheader("⚙️ Fiili Tüketim Giriş Matrisi")
        
        with st.form("uretim_form"):
            fiili_girisler = {}
            c1_f, c2_f, c3_f, c4_f = st.columns(4)
            cols_list = [c1_f, c2_f, c3_f, c4_f]
            
            for idx, (h_adi, oran) in enumerate(secilen_recete["BOM"].items()):
                teorik = hedef_miktar * oran
                current_col = cols_list[idx % 4]
                
                fiili_girisler[h_adi] = current_col.number_input(
                    f"{h_adi} Fiili Tüketim", 
                    min_value=0.0, 
                    value=float(teorik), 
                    step=1.0, 
                    format="%.2f"
                )
                
            uretim_submit = st.form_submit_button("Üretim İşlemini Onayla ve Depoları Güncelle")
            if uretim_submit:
                kontrol = True
                eksikler = []
                for h_adi, f_kg in fiili_girisler.items():
                    if stok_dict.get(h_adi, 0.0) < f_kg:
                        kontrol = False
                        eksikler.append(f"{h_adi} (Talep: {f_kg:,.1f}, Mevcut: {stok_dict.get(h_adi,0.0):,.1f})")
                
                if not kontrol:
                    st.error("❌ Stok Yetersiz! Girilen fiili değerler depo bakiyelerini aşmaktadır:\n" + "\n".join([f"- {i}" for i in eksikler]))
                else:
                    for h_adi, f_kg in fiili_girisler.items():
                        st.session_state.hammadde_kullanilan_toplam[h_adi] = st.session_state.hammadde_kullanilan_toplam.get(h_adi, 0.0) + f_kg
                    
                    if hedef_tur == "Ara Mamul Reçetesi":
                        st.session_state.hammadde_depo.append({
                            "Giriş Tarihi": datetime.now().strftime("%Y-%m-%d"),
                            "Kategori": "Ara Mamul",
                            "Hammadde": secilen_recete_adi,
                            "LOT No": u_lot,
                            "Miktar (Kg/Adet)": hedef_miktar
                        })
                        st.success(f"🎉 Ara Mamul Başarıyla Üretildi! {hedef_miktar:,.1f} Kg ürün Ara Mamul stoklarına eklendi.")
                    else:
                        st.session_state.mamul_depo.append({
                            "Üretim Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Ürün": secilen_recete_adi,
                            "Üretim LOT / Silo": u_lot,
                            "Miktar (Kg)": hedef_miktar
                        })
                        st.success(f"🎉 Nihai Ürün Başarıyla Paketlenip Ambalajlandı! {hedef_miktar:,.1f} Kg ürün Satış Deposuna aktarıldı.")
                    st.rerun()
