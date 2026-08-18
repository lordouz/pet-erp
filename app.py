import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.6", layout="wide")

# MERKEZİ STOK KARTLARI HAFIZASI (Kullanıcı dinamik olarak artırabilir)
if 'stok_kartlari' not in st.session_state:
    st.session_state.stok_kartlari = {
        "Hammadde": ["PTA", "MEG", "IPA", "DEG"],
        "Yardımcı Kimyasal": ["Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya"],
        "Ambalaj": ["PET Big Bag Çuval", "Ahşap Palet"],
        "Ara Mamul": ["Standart Amorf Chips"]
    }

# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar (Kg/Adet)": 100000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "MEG", "LOT No": "MEG-LOT-001", "Miktar (Kg/Adet)": 50000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "IPA", "LOT No": "IPA-LOT-001", "Miktar (Kg/Adet)": 1500.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "DEG", "LOT No": "DEG-LOT-001", "Miktar (Kg/Adet)": 4000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Antimon", "LOT No": "ANT-LOT-001", "Miktar (Kg/Adet)": 5000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Fosforik Asit", "LOT No": "FOS-LOT-001", "Miktar (Kg/Adet)": 2000.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ambalaj", "Hammadde": "PET Big Bag Çuval", "LOT No": "BB-LOT-01", "Miktar (Kg/Adet)": 500.0},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ara Mamul", "Hammadde": "Standart Amorf Chips", "LOT No": "AMF-LOT-00", "Miktar (Kg/Adet)": 10000.0}
    ]

if 'hammadde_kullanilan_toplam' not in st.session_state:
    st.session_state.hammadde_kullanilan_toplam = {}

if 'receteler' not in st.session_state:
    st.session_state.receteler = [
        {
            "Reçete Adı": "Standart Amorf Chips (Reaktör)",
            "Tür": "Ara Mamul Reçetesi",
            "BOM": {"PTA": 0.850, "MEG": 0.135, "Antimon": 0.005, "Fosforik Asit": 0.002}
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
    "🗂️ 0. Stok Kartı Tanımlama Sayfası",
    "📥 1. Hammadde Giriş Sayfası",
    "📝 2. Reçete Oluşturma Sayfası",
    "🏭 3. Üretim Emri & Giriş Sayfası"
])

# ==========================================
# SAYFA: GENEL DEPO VE STOK DURUMU (TIKLAYINCA AÇILAN BAŞLIKLAR)
# ==========================================
if sayfa == "📊 Genel Depo & Stok Durumu":
    st.header("📊 Fabrika Segment Bazlı Anlık Depo Paneli")
    st.info("💡 Stok detaylarını ve miktarlarını görmek için aşağıdaki ilgili başlığa tıklayınız.")
    
    stok_dict = segment_stok_getir()
    df_merkez = pd.DataFrame(st.session_state.hammadde_depo)
    kat_rehber = df_merkez.set_index("Hammadde")["Kategori"].to_dict() if not df_merkez.empty else {}

    # 1) Hammaddeler Başlığı
    with st.expander("🛠️ 1) HAMMADDE DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c1, c2, c3, c4 = st.columns(4)
        cols1 = [c1, c2, c3, c4]
        ham_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Hammadde":
                cols1[ham_idx % 4].metric(h, f"{m:,.1f} Kg")
                ham_idx += 1
        if ham_idx == 0: st.write("Bu kategoride bakiye bulunmuyor.")
    
    # 2) Yardımcı Kimyasallar Başlığı
    with st.expander("🧪 2) YARDIMCI KİMYASAL DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c5, c6, c7, c8 = st.columns(4)
        cols2 = [c5, c6, c7, c8]
        kim_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Yardımcı Kimyasal":
                cols2[kim_idx % 4].metric(h, f"{m:,.1f} Kg")
                kim_idx += 1
        if kim_idx == 0: st.write("Bu kategoride bakiye bulunmuyor.")

    # 3) Ambalaj Başlığı
    with st.expander("📦 3) AMBALAJ MALZEMESİ DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c9, c10 = st.columns(2)
        cols3 = [c9, c10]
        amb_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Ambalaj":
                cols3[amb_idx % 2].metric(h, f"{m:,.0f} Adet")
                amb_idx += 1
        if amb_idx == 0: st.write("Bu kategoride bakiye bulunmuyor.")

    # 4) Ara Mamul Başlığı
    with st.expander("⚙️ 4) ARA MAMUL DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        ara_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Ara Mamul":
                st.metric(h, f"{m:,.1f} Kg")
                ara_idx += 1
        if ara_idx == 0: st.write("Bu kategoride bakiye bulunmuyor.")

    # 5) Ürün Bazlı Gruplanmış Satışa Hazır Mamul Başlığı
    with st.expander("🏭 5) ÜRÜN BAZLI SATIŞA HAZIR MAMUL DEPOSU İÇİN TIKLAYIN"):
        if st.session_state.mamul_depo:
            df_mamul = pd.DataFrame(st.session_state.mamul_depo)
            for urun_adi, urun_data in df_mamul.groupby("Ürün"):
                toplam_urun_stok = urun_data["Miktar (Kg)"].sum()
                benzersiz_lot = urun_data["Üretim LOT / Silo"].nunique()
                st.write(f"**🔹 {urun_adi}** | Toplam Stok: {toplam_urun_stok:,.1f} Kg | LOT Çeşitliliği: {benzersiz_lot} Adet")
                st.dataframe(urun_data[["Üretim Tarihi", "Üretim LOT / Silo", "Miktar (Kg)"]].reset_index(drop=True), use_container_width=True)
        else:
            st.info("Satışa hazır bitmiş mamul stoku bulunmuyor.")
# ==========================================
# SAYFA 0: YENİ STOK KARTI TANIMLAMA (YENİ SAYFA EKLENDİ)
# ==========================================
elif sayfa == "🗂️ 0. Stok Kartı Tanımlama Sayfası":
    st.header("🗂️ Fabrika Malzeme / Stok Kartı Tanımlama")
    st.write("Sisteme yeni hammadde, ambalaj veya kimyasal kartları ekleyerek ERP kapsamını genişletin.")
    
    with st.form("stok_kart_form"):
        k_kat = st.selectbox("Kartın Bağlanacağı Kategori", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul"])
        k_adi = st.text_input("Yeni Malzeme / Stok Kartı Adı", placeholder="Örn: Katı Katalizör X-42")
        
        kart_submit = st.form_submit_button("Yeni Stok Kartını Sisteme Kaydet")
        if kart_submit:
            if not k_adi:
                st.error("❌ Kart adı boş bırakılamaz!")
            elif k_adi in st.session_state.stok_kartlari[k_kat]:
                st.warning("⚠️ Bu malzeme kartı seçilen kategoride zaten mevcut!")
            else:
                st.session_state.stok_kartlari[k_kat].append(k_adi)
                st.success(f"✅ '{k_adi}' kartı başarıyla '{k_kat}' kategorisine eklendi ve kullanıma açıldı.")
                st.rerun()
                
    st.subheader("📋 Güncel Sistem Kart Matrisi")
    for k, v in st.session_state.stok_kartlari.items():
        st.write(f"**{k}:** {', '.join(v)}")

# ==========================================
# SAYFA: HAMMADDE / MALZEME GİRİŞİ (DİNAMİK KARTLARA BAĞLANDI)
# ==========================================
elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Fabrika Depolarına Giriş Kabul Ekranı")
    kat_turu = st.selectbox("Malzeme Kategorisi Seçin", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul"])
    
    # Yeni eklenen kartları da görecek şekilde dinamik listeden veri çekiyoruz
    uygun_malzemeler = st.session_state.stok_kartlari.get(kat_turu, [])
    
    with st.form("hammadde_form"):
        g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
        h_turu = st.selectbox("Malzeme / Kalem Adı", uygun_malzemeler)
        h_lot = st.text_input("Gelen LOT / Parti Numarası")
        h_miktar = st.number_input("Gelen Miktar", min_value=0.1, step=50.0, format="%.1f")
        
        submit = st.form_submit_button("Malzemeyi Depoya Kabul Et")
        if submit:
            st.session_state.hammadde_depo.append({"Giriş Tarihi": str(g_tarih), "Kategori": kat_turu, "Hammadde": h_turu, "LOT No": h_lot, "Miktar (Kg/Adet)": h_miktar})
            st.success(f"✅ {h_turu} depoya alındı."); st.rerun()

# ==========================================
# SAYFA: REÇETE OLUŞTURMA
# ==========================================
elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Yeni Ürün Reçetesi (BOM) Tanımlama")
    r_turu = st.selectbox("Reçete Sınıfı", ["Ara Mamul Reçetesi", "Mamul Reçetesi"])
    
    with st.form("recete_form"):
        r_adi = st.text_input("Reçete / Ürün Adı")
        secilen_bom = {}
        
        # Tüm dinamik kartları reçete formuna listeliyoruz
        for kat, kalemler in st.session_state.stok_kartlari.items():
            for kalem in kalemler:
                val = st.number_input(f"[{kat}] {kalem} İhtiyacı", min_value=0.0, max_value=100.0, value=0.0, step=0.001, format="%.3f")
                if val > 0: secilen_bom[kalem] = val
                
        recete_submit = st.form_submit_button("Reçeteyi Kaydet")
        if recete_submit and r_adi:
            st.session_state.receteler.append({"Reçete Adı": r_adi, "Tür": r_turu, "BOM": secilen_bom})
            st.success("✅ Reçete kaydedildi!")

# ==========================================
# SAYFA: ÜRETİM EMRİ & GİRİŞİ
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Yönetim ve Reaktör Besleme Arayüzü")
    u_kategori = st.radio("Yapılacak Üretim Sınıfı:", ["1) Ara Mamul Üretimi", "2) Mamul Üretimi"])
    hedef_tur = "Ara Mamul Reçetesi" if "1)" in u_kategori else "Mamul Reçetesi"
    
    uygun_receteler = [r for r in st.session_state.receteler if r.get("Tür") == hedef_tur]
    
    if not uygun_receteler:
        st.warning(f"⚠️ Bu kategoride kayıtlı bir reçete bulunamadı.")
    else:
        stok_dict = segment_stok_getir()
        secilen_recete_adi = st.selectbox("Kullanılacak Reçeteyi Seçin", [r["Reçete Adı"] for r in uygun_receteler])
        hedef_miktar = st.number_input("Hedef Üretim Hacmi (Kg)", min_value=1.0, value=1000.0)
        u_lot = st.text_input("Üretim Parti / Silo LOT No", value=f"LOT-{datetime.now().strftime('%Y%m%d%H%M')}")
        secilen_recete = next(r for r in uygun_receteler if r["Reçete Adı"] == secilen_recete_adi)
        
        with st.form("uretim_form"):
            fiili_girisler = {}
            for h_adi, oran in secilen_recete["BOM"].items():
                teorik = hedef_miktar * oran
                fiili_girisler[h_adi] = st.number_input(f"{h_adi} Fiili Tüketim", min_value=0.0, value=float(teorik))
                
            uretim_submit = st.form_submit_button("Üretimi Onayla")
            if uretim_submit:
                for h_adi, f_kg in fiili_girisler.items():
                    st.session_state.hammadde_kullanilan_toplam[h_adi] = st.session_state.hammadde_kullanilan_toplam.get(h_adi, 0.0) + f_kg
                if hedef_tur == "Ara Mamul Reçetesi":
                    st.session_state.hammadde_depo.append({"Giriş Tarihi": datetime.now().strftime("%Y-%m-%d"), "Kategori": "Ara Mamul", "Hammadde": secilen_recete_adi, "LOT No": u_lot, "Miktar (Kg/Adet)": hedef_miktar})
                else:
                    st.session_state.mamul_depo.append({"Üretim Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"), "Ürün": secilen_recete_adi, "Üretim LOT / Silo": u_lot, "Miktar (Kg)": hedef_miktar})
                st.success("🎉 Üretim tamamlandı!"); st.rerun()
