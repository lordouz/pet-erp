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
            {"Ad": "PTA", "Birim": "Kg"}, {"Ad": "IPA", "Birim": "Kg"},
            {"Ad": "SAF MEG", "Birim": "Kg"}, {"Ad": "YERLİ FLAKE", "Birim": "Kg"},
            {"Ad": "İTHAL FLAKE", "Birim": "Kg"}, {"Ad": "K2 ERİTMELİK", "Birim": "Kg"},
            {"Ad": "DEŞE KIRIĞI", "Birim": "Kg"}, {"Ad": "KİRLİ MEG", "Birim": "Kg"}
        ],
        "Yardımcı Kimyasal": [
            {"Ad": "SAF DEG", "Birim": "Kg"}, {"Ad": "ANTİMON TRİOKSİT", "Birim": "Kg"}, 
            {"Ad": "FOSFORİK ASİT", "Birim": "Kg"}, {"Ad": "KIRMIZI BOYA", "Birim": "Kg"}, 
            {"Ad": "MAVİ BOYA", "Birim": "Kg"}, {"Ad": "REHEAT", "Birim": "Kg"}, 
            {"Ad": "TYZOR AC 422", "Birim": "Kg"}, {"Ad": "TALK", "Birim": "Kg"}
        ],
        "Ambalaj": [
            {"Ad": "1150 kg Virgin ürün BİG-BEG (Beyaz Kulak)", "Birim": "Adet"},
            {"Ad": "1100 kg Virgin ürün BİG-BEG (Beyaz Kulak)", "Birim": "Adet"},
            {"Ad": "1150 kg Baskısız MAVİ Kulak BİG-BEG", "Birim": "Adet"},
            {"Ad": "1150 kg Baskısız BEYAZ Kulak BİG-BEG", "Birim": "Adet"},
            {"Ad": "1150 kg İç astarlı r-PET BİG-BEG (Yeşil Kulak)", "Birim": "Adet"},
            {"Ad": "1100 kg r-PET BİG-BEG (Yeşil Kulak)", "Birim": "Adet"},
            {"Ad": "1150 kg r-PET BİG-BEG (Yeşil Kulak)", "Birim": "Adet"},
            {"Ad": "1100 Yeşil Kulak Virgin baskılı", "Birim": "Adet"},
            {"Ad": "Yurtiçi Standart Palet", "Birim": "Adet"},
            {"Ad": "Konteyner İhracat Paleti", "Birim": "Adet"},
            {"Ad": "Karton Seperatör", "Birim": "Adet"}
        ],
        "Ara Mamul": [
            {"Ad": "Standart Amorf Chips", "Birim": "Kg"}, {"Ad": "HTM", "Birim": "Kg"}
        ],
        "Enerji ve Sarfiyat": [
            {"Ad": "LPG", "Birim": "Kg"}, {"Ad": "MOTORİN", "Birim": "lt"}
        ]
    }
# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        {"Giriş Tarihi": "2026-08-15", "Depo": "Depo 1", "Kategori": "Hammadde", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar": 100000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Depo": "Depo 2", "Kategori": "Hammadde", "Hammadde": "SAF MEG", "LOT No": "MEG-LOT-001", "Miktar": 50000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Depo": "Depo 1", "Kategori": "Yardımcı Kimyasal", "Hammadde": "ANTİMON TRİOKSİT", "LOT No": "ANT-LOT-001", "Miktar": 5000.0, "Birim": "Kg"},
        {"Giriş Tarihi": "2026-08-15", "Depo": "Depo 3", "Kategori": "Ambalaj", "Hammadde": "1150 kg Virgin ürün BİG-BEG (Beyaz Kulak)", "LOT No": "BB-LOT-01", "Miktar": 500.0, "Birim": "Adet"},
        {"Giriş Tarihi": "2026-08-15", "Depo": "Depo 2", "Kategori": "Ara Mamul", "Hammadde": "Standart Amorf Chips", "LOT No": "AMF-LOT-00", "Miktar": 10000.0, "Birim": "Kg"}
    ]

if 'hammadde_kullanilan_toplam' not in st.session_state:
    st.session_state.hammadde_kullanilan_toplam = {}

if 'receteler' not in st.session_state:
    st.session_state.receteler = [
        {"Reçete Adı": "Standart Amorf Chips (Reaktör)", "Tür": "Ara Mamul Reçetesi", "BOM": {"PTA": 0.850000, "SAF MEG": 0.135000, "ANTİMON TRİOKSİT": 0.005000}}
    ]

if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

if 'sevkiyat_depo' not in st.session_state:
    st.session_state.sevkiyat_depo = []

if 'uretim_harcamalari_log' not in st.session_state:
    st.session_state.uretim_harcamalari_log = []

if 'transfer_log' not in st.session_state:
    st.session_state.transfer_log = []

if 'manuel_dusum_log' not in st.session_state:
    st.session_state.manuel_dusum_log = []

# Yeni Eklenen Üretim Emirleri İzleme Hafızası
if 'uretim_emirleri' not in st.session_state:
    st.session_state.uretim_emirleri = []
def malzeme_birimi_bul(malzeme_adi):
    for kat, kalemler in st.session_state.stok_kartlari.items():
        for k in kalemler:
            if k["Ad"] == malzeme_adi: return k["Birim"]
    return "Kg"

def malzeme_depo_stok_getir(malzeme_adi, depo_adi):
    df = pd.DataFrame(st.session_state.hammadde_depo)
    if df.empty: return 0.0
    filtre = df[(df["Hammadde"] == malzeme_adi) & (df["Depo"] == depo_adi)]
    giren_toplam = filtre["Miktar"].sum() if not filtre.empty else 0.0
    anahtar = f"{malzeme_adi}_{depo_adi}"
    harcanan_toplam = st.session_state.hammadde_kullanilan_toplam.get(anahtar, 0.0)
    return max(0.0, giren_toplam - harcanan_toplam)

def endustriyel_excel_rapor_olustur(bas_tarih, bit_tarih):
    df_depo = pd.DataFrame(st.session_state.hammadde_depo) if st.session_state.hammadde_depo else pd.DataFrame(columns=["Giriş Tarihi", "Depo", "Kategori", "Hammadde", "LOT No", "Miktar", "Birim"])
    df_harcama = pd.DataFrame(st.session_state.uretim_harcamalari_log) if st.session_state.uretim_harcamalari_log else pd.DataFrame(columns=["Tarih", "Harcanan Depo", "Üretim LOT", "Harcanan Malzeme", "Miktar", "Birim"])
    df_mamul = pd.DataFrame(st.session_state.mamul_depo) if st.session_state.mamul_depo else pd.DataFrame(columns=["Üretim Tarihi", "Ürün", "Üretim LOT / Silo", "Miktar"])
    df_sevk = pd.DataFrame(st.session_state.sevkiyat_depo) if st.session_state.sevkiyat_depo else pd.DataFrame(columns=["Sevkiyat Tarihi", "Müşteri", "İrsaliye No", "Plaka", "Ürün", "Sevk Edilen LOT", "Sevk Miktarı (Kg)"])
    df_trans = pd.DataFrame(st.session_state.transfer_log) if st.session_state.transfer_log else pd.DataFrame(columns=["Tarih", "Malzeme", "Kaynak Depo", "Hedef Depo", "Miktar", "Birim"])
    df_man_dus = pd.DataFrame(st.session_state.manuel_dusum_log) if st.session_state.manuel_dusum_log else pd.DataFrame(columns=["Tarih", "Depo", "Malzeme", "Miktar", "Neden / Fire Tipi"])
    
    def tarih_filtrele(df, tarih_kolonu):
        if df.empty or tarih_kolonu not in df.columns: return df
        df_copy = df.copy()
        try:
            df_copy["temp_date"] = pd.to_datetime(df_copy[tarih_kolonu].astype(str).str.slice(0, 10), errors='coerce').dt.date
            filtered_df = df_copy[(df_copy["temp_date"] >= bas_tarih) & (df_copy["temp_date"] <= bit_tarih)]
            return filtered_df.drop(columns=["temp_date"])
        except Exception: return df

    f_depo_giris = tarih_filtrele(df_depo, "Giriş Tarihi")
    f_uretim_harcama = tarih_filtrele(df_harcama, "Tarih")
    f_mamul_depo = tarih_filtrele(df_mamul, "Üretim Tarihi")
    f_sevk_hareket = tarih_filtrele(df_sevk, "Sevkiyat Tarihi")
    f_trans_hareket = tarih_filtrele(df_trans, "Tarih")
    f_man_dus_hareket = tarih_filtrele(df_man_dus, "Tarih")
    
    bakiye_satirlari = []
    df_m_kontrol = pd.DataFrame(st.session_state.hammadde_depo)
    tum_malzemeler = df_m_kontrol["Hammadde"].unique().tolist() if not df_m_kontrol.empty else []
    for m in tum_malzemeler:
        d1 = h1 if (h1 := malzeme_depo_stok_getir(m, "Depo 1")) else 0.0
        d2 = h2 if (h2 := malzeme_depo_stok_getir(m, "Depo 2")) else 0.0
        d3 = h3 if (h3 := malzeme_depo_stok_getir(m, "Depo 3")) else 0.0
        bakiye_satirlari.append({
            "Malzeme / Ürün Adı": m, "Depo 1 Stok": d1, "Depo 2 Stok": d2, "Depo 3 Stok": d3,
            "Toplam Fabrika Stoğu": (d1 + d2 + d3), "Ölçü Birimi": malzeme_birimi_bul(m)
        })
    df_anlik_bakiye = pd.DataFrame(bakiye_satirlari) if bakiye_satirlari else pd.DataFrame(columns=["Malzeme / Ürün Adı", "Depo 1 Stok", "Depo 2 Stok", "Depo 3 Stok", "Toplam Fabrika Stoğu", "Ölçü Birimi"])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_anlik_bakiye.to_excel(writer, index=False, sheet_name='Anlık Depolar Özet Matris')
        f_depo_giris.to_excel(writer, index=False, sheet_name='Giriş Hareketleri Detay')
        f_uretim_harcama.to_excel(writer, index=False, sheet_name='Üretim Sarfiyat Detay')
        f_mamul_depo.to_excel(writer, index=False, sheet_name='Mamul Üretim Çıktı Detay')
        f_sevk_hareket.to_excel(writer, index=False, sheet_name='Müşteri Sevkiyat Detay')
        f_trans_hareket.to_excel(writer, index=False, sheet_name='Dahili Depo Transferleri')
        f_man_dus_hareket.to_excel(writer, index=False, sheet_name='Manuel Fire ve Düşümler')
                
    return buffer.getvalue()
# 3. YAN PANEL MENÜ SİSTEMİ
st.sidebar.title("🧪 PET Resin ERP v2.6")
st.sidebar.write("---")
sayfa = st.sidebar.radio("Gitmek İstediğiniz Sayfa:", [
    "📊 Genel Depo & Stok Durumu",
    "📈 📊 Fabrika Raporlar Sayfası",
    "🗂️ 0. Stok Kartı Tanımlama Sayfası",
    "📥 1. Hammadde Giriş Sayfası",
    "📉 1-B. Manuel Stoktan Düşüm Sayfası",
    "🔄 1-C. Depolar Arası Stok Aktarımı",
    "📝 2. Reçete Oluşturma Sayfası",
    "🏭 3. Üretim Emri & Takip İstasyonu",
    "🚚 4. Müşteri Sevkiyat Sayfası"
])

# ==========================================
# SAYFA: GENEL DEPO VE STOK DURUMU
# ==========================================
if sayfa == "📊 Genel Depo & Stok Durumu":
    st.header("📊 Fabrika Çoklu Depo Yönetim Kokpiti")
    st.info("💡 Depoların anlık durumlarını görmek için ilgili kategorileri açınız.")
    
    df_merkez = pd.DataFrame(st.session_state.hammadde_depo)
    kat_rehber = df_merkez.set_index("Hammadde")["Kategori"].to_dict() if not df_merkez.empty else {}
    tum_mevcut_malzemeler = df_merkez["Hammadde"].unique().tolist() if not df_merkez.empty else []

    for idx, kat_isim in enumerate(["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul", "Enerji ve Sarfiyat"]):
        with st.expander(f"📦 {idx+1}) {kat_isim.upper()} DEPOLARI DETAYLARI"):
            for h in tum_mevcut_malzemeler:
                if kat_rehber.get(h) == kat_isim:
                    st.markdown(f"**🔹 {h} Detay Matrisi ({malzeme_birimi_bul(h)}):**")
                    c1, c2, c3, c4 = st.columns(4)
                    d1, d2, d3 = malzeme_depo_stok_getir(h, "Depo 1"), malzeme_depo_stok_getir(h, "Depo 2"), malzeme_depo_stok_getir(h, "Depo 3")
                    c1.metric("Depo 1", f"{d1:,.1f}"); c2.metric("Depo 2", f"{d2:,.1f}"); c3.metric("Depo 3", f"{d3:,.1f}"); c4.metric("Küm. Toplam", f"{(d1+d2+d3):,.1f}")

    with st.expander("🏭 6) ÜRÜN BAZLI SATIŞA HAZIR MAMUL DEPOSU"):
        if st.session_state.mamul_depo:
            df_mamul = pd.DataFrame(st.session_state.mamul_depo)
            df_sevk_matris = pd.DataFrame(st.session_state.sevkiyat_depo) if st.session_state.sevkiyat_depo else pd.DataFrame(columns=["Ürün", "Sevk Edilen LOT", "Sevk Miktarı (Kg)"])
            for urun_adi, urun_data in df_mamul.groupby("Ürün"):
                toplam_sevk_edilen = df_sevk_matris[df_sevk_matris["Ürün"] == urun_adi]["Sevk Miktarı (Kg)"].sum() if not df_sevk_matris.empty else 0.0
                kalan_net_mamul = max(0.0, urun_data["Miktar"].sum() - toplam_sevk_edilen)
                st.write(f"**🔹 {urun_adi}** | Kalan Satış Stoğu: **{kalan_net_mamul:,.1f} Kg**")
                lot_satirlari = []
                for lot_no, lot_data in urun_data.groupby("Üretim LOT / Silo"):
                    l_uretim = lot_data["Miktar"].sum()
                    l_sevk = df_sevk_matris[(df_sevk_matris["Ürün"] == urun_adi) & (df_sevk_matris["Sevk Edilen LOT"] == lot_no)]["Sevk Miktarı (Kg)"].sum() if not df_sevk_matris.empty else 0.0
                    lot_satirlari.append({"Üretim LOT / Silo": lot_no, "Üretilen (Kg)": l_uretim, "Sevk Edilen (Kg)": l_sevk, "Kalan Stok (Kg)": max(0.0, l_uretim - l_sevk)})
                st.dataframe(pd.DataFrame(lot_satirlari), use_container_width=True)

elif sayfa == "📈 📊 Fabrika Raporlar Sayfası":
    st.header("📈 📊 Dönemsel Fabrika Profesyonel Rapor İstasyonu")
    c_t1, c_t2 = st.columns(2)
    bas_secim = c_t1.date_input("Analiz Başlangıç Tarihi", value=date(2026, 1, 1))
    bit_secim = c_t2.date_input("Analiz Bitiş Tarihi", value=date(2026, 12, 31))
    if bas_secim <= bit_secim:
        excel_dosyası = endustriyel_excel_rapor_olustur(bas_secim, bit_secim)
        st.download_button(label="📊 Kurumsal Excel Raporunu İndir (.XLSX)", data=excel_dosyası, file_name=f"Fabrika_Kurumsal_Rapor_{bas_secim}_to_{bit_secim}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
# ==========================================
# SAYFA 0: STOK KARTI TANIMLAMA & YÖNETİMİ
# ==========================================
elif sayfa == "🗂️ 0. Stok Kartı Tanımlama Sayfası":
    st.header("🗂️ Fabrika Malzeme / Stok Kartı Yönetim İstasyonu")
    tab_ekle, tab_yonet = st.tabs(["➕ Yeni Stok Kartı Ekle", "✏️ / ❌ Mevcut Kartları Düzenle & Sil"])
    
    with tab_ekle:
        with st.form("stok_kart_form"):
            k_kat = st.selectbox("Kartın Bağlanacağı Kategori", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul", "Enerji ve Sarfiyat"])
            k_adi = st.text_input("Yeni Malzeme / Stok Kartı Adı")
            k_birim = st.selectbox("Miktar Ölçü Birimi", ["Kg", "Adet", "Ton", "lt"])
            if st.form_submit_button("Yeni Stok Kartını Kaydet") and k_adi:
                st.session_state.stok_kartlari[k_kat].append({"Ad": k_adi, "Birim": k_birim})
                st.success(f"✅ '{k_adi}' kartı eklendi."); st.rerun()
                
    with tab_yonet:
        st.subheader("🛠️ Kart Düzenleme ve Silme Paneli")
        kat_sec = st.selectbox("Kategori Seçin", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul", "Enerji ve Sarfiyat"], key="kat_sec_duz")
        kart_listesi = st.session_state.stok_kartlari.get(kat_sec, [])
        if kart_listesi:
            kart_adlari = [x["Ad"] for x in kart_listesi]
            secilen_kart_ad = st.selectbox("Düzenlenecek / Silinecek Kart", kart_adlari)
            kart_idx = next(i for idx, i in enumerate(range(len(kart_listesi))) if kart_listesi[i]["Ad"] == secilen_kart_ad)
            
            c_d1, c_d2 = st.columns(2)
            yeni_ad = c_d1.text_input("Yeni Adı", value=kart_listesi[kart_idx]["Ad"])
            yeni_birim = c_d2.selectbox("Yeni Birimi", ["Kg", "Adet", "Ton", "lt"], index=["Kg", "Adet", "Ton", "lt"].index(kart_listesi[kart_idx]["Birim"]))
            
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("💾 Değişiklikleri Güncelle"):
                st.session_state.stok_kartlari[kat_sec][kart_idx] = {"Ad": yeni_ad, "Birim": yeni_birim}
                st.success("Kart başarıyla güncellendi!"); st.rerun()
            if col_b2.button("❌ Stok Kartını Sistemden Tamamen Sil"):
                st.session_state.stok_kartlari[kat_sec].pop(kart_idx)
                st.warning("Stok kartı başarıyla sistemden silindi!"); st.rerun()
        else: st.info("Bu kategoride kayıtlı kart bulunmuyor.")

elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Fabrika Depolarına Giriş Kabul Ekranı")
    kat_turu = st.selectbox("Malzeme Kategorisi Seçin", ["Hammadde", "Yardımcı Kimyasal", "Ambalaj", "Ara Mamul", "Enerji ve Sarfiyat"])
    uygun_malzemeler = [x["Ad"] for x in st.session_state.stok_kartlari.get(kat_turu, [])]
    if uygun_malzemeler:
        with st.form("hammadde_form"):
            g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
            hedef_depo_secim = st.selectbox("Malzemenin İndirileceği Fiziksel Depo", ["Depo 1", "Depo 2", "Depo 3"])
            h_turu = st.selectbox("Malzeme / Kalem Adı", uygun_malzemeler)
            h_lot = st.text_input("Gelen LOT / Parti Numarası")
            h_miktar = st.number_input(f"Gelen Miktar ({malzeme_birimi_bul(h_turu)})", min_value=0.1, step=50.0)
            if st.form_submit_button("Malzemeyi Depoya Kabul Et") and h_lot:
                st.session_state.hammadde_depo.append({"Giriş Tarihi": str(g_tarih), "Depo": hedef_depo_secim, "Kategori": kat_turu, "Hammadde": h_turu, "LOT No": h_lot, "Miktar": h_miktar, "Birim": malzeme_birimi_bul(h_turu)})
                st.success("✅ Malzeme depoya alındı."); st.rerun()
elif sayfa == "📉 1-B. Manuel Stoktan Düşüm Sayfası":
    st.header("📉 Depolardan Manuel Stok Düşüm ve Fire Giriş Ekranı")
    df_d = pd.DataFrame(st.session_state.hammadde_depo)
    aktif_malz = df_d["Hammadde"].unique().tolist() if not df_d.empty else []
    if aktif_malz:
        m_sec = st.selectbox("Stoktan Düşülecek Malzemeyi Seçin", aktif_malz)
        depo_sec = st.selectbox("Hangi Depodan Düşülecek?", ["Depo 1", "Depo 2", "Depo 3"])
        current_bakiye = malzeme_depo_stok_getir(m_sec, depo_sec)
        st.info(f"💡 Seçilen {m_sec} malzemesinin {depo_sec} alanındaki güncel bakiyesi: **{current_bakiye:,.1f} {malzeme_birimi_bul(m_sec)}**")
        with st.form("manuel_dus_form"):
            dus_miktar = st.number_input("Düşülecek Fire / Sarfiyat Miktarı", min_value=0.1, value=float(min(10.0, current_bakiye)))
            neden_metni = st.selectbox("Düşüm / Fire Nedeni", ["Kullanım Süresi Dolması", "Saha Firesi / Dökülme", "Laboratuvar Analiz Sarfiyatı", "Düzeltme Fişi"])
            if st.form_submit_button("Stoktan Manuel Düşümü Onayla"):
                if dus_miktar > current_bakiye: st.error("❌ Kalan stoktan fazla düşüm yapılamaz!")
                else:
                    st.session_state.hammadde_kullanilan_toplam[f"{m_sec}_{depo_sec}"] = st.session_state.hammadde_kullanilan_toplam.get(f"{m_sec}_{depo_sec}", 0.0) + dus_miktar
                    st.session_state.manuel_dusum_log.append({"Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Depo": depo_sec, "Malzeme": m_sec, "Miktar": dus_miktar, "Neden / Fire Tipi": neden_metni})
                    st.success("📉 Stok düşümü başarıyla kaydedildi!"); st.rerun()

elif sayfa == "🔄 1-C. Depolar Arası Stok Aktarımı":
    st.header("🔄 Depolar Arası Dahili Malzeme Aktarım Fişi (Forklift / Lojistik)")
    df_d = pd.DataFrame(st.session_state.hammadde_depo)
    aktif_malz = df_d["Hammadde"].unique().tolist() if not df_d.empty else []
    if aktif_malz:
        trans_malz = st.selectbox("Sevk Edilecek Malzemeyi Seçin", aktif_malz)
        k_depo = st.selectbox("Kaynak Depo (Çıkış)", ["Depo 1", "Depo 2", "Depo 3"])
        h_depo = st.selectbox("Hedef Depo (Giriş)", ["Depo 1", "Depo 2", "Depo 3"])
        current_bakiye = malzeme_depo_stok_getir(trans_malz, k_depo)
        st.info(f"💡 {trans_malz} malzemesinin {k_depo} taşınabilir bakiyesi: **{current_bakiye:,.1f} {malzeme_birimi_bul(trans_malz)}**")
        with st.form("transfer_form"):
            trans_miktar = st.number_input("Sevk Edilecek Miktar", min_value=0.1, value=float(min(50.0, current_bakiye)))
            if st.form_submit_button("Depolar Arası Sevkiyatı Başlat"):
                if k_depo == h_depo: st.error("❌ Kaynak ve hedef depo aynı olamaz!")
                elif trans_miktar > current_bakiye: st.error("❌ Kaynak depoda yeterli stok yok!")
                else:
                    st.session_state.hammadde_kullanilan_toplam[f"{trans_malz}_{k_depo}"] = st.session_state.hammadde_kullanilan_toplam.get(f"{trans_malz}_{k_depo}", 0.0) + trans_miktar
                    st.session_state.hammadde_depo.append({"Giriş Tarihi": datetime.now().strftime("%Y-%m-%d"), "Depo": h_depo, "Kategori": "Hammadde", "Hammadde": trans_malz, "LOT No": "TRF-LOT", "Miktar": trans_miktar, "Birim": malzeme_birimi_bul(trans_malz)})
                    st.session_state.transfer_log.append({"Tarih": datetime.now().strftime("%Y-%m-%d %H:%M"), "Malzeme": trans_malz, "Kaynak Depo": k_depo, "Hedef Depo": h_depo, "Miktar": trans_miktar, "Birim": malzeme_birimi_bul(trans_malz)})
                    st.success(f"🎉 Malzeme başarıyla transfer edildi!"); st.rerun()

elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Ürün Reçetesi (BOM) Yönetim İstasyonu")
    operasyon_turu = st.radio("Yapmak İstediğiniz İşlem:", ["➕ Yeni Reçete Oluştur", "✏️ Mevcut Reçeteyi Gör ve Düzenle"])
    duzenlenecek_recete_adi, eski_bom, duzenleme_indeksi, r_adi_val, r_turu_idx = None, {}, None, "", 0
    if operasyon_turu == "✏️ Mevcut Reçeteyi Gör ve Düzenle" and st.session_state.receteler:
        recete_isimleri = [r["Reçete Adı"] for r in st.session_state.receteler]
        duzenlemek_istediğiniz_recete_adi = st.selectbox("🔍 Düzenlemek İstediğiniz Reçeteyi Seçin", recete_isimleri)
        duzenleme_indeksi = next(idx for idx, r in enumerate(st.session_state.receteler) if r["Reçete Adı"] == duzenlemek_istediğiniz_recete_adi)
        eski_bom, r_adi_val = st.session_state.receteler[duzenleme_indeksi]["BOM"], st.session_state.receteler[duzenleme_indeksi]["Reçete Adı"]
        r_turu_idx = 0 if st.session_state.receteler[duzenleme_indeksi]["Tür"] == "Ara Mamul Reçetesi" else 1
    r_adi_input = st.text_input("Reçete / Ürün Adı", value=r_adi_val)
    r_turu_input = st.selectbox("Reçete Sınıfı", ["Ara Mamul Reçetesi", "Mamul Reçetesi"], index=r_turu_idx)
    
    tab_ham, tab_kim, tab_amb, tab_ara, tab_enr = st.tabs(["🛠️ Hammaddeler", "🧪 Yardımcı Kimyasallar", "📦 Ambalaj", "⚙️ Ara Mamuller", "⚡ Enerji & Sarfiyat"])
    secilen_bom = {}
    with tab_ham:
        for k in st.session_state.stok_kartlari["Hammadde"]:
            val = st.number_input(f"{k['Ad']} ({k['Birim']})", min_value=0.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"h_{k['Ad']}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_kim:
        for k in st.session_state.stok_kartlari["Yardımcı Kimyasal"]:
            val = st.number_input(f"{k['Ad']} ({k['Birim']})", min_value=0.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"ki_{k['Ad']}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_amb:
        for k in st.session_state.stok_kartlari["Ambalaj"]:
            safe_key = str(k['Ad']).replace(" ", "").replace("(", "").replace(")", "").replace(";", "")
            val = st.number_input(f"{k['Ad']} ({k['Birim']})", min_value=0.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"am_{safe_key}")
            if val > 0: secilen_bom[k['Ad']] = val
    with tab_ara:
        df_d = pd.DataFrame(st.session_state.hammadde_depo)
        stoktaki_ara = df_d[df_d["Kategori"] == "Ara Mamul"]["Hammadde"].unique().tolist() if not df_d.empty else []
        for am_ad in list(set([x["Ad"] for x in st.session_state.stok_kartlari["Ara Mamul"]] + stoktaki_ara)):
            val = st.number_input(f"{am_ad} (Kg)", min_value=0.0, value=float(eski_bom.get(am_ad, 0.0)), step=0.000001, format="%.6f", key=f"ar_{am_ad.replace(' ', '')}")
            if val > 0: secilen_bom[am_ad] = val
    with tab_enr:
        for k in st.session_state.stok_kartlari["Enerji ve Sarfiyat"]:
            val = st.number_input(f"{k['Ad']} ({k['Birim']})", min_value=0.0, value=float(eski_bom.get(k['Ad'], 0.0)), step=0.000001, format="%.6f", key=f"en_{k['Ad'].replace(' ', '')}")
            if val > 0: secilen_bom[k['Ad']] = val

    if st.button("💾 Reçeteyi Kaydet") and r_adi_input and secilen_bom:
        g_rec = {"Reçete Adı": r_adi_input, "Tür": r_turu_input, "BOM": secilen_bom}
        if operasyon_turu == "✏️ Mevcut Reçeteyi Gör ve Düzenle" and duzenleme_indeksi is not None: st.session_state.receteler[duzenleme_indeksi] = g_rec
        else: st.session_state.receteler.append(g_rec)
        st.success("✅ Ürün Reçetesi Başarıyla Kaydedildi!"); st.rerun()
# ==========================================
# SAYFA 3: ÜRETİM EMRİ & TAKİP İSTASYONU (İPTAL ETME ÖZELLİĞİ EKLENDİ)
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Takip İstasyonu":
    st.header("🏭 Üretim Emri Yönetimi ve Canlı Takip İstasyonu")
    
    t_ekle, t_takip = st.tabs(["🏭 Yeni Üretim Emri Ver", "📋 Canlı Emir Takip & İptal Paneli"])
    
    with t_ekle:
        u_kategori = st.radio("Üretim Sınıfı:", ["1) Ara Mamul Üretimi", "2) Mamul Üretimi"])
        hedef_tur = "Ara Mamul Reçetesi" if "1)" in u_kategori else "Mamul Reçetesi"
        uygun_receteler = [r for r in st.session_state.receteler if r.get("Tür") == hedef_tur]
        
        if uygun_receteler:
            secilen_recete_adi = st.selectbox("Reçete Seçin", [r["Reçete Adı"] for r in uygun_receteler])
            hedef_miktar = st.number_input("Hedef Üretim Hacmi (Kg)", min_value=1.0, value=1000.0)
            u_lot = st.text_input("Üretim LOT No", value=f"LOT-{datetime.now().strftime('%Y%m%d%H%M')}")
            kaynak_depo_secim = st.selectbox("🚀 Tüketilecek Kaynak Depo", ["Depo 1", "Depo 2", "Depo 3"])
            secilen_recete = next(r for r in uygun_receteler if r["Reçete Adı"] == secilen_recete_adi)
            
            with st.form("uretim_form"):
                fiili_girisler = {}
                for h_adi, oran in secilen_recete["BOM"].items():
                    m_stok = malzeme_depo_stok_getir(h_adi, kaynak_depo_secim)
                    fiili_girisler[h_adi] = st.number_input(f"{h_adi} Fiili Tüketim [Mevcut: {m_stok:,.1f}]", min_value=0.0, value=float(hedef_miktar * oran))
                
                if st.form_submit_button("Üretimi Başlat ve Kaydet"):
                    kontrol = True
                    for h_adi, f_amt in fiili_girisler.items():
                        if malzeme_depo_stok_getir(h_adi, kaynak_depo_secim) < f_amt: kontrol = False
                    if not kontrol: st.error("❌ Kaynak depoda yeterli hammadde stoğu yok!")
                    else:
                        current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        # Hammaddeleri depodan düş
                        for h_adi, f_amt in fiili_girisler.items():
                            st.session_state.hammadde_kullanilan_toplam[f"{h_adi}_{kaynak_depo_secim}"] = st.session_state.hammadde_kullanilan_toplam.get(f"{h_adi}_{kaynak_depo_secim}", 0.0) + f_amt
                            st.session_state.uretim_harcamalari_log.append({"Tarih": current_date_str, "Harcanan Depo": kaynak_depo_secim, "Üretim LOT": u_lot, "Harcanan Malzeme": h_adi, "Miktar": f_amt, "Birim": malzeme_birimi_bul(h_adi)})
                        
                        # Üretilen mamulü depoya ekle
                        if hedef_tur == "Ara Mamul Reçetesi":
                            st.session_state.hammadde_depo.append({"Giriş Tarihi": datetime.now().strftime("%Y-%m-%d"), "Depo": kaynak_depo_secim, "Kategori": "Ara Mamul", "Hammadde": secilen_recete_adi, "LOT No": u_lot, "Miktar": hedef_miktar, "Birim": "Kg"})
                        else:
                            st.session_state.mamul_depo.append({"Üretim Tarihi": current_date_str, "Ürün": secilen_recete_adi, "Üretim LOT / Silo": u_lot, "Miktar": hedef_miktar})
                        
                        # Emri takip listesine kaydet
                        st.session_state.uretim_emirleri.append({
                            "Tarih": current_date_str, "LOT No": u_lot, "Ürün/Reçete": secilen_recete_adi, "Miktar (Kg)": hedef_miktar, "Depo": kaynak_depo_secim, "Tüketim Detay": fiili_girisler, "Tür": hedef_tur, "Durum": "Tamamlandı"
                        })
                        st.success(f"🎉 {u_lot} numaralı üretim emri başarıyla işlendi."); st.rerun()
        else: st.info("Sistemde henüz reçete tanımlanmamış.")

    with t_takip:
        st.subheader("📋 Aktif ve Geçmiş Üretim Emirleri Listesi")
        if not st.session_state.uretim_emirleri:
            st.info("Kayıtlı üretim emri bulunmuyor.")
        else:
            for idx, emir in enumerate(st.session_state.uretim_emirleri):
                c_e1, c_e2, c_e3, c_e4 = st.columns([2, 3, 2, 2])
                c_e1.write(f"**Tarih:** {emir['Tarih']} | **LOT:** `{emir['LOT No']}`")
                c_e2.write(f"**Ürün:** {emir['Ürün/Reçete']} | **Hacim:** {emir['Miktar (Kg)']:,.1f} Kg")
                c_e3.write(f"**Depo:** {emir['Depo']} | **Durum:** `{emir['Durum']}`")
                
                if emir['Durum'] == "Tamamlandı":
                    if c_e4.button(f"❌ Emri İptal Et", key=f"iptal_{emir['LOT No']}_{idx}"):
                        # 1. Hammaddeleri Depoya Geri İade Et (Kullanılan toplamdan miktar düş)
                        for h_adi, f_amt in emir['Tüketim Detay'].items():
                            st.session_state.hammadde_kullanilan_toplam[f"{h_adi}_{emir['Depo']}"] -= f_amt
                        
                        # 2. Üretilen Mamulü Depo Hafızasından Temizle
                        if emir['Tür'] == "Ara Mamul Reçetesi":
                            st.session_state.hammadde_depo = [x for x in st.session_state.hammadde_depo if x.get("LOT No") != emir['LOT No']]
                        else:
                            st.session_state.mamul_depo = [x for x in st.session_state.mamul_depo if x.get("Üretim LOT / Silo") != emir['LOT No']]
                        
                        # 3. İlgili Sarfiyat Loglarını Temizle
                        st.session_state.uretim_harcamalari_log = [x for x in st.session_state.uretim_harcamalari_log if x.get("Üretim LOT") != emir['LOT No']]
                        
                        # 4. Durumu Güncelle
                        st.session_state.uretim_emirleri[idx]['Durum'] = "İPTAL EDİLDİ"
                        st.warning(f"⚠️ {emir['LOT No']} numaralı üretim emri iptal edildi, hammaddeler {emir['Depo']}'a iade edildi!"); st.rerun()
                else:
                    c_e4.write("➖ *İşlem Yapılamaz*")
                st.write("---")

elif sayfa == "🚚 4. Müşteri Sevkiyat Sayfası":
    st.header("🚚 Müşteri Mamul Sevkiyat İstasyonu")
    if not st.session_state.mamul_depo: st.warning("⚠️ Sevkiyat yapabilmek için mamul deposunda ürün bulunmalıdır.")
    else:
        df_mamul = pd.DataFrame(st.session_state.mamul_depo)
        df_sevk_matris = pd.DataFrame(st.session_state.sevkiyat_depo) if st.session_state.sevkiyat_depo else pd.DataFrame(columns=["Ürün", "Sevk Edilen LOT", "Sevk Miktarı (Kg)"])
        secilen_sevk_urun = st.selectbox("Sevk Edilecek Mamul Ürün", df_mamul["Ürün"].unique().tolist())
        secilen_sevk_lot = st.selectbox("Sevk Edilecek Üretim LOT / Silo", df_mamul[df_mamul["Ürün"] == secilen_sevk_urun]["Üretim LOT / Silo"].unique().tolist())
        l_toplam_uretim = df_mamul[(df_mamul["Ürün"] == secilen_sevk_urun) & (df_mamul["Üretim LOT / Silo"] == secilen_sevk_lot)]["Miktar"].sum()
        l_toplam_sevk = df_sevk_matris[(df_sevk_matris["Ürün"] == secilen_sevk_urun) & (df_sevk_matris["Sevk Edilen LOT"] == secilen_sevk_lot)]["Sevk Miktarı (Kg)"].sum() if not df_sevk_matris.empty else 0.0
        mevcut_lot_bakiyesi = max(0.0, l_toplam_uretim - l_toplam_sevk)
        st.info(f"💡 Kullanılabilir net bakiye: **{mevcut_lot_bakiyesi:,.1f} Kg**")
        with st.form("sevkiyat_form"):
            f_musteri, f_irsaliye = st.text_input("Müşteri Firma Adı"), st.text_input("İrsaliye Numarası")
            f_plaka, f_sevk_miktar = st.text_input("Nakliye Araç Plakası"), st.number_input("Sevk Edilecek Net Miktar (Kg)", min_value=1.0, value=float(min(1000.0, mevcut_lot_bakiyesi)))
            if st.form_submit_button("Sevkiyatı Onayla"):
                if not f_musteri or not f_irsaliye: st.error("❌ Eksik alan var!")
                elif f_sevk_miktar > mevcut_lot_bakiyesi: st.error("❌ Stok Yetersiz!")
                else:
                    st.session_state.sevkiyat_depo.append({"Sevkiyat Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"), "Müşteri": f_musteri, "İrsaliye No": f_irsaliye, "Plaka": f_plaka, "Ürün": secilen_sevk_urun, "Sevk Edilen LOT": secilen_sevk_lot, "Sevk Miktarı (Kg)": f_sevk_miktar})
                    st.success("🎉 Sevkiyat tamamlandı!"); st.rerun()
        if st.session_state.sevkiyat_depo: st.dataframe(pd.DataFrame(st.session_state.sevkiyat_depo), use_container_width=True)
