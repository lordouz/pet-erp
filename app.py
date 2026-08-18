import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.6", layout="wide")

# MERKEZİ STOK KARTLARI VE BİRİMLERİ HAFIZASI
if 'stok_kartlari' not in st.session_state:
    st.session_state.stok_kartlari = {
        "Hammadde": [
            {"Ad": "PTA", "Birim": "Kg"}, {"Ad": "MEG", "Birim": "Kg"},
            {"Ad": "IPA", "Birim": "Kg"}, {"Ad": "DEG", "Birim": "Kg"}
        ],
        "Yardımcı Kimyasal": [
            {"Ad": "Antimon", "Birim": "Kg"}, {"Ad": "Fosforik Asit", "Birim": "Kg"},
            {"Ad": "Mavi Boya", "Birim": "Kg"}, {"Ad": "Kırmızı Boya", "Birim": "Kg"}
        ],
        "Ambalaj": [
            {"Ad": "PET Big Bag Çuval", "Birim": "Adet"}, {"Ad": "Ahşap Palet", "Birim": "Adet"}
        ],
        "Ara Mamul": [
            {"Ad": "Standart Amorf Chips", "Birim": "Kg"}
        ]
    }

# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar": 100000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Hammadde", "Hammadde": "MEG", "LOT No": "MEG-LOT-001", "Miktar": 50000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Yardımcı Kimyasal", "Hammadde": "Antimon", "LOT No": "ANT-LOT-001", "Miktar": 5000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ambalaj", "Hammadde": "PET Big Bag Çuval", "LOT No": "BB-LOT-01", "Miktar": 500.0, "Birim": "Adet"},
        {"Giriş Tarihi": "2026-08-15", "Kategori": "Ara Mamul", "Hammadde": "Standart Amorf Chips", "LOT No": "AMF-LOT-00", "Miktar": 10000.0, "Birim": "Kg"}
    ]

if 'hammadde_kullanilan_toplam' not in st.session_state:
    st.session_state.hammadde_kullanilan_toplam = {}

if 'receteler' not in st.session_state:
    st.session_state.receteler = [
        {"Reçete Adı": "Standart Amorf Chips (Reaktör)", "Tür": "Ara Mamul Reçetesi", "BOM": {"PTA": 0.850000, "MEG": 0.135000, "Antimon": 0.005000}}
    ]

if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

if 'uretim_harcamalari_log' not in st.session_state:
    st.session_state.uretim_harcamalari_log = []

def malzeme_birimi_bul(malzeme_adi):
    for kat, kalemler in st.session_state.stok_kartlari.items():
        for k in kalemler:
            if k["Ad"] == malzeme_adi: return k["Birim"]
    return "Kg"

def segment_stok_getir():
    df = pd.DataFrame(st.session_state.hammadde_depo)
    if df.empty: return {}
    grup_toplamlari = df.groupby("Hammadde")["Miktar"].sum().to_dict()
    güncel_stok = {}
    for h_adi, giren in grup_toplamlari.items():
        kullanilan = st.session_state.hammadde_kullanilan_toplam.get(h_adi, 0.0)
        güncel_stok[h_adi] = max(0.0, giren - kullanilan)
    return güncel_stok
def endustriyel_excel_rapor_olustur(bas_tarih, bit_tarih):
    buffer = io.BytesIO()
    df_depo = pd.DataFrame(st.session_state.hammadde_depo)
    df_harcama = pd.DataFrame(st.session_state.uretim_harcamalari_log)
    df_mamul = pd.DataFrame(st.session_state.mamul_depo)
    
    def tarih_filtrele(df, tarih_kolonu):
        if df.empty or tarih_kolonu not in df.columns: return pd.DataFrame()
        df_copy = df.copy()
        df_copy[tarih_kolonu] = df_copy[tarih_kolonu].apply(lambda x: x.split(" ") if " " in str(x) else str(x))
        df_copy[tarih_kolonu] = pd.to_datetime(df_copy[tarih_kolonu]).dt.date
        return df_copy[(df_copy[tarih_kolonu] >= bas_tarih) & (df_copy[tarih_kolonu] <= bit_tarih)]

    f_depo_giris = tarih_filtrele(df_depo, "Giriş Tarihi")
    f_uretim_harcama = tarih_filtrele(df_harcama, "Tarih")
    f_mamul_depo = tarih_filtrele(df_mamul, "Üretim Tarihi")
    
    stok_durumu = segment_stok_getir()
    bakiye_satirlari = []
    for malz, kalan_stok in stok_durumu.items():
        bakiye_satirlari.append({
            "Malzeme / Ürün Adı": malz, "Mevcut Depo Stoğu": kalan_stok,
            "Ölçü Birimi": malzeme_birimi_bul(malz), "Toplam Harcanan Ölçü": st.session_state.hammadde_kullanilan_toplam.get(malz, 0.0)
        })
    df_anlik_bakiye = pd.DataFrame(bakiye_satirlari)

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        if not df_anlik_bakiye.empty: df_anlik_bakiye.to_excel(writer, index=False, sheet_name='Anlık Depo Bakiyeleri Özet')
        if not f_depo_giris.empty: f_depo_giris.to_excel(writer, index=False, sheet_name='Dönemsel Giriş Hareketleri')
        if not f_uretim_harcama.empty: f_uretim_harcama.to_excel(writer, index=False, sheet_name='Dönemsel Tüketim Detayları')
        if not f_mamul_depo.empty: f_mamul_depo.to_excel(writer, index=False, sheet_name='Dönemsel Mamul Üretimleri')
            
    return buffer.getvalue()

# 3. YAN PANEL MENÜ SİSTEMİ
st.sidebar.title("🧪 PET Resin ERP v2.6")
st.sidebar.write("---")
sayfa = st.sidebar.radio("Gitmek İstediğiniz Sayfa:", [
    "📊 Genel Depo & Stok Durumu",
    "📈 📊 Fabrika Raporlar Sayfası",
    "🗂️ 0. Stok Kartı Tanımlama Sayfası",
    "📥 1. Hammadde Giriş Sayfası",
    "📝 2. Reçete Oluşturma Sayfası",
    "🏭 3. Üretim Emri & Giriş Sayfası"
])

# ==========================================
# SAYFA: GENEL DEPO VE STOK DURUMU
# ==========================================
if sayfa == "📊 Genel Depo & Stok Durumu":
    st.header("📊 Fabrika Segment Bazlı Anlık Depo Paneli")
    st.info("💡 Stok detaylarını ve dinamik birim miktarlarını görmek için aşağıdaki ilgili başlığa tıklayınız.")
    
    stok_dict = segment_stok_getir()
    df_merkez = pd.DataFrame(st.session_state.hammadde_depo)
    kat_rehber = df_merkez.set_index("Hammadde")["Kategori"].to_dict() if not df_merkez.empty else {}

    with st.expander("🛠️ 1) HAMMADDE DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c1, c2, c3, c4 = st.columns(4)
        cols1 = [c1, c2, c3, c4]
        ham_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Hammadde":
                birim = malzeme_birimi_bul(h)
                cols1[ham_idx % 4].metric(h, f"{m:,.1f} {birim}")
                ham_idx += 1
        if ham_idx == 0: st.write("Bu kategoride aktif bakiye bulunmuyor.")
    
    with st.expander("🧪 2) YARDIMCI KİMYASAL DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c5, c6, c7, c8 = st.columns(4)
        cols2 = [c5, c6, c7, c8]
        kim_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Yardımcı Kimyasal":
                birim = malzeme_birimi_bul(h)
                cols2[kim_idx % 4].metric(h, f"{m:,.1f} {birim}")
                kim_idx += 1
        if kim_idx == 0: st.write("Bu kategoride aktif bakiye bulunmuyor.")

    with st.expander("📦 3) AMBALAJ MALZEMESİ DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        c9, c10 = st.columns(2)
        cols3 = [c9, c10]
        amb_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Ambalaj":
                birim = malzeme_birimi_bul(h)
                cols3[amb_idx % 2].metric(h, f"{m:,.0f} {birim}")
                amb_idx += 1
        if amb_idx == 0: st.write("Bu kategoride aktif bakiye bulunmuyor.")

    with st.expander("⚙️ 4) ARA MAMUL DEPOSU DETAYLARI İÇİN TIKLAYIN"):
        ara_idx = 0
        for h, m in stok_dict.items():
            if kat_rehber.get(h) == "Ara Mamul":
                st.metric(h, f"{m:,.1f} {malzeme_birimi_bul(h)}")
                ara_idx += 1
        if ara_idx == 0: st.write("Bu kategoride aktif bakiye bulunmuyor.")

    with st.expander("🏭 5) ÜRÜN BAZLI SATIŞA HAZIR MAMUL DEPOSU İÇİN TIKLAYIN"):
        if st.session_state.mamul_depo:
            df_mamul = pd.DataFrame(st.session_state.mamul_depo)
            for urun_adi, urun_data in df_mamul.groupby("Ürün"):
                toplam_urun_stok = urun_data["Miktar"].sum()
                benzersiz_lot = urun_data["Üretim LOT / Silo"].nunique()
                st.write(f"**🔹 {urun_adi}** | Toplam Stok: {toplam_urun_stok:,.1f} Kg | LOT: {benzersiz_lot} Adet")
                st.dataframe(urun_data[["Üretim Tarihi", "Üretim LOT / Silo", "Miktar"]].reset_index(drop=True), use_container_width=True)
        else:
            st.info("Satışa hazır bitmiş mamul stoku bulunmuyor.")
# ==========================================
# SAYFA: FABRİKA RAPORLAR SAYFASI
# ==========================================
elif sayfa == "📈 📊 Fabrika Raporlar Sayfası":
    st.header("📈 📊 Dönemsel Fabrika Üretim ve Stok Hareketleri Rapor İstasyonu")
    c_t1, c_t2 = st.columns(2)
    bas_secim = c_t1.date_input("Analiz Başlangıç Tarihi", value=date(2026, 1, 1))
    bit_secim = c_t2.date_input("Analiz Bitiş Tarihi", value=date(2026, 12, 31))
    
    if bas_secim <= bit_secim:
        excel_dosyası = endustriyel_excel_rapor_olustur(bas_secim, bit_secim)
        st.download_button(
            label="📊 Fabrika Konsolide Genel Stok Raporunu İndir (.XLSX)",
            data=excel_dosyası, file_name=f"Fabrika_Sistem_Raporu_{bas_secim}_to_{bit_secim}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==========================================
# SAYFA 0: BİRİMLİ STOK KARTI TANIMLAMA
# ==========================================
elif sayfa == "🗂️ 0. Stok Kartı Tanımlama Sayfası":
    st.header("🗂️ Fabrika Malzeme / Stok Kartı Tanımlama")
    with st.form("stok_kart_form"):
        k_kat = st.selectbox("Kartın Bağlanacağı Kategori", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul"])
        k_adi = st.text_input("Yeni Malzeme / Stok Kartı Adı")
        k_birim = st.selectbox("Miktar Ölçü Birimi", ["Kg", "Adet", "Ton"])
        if st.form_submit_button("Yeni Stok Kartını Sisteme Kaydet") and k_adi:
            st.session_state.stok_kartlari[k_kat].append({"Ad": k_adi, "Birim": k_birim})
            st.success(f"✅ '{k_adi}' kartı kaydedildi."); st.rerun()
            
    st.subheader("📋 Sistemde Kayıtlı Kart Listesi")
    for k, v in st.session_state.stok_kartlari.items():
        gosterim = [f"{x['Ad']} ({x['Birim']})" for x in v]
        st.write(f"**{k}:** {', '.join(gosterim)}")

# ==========================================
# SAYFA 1: HAMMADDE / MALZEME GİRİŞİ
# ==========================================
elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Fabrika Depolarına Giriş Kabul Ekranı")
    kat_turu = st.selectbox("Malzeme Kategorisi Seçin", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul"])
    uygun_malzemeler = [x["Ad"] for x in st.session_state.stok_kartlari.get(kat_turu, [])]
    
    if uygun_malzemeler:
        with st.form("hammadde_form"):
            g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
            h_turu = st.selectbox("Malzeme / Kalem Adı", uygun_malzemeler)
            h_lot = st.text_input("Gelen LOT / Parti Numarası")
            secilen_birim = malzeme_birimi_bul(h_turu)
            h_miktar = st.number_input(f"Gelen Miktar ({secilen_birim})", min_value=0.1, step=50.0)
            if st.form_submit_button("Malzemeyi Depoya Kabul Et") and h_lot:
                st.session_state.hammadde_depo.append({"Giriş Tarihi": str(g_tarih), "Kategori": kat_turu, "Hammadde": h_turu, "LOT No": h_lot, "Miktar": h_miktar, "Birim": secilen_birim})
                st.success(f"✅ {h_turu} alındı."); st.rerun()
# ==========================================
# SAYFA 2: REÇETE OLUŞTURMA VE DÜZENLEME (TABLO GÖRÜNÜMÜ REZİVONUYLA BİRLİKTE)
# ==========================================
elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Ürün Reçetesi (BOM) Yönetim İstasyonu")
    operasyon_turu = st.radio("Yapmak İstediğiniz İşlem:", ["➕ Yeni Reçete Oluştur", "✏️ Mevcut Reçeteyi Gör ve Düzenle"])
    
    duzenlenecek_recete_adi, eski_bom, duzenleme_indeksi, r_adi_val, r_turu_idx = None, {}, None, "", 0
    
    if operasyon_turu == "✏️ Mevcut Reçeteyi Gör ve Düzenle" and st.session_state.receteler:
        recete_isimleri = [r["Reçete Adı"] for r in st.session_state.receteler]
        duzenlenecek_recete_adi = st.selectbox("🔍 Detaylarını Görmek ve Düzenlemek İstediğiniz Reçeteyi Seçin", recete_isimleri)
        duzenleme_indeksi = next(idx for idx, r in enumerate(st.session_state.receteler) if r["Reçete Adı"] == duzenlenecek_recete_adi)
        hedef_recete = st.session_state.receteler[duzenleme_indeksi]
        eski_bom, r_adi_val = hedef_recete["BOM"], hedef_recete["Reçete Adı"]
        r_turu_idx = 0 if hedef_recete["Tür"] == "Ara Mamul Reçetesi" else 1
        
        # --- YENİLENEN TABLO GÖRÜNÜMÜ ALGORİTMASI ---
        st.subheader("📋 Kayıtlı Mevcut Reçete Oranları Özet Görünümü")
        if eski_bom:
            rapor_satirlari = []
            for b_malz, b_oran in eski_bom.items():
                rapor_satirlari.append({
                    "Malzeme Adı": b_malz,
                    "Katsayı İhtiyaç Oranı": f"{b_oran:.6f}",
                    "Birim": malzeme_birimi_bul(b_malz)
                })
            st.dataframe(pd.DataFrame(rapor_satirlari), use_container_width=True)
        else:
            st.info("Bu reçetenin içeriği boş.")

    st.write("---")
    st.subheader("🛠️ Reçete Güncelleme ve BOM Giriş Paneli")
    r_adi_input = st.text_input("Reçete / Ürün Adı", value=r_adi_val)
    r_turu_input = st.selectbox("Reçete Sınıfı", ["Ara Mamul Reçetesi", "Mamul Reçetesi"], index=r_turu_idx)
    
    tab_ham, tab_kim, tab_amb, tab_ara = st.tabs(["🛠️ Hammaddeler", "🧪 Yardımcı Kimyasallar", "📦 Ambalaj", "⚙️ Ara Mamuller"])
    secilen_bom = {}
    
    with tab_ham:
        for k in st.session_state.stok_kartlari["Hammadde"]:
            val = st.number_input(f"{k['Ad']} İhtiyacı ({k['Birim']})", min_value=0.0, max_value=100.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"h_{k['Ad']}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_kim:
        for k in st.session_state.stok_kartlari["Yardımcı Kimyasal"]:
            val = st.number_input(f"{k['Ad']} İhtiyacı ({k['Birim']})", min_value=0.0, max_value=100.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"ki_{k['Ad']}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_amb:
        for k in st.session_state.stok_kartlari["Ambalaj"]:
            val = st.number_input(f"{k['Ad']} İhtiyacı ({k['Birim']})", min_value=0.0, max_value=100.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"am_{k['Ad']}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_ara:
        df_d = pd.DataFrame(st.session_state.hammadde_depo)
        stoktaki_ara = df_d[df_d["Kategori"] == "Ara Mamul"]["Hammadde"].unique().tolist() if not df_d.empty else []
        for am_ad in list(set([x["Ad"] for x in st.session_state.stok_kartlari["Ara Mamul"]] + stoktaki_ara)):
            val = st.number_input(f"{am_ad} İhtiyacı (Kg)", min_value=0.0, max_value=100.0, value=float(eski_bom.get(am_ad, 0.0)), step=0.000001, format="%.6f", key=f"ar_{am_ad}")
            if val > 0: secilen_bom[am_ad] = val

    if st.button("💾 Değişiklikleri Onayla ve Reçete Veritabanını Güncelle") and r_adi_input and secilen_bom:
        g_rec = {"Reçete Adı": r_adi_input, "Tür": r_turu_input, "BOM": secilen_bom}
        if operasyon_turu == "✏️ Mevcut Reçeteyi Gör ve Düzenle" and duzenleme_indeksi is not None: st.session_state.receteler[duzenleme_indeksi] = g_rec
        else: st.session_state.receteler.append(g_rec)
        st.success("✅ Reçete başarıyla işlendi!"); st.rerun()

# ==========================================
# SAYFA 3: ÜRETİM EMRİ & GİRİŞİ
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Yönetim ve Reaktör Besleme Arayüzü")
    u_kategori = st.radio("Yapılacak Üretim Sınıfı:", ["1) Ara Mamul Üretimi", "2) Mamul Üretimi"])
    hedef_tur = "Ara Mamul Reçetesi" if "1)" in u_kategori else "Mamul Reçetesi"
    uygun_receteler = [r for r in st.session_state.receteler if r.get("Tür") == hedef_tur]
    
    if uygun_receteler:
        stok_dict = segment_stok_getir()
        secilen_recete_adi = st.selectbox("Kullanılacak Reçeteyi Seçin", [r["Reçete Adı"] for r in uygun_receteler])
        hedef_miktar = st.number_input("Hedef Üretim Hacmi (Kg)", min_value=1.0, value=1000.0)
        u_lot = st.text_input("Üretim Parti / Silo LOT No", value=f"LOT-{datetime.now().strftime('%Y%m%d%H%M')}")
        secilen_recete = next(r for r in uygun_receteler if r["Reçete Adı"] == secilen_recete_adi)
        
        with st.form("uretim_form"):
            fiili_girisler = {}
            for h_adi, oran in secilen_recete["BOM"].items():
                teorik = hedef_miktar * oran
                fiili_girisler[h_adi] = st.number_input(f"{h_adi} Fiili Tüketim ({malzeme_birimi_bul(h_adi)})", min_value=0.0, value=float(teorik))
                
            if st.form_submit_button("Üretimi Onayla"):
                kontrol = True
                for h_adi, f_amt in fiili_girisler.items():
                    if stok_dict.get(h_adi, 0.0) < f_amt: kontrol = False
                if not kontrol: st.error("❌ Stok Yetersiz!")
                else:
                    current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    for h_adi, f_amt in fiili_girisler.items():
                        st.session_state.hammadde_kullanilan_toplam[h_adi] = st.session_state.hammadde_kullanilan_toplam.get(h_adi, 0.0) + f_amt
                        st.session_state.uretim_harcamalari_log.append({"Tarih": current_date_str, "Üretim LOT": u_lot, "Harcanan Malzeme": h_adi, "Miktar": f_amt, "Birim": malzeme_birimi_bul(h_adi)})
                    
                    if hedef_tur == "Ara Mamul Reçetesi":
                        st.session_state.hammadde_depo.append({"Giriş Tarihi": datetime.now().strftime("%Y-%m-%d"), "Kategori": "Ara Mamul", "Hammadde": secilen_recete_adi, "LOT No": u_lot, "Miktar": hedef_miktar, "Birim": "Kg"})
                    else:
                        st.session_state.mamul_depo.append({"Üretim Tarihi": current_date_str, "Ürün": secilen_recete_adi, "Üretim LOT / Silo": u_lot, "Miktar": hedef_miktar})
                    st.success("🎉 Üretim tamamlandı!"); st.rerun()
