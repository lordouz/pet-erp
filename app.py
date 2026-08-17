import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. SAYFA VE TASARIM AYARLARI
st.set_page_config(page_title="PET Resin Komple ERP v2.6", layout="wide")

# 2. MERKEZİ VERİ TABANI SİMÜLASYONU
if 'hammadde_depo' not in st.session_state:
    st.session_state.hammadde_depo = [
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "PTA", "LOT No": "PTA-LOT-001", "Miktar (Kg)": 100000.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "MEG", "LOT No": "MEG-LOT-001", "Miktar (Kg)": 50000.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Antimon", "LOT No": "ANT-LOT-001", "Miktar (Kg)": 5000.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Fosforik Asit", "LOT No": "FOS-LOT-001", "Miktar (Kg)": 2000.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Mavi Boya", "LOT No": "BOY-M-001", "Miktar (Kg)": 500.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "Kırmızı Boya", "LOT No": "BOY-K-001", "Miktar (Kg)": 300.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "IPA", "LOT No": "IPA-LOT-001", "Miktar (Kg)": 1500.0},
        {"Giriş Tarihi": "2026-08-15", "Hammadde": "DEG", "LOT No": "DEG-LOT-001", "Miktar (Kg)": 4000.0}
    ]

if 'hammadde_giren_toplam' not in st.session_state:
    st.session_state.hammadde_giren_toplam = {
        "PTA": 100000.0, "MEG": 50000.0, "Antimon": 5000.0, "Fosforik Asit": 2000.0,
        "Mavi Boya": 500.0, "Kırmızı Boya": 300.0, "IPA": 1500.0, "DEG": 4000.0
    }

if 'hammadde_kullanilan_toplam' not in st.session_state:
    st.session_state.hammadde_kullanilan_toplam = {
        "PTA": 0.0, "MEG": 0.0, "Antimon": 0.0, "Fosforik Asit": 0.0,
        "Mavi Boya": 0.0, "Kırmızı Boya": 0.0, "IPA": 0.0, "DEG": 0.0
    }

if 'receteler' not in st.session_state:
    st.session_state.receteler = [
        {
            "Reçete Adı": "Şişelik PET Resin (IV 0.80) - Standart",
            "BOM (Kg/Kg)": {"PTA": 0.850, "MEG": 0.135, "Antimon": 0.005, "Fosforik Asit": 0.002, "Mavi Boya": 0.001, "Kırmızı Boya": 0.001, "IPA": 0.004, "DEG": 0.002}
        }
    ]

if 'mamul_depo' not in st.session_state:
    st.session_state.mamul_depo = []

# --- ANLIK STOK HESAPLAYICILAR ---
def toplam_hammadde_stok():
    df = pd.DataFrame(st.session_state.hammadde_depo)
    ham_listesi = ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"]
    
    if df.empty: 
        return {h: 0.0 for h in ham_listesi}
        
    grup_toplamlari = df.groupby("Hammadde")["Miktar (Kg)"].sum().to_dict()
    güncel_stok = {}
    
    for h in ham_listesi:
        giren = grup_toplamlari.get(h, 0.0)
        kullanilan = st.session_state.hammadde_kullanilan_toplam.get(h, 0.0)
        güncel_stok[h] = max(0.0, giren - kullanilan)
    return güncel_stok

def toplam_mamul_stok():
    df = pd.DataFrame(st.session_state.mamul_depo)
    if df.empty: return {}
    return df.groupby("Ürün")["Miktar (Kg)"].sum().to_dict()

# --- TEK PARÇA ÖZEL EXCEL RAPOR OLUŞTURUCU ---
def tek_rapor_excel_olustur():
    h_stok = toplam_hammadde_stok()
    m_stok = toplam_mamul_stok()
    
    satirlar = []
    ham_listesi = ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"]
    
    for h in ham_listesi:
        satirlar.append({
            "Malzeme Adı": h,
            "Giren Miktar (Kg)": st.session_state.hammadde_giren_toplam.get(h, 0.0),
            "Üretimde Kullanılan Miktar (Kg)": st.session_state.hammadde_kullanilan_toplam.get(h, 0.0),
            "Kalan Hammadde Stok (Kg)": h_stok.get(h, 0.0),
            "Sevkiyat (Kg)": 0.0,
            "Kalan Mamul Stok (Kg)": 0.0
        })
        
    for m_adi, m_miktar in m_stok.items():
        satirlar.append({
            "Malzeme Adı": m_adi,
            "Giren Miktar (Kg)": 0.0,
            "Üretimde Kullanılan Miktar (Kg)": 0.0,
            "Kalan Hammadde Stok (Kg)": 0.0,
            "Sevkiyat (Kg)": 0.0,
            "Kalan Mamul Stok (Kg)": m_miktar
        })
        
    df_rapor = pd.DataFrame(satirlar)
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_rapor.to_excel(writer, index=False, sheet_name='Fabrika Genel Stok Raporu')
    return buffer.getvalue(), df_rapor
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
    st.header("📊 Fabrika Anlık Stok ve Depo Paneli (Kg)")
    
    h_stok = toplam_hammadde_stok()
    
    st.subheader("💡 Kritik Hammadde Stok Özetleri")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PTA Stoku", f"{h_stok.get('PTA', 0.0):,.1f} Kg")
    col2.metric("MEG Stoku", f"{h_stok.get('MEG', 0.0):,.1f} Kg")
    col3.metric("Antimon Stoku", f"{h_stok.get('Antimon', 0.0):,.1f} Kg")
    col4.metric("Fosforik Asit Stoku", f"{h_stok.get('Fosforik Asit', 0.0):,.1f} Kg")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Mavi Boya", f"{h_stok.get('Mavi Boya', 0.0):,.1f} Kg")
    col6.metric("Kırmızı Boya", f"{h_stok.get('Kırmızı Boya', 0.0):,.1f} Kg")
    col7.metric("IPA Stoku", f"{h_stok.get('IPA', 0.0):,.1f} Kg")
    col8.metric("DEG Stoku", f"{h_stok.get('DEG', 0.0):,.1f} Kg")
    
    st.write("---")
    
    st.subheader("📦 Ürün Bazlı Gruplanmış Satışa Hazır Mamul Stokları")
    
    if st.session_state.mamul_depo:
        df_mamul = pd.DataFrame(st.session_state.mamul_depo)
        urun_gruplari = df_mamul.groupby("Ürün")
        
        for urun_adi, urun_data in urun_gruplari:
            toplam_urun_stok = urun_data["Miktar (Kg)"].sum()
            benzersiz_lot_sayisi = urun_data["Üretim LOT / Silo"].nunique()
            toplam_uretim_sayisi = len(urun_data)
            
            expander_basligi = f"🔹 {urun_adi}  |  Toplam Stok: {toplam_urun_stok:,.1f} Kg"
            with st.expander(expander_basligi):
                m1, m2, m3 = st.columns(3)
                m1.metric("Toplam Stok", f"{toplam_urun_stok:,.1f} Kg")
                m2.metric("Mevcut LOT Sayısı", f"{benzersiz_lot_sayisi} Adet")
                m3.metric("Toplam Üretim Sayısı", f"{toplam_uretim_sayisi} Sefer")
                
                st.write("**Bu Ürüne Ait Detaylı LOT Giriş Tablosu:**")
                st.dataframe(
                    urun_data[["Üretim Tarihi", "Üretim LOT / Silo", "Miktar (Kg)"]].reset_index(drop=True),
                    use_container_width=True
                )
    else:
        st.info("Sistemde henüz üretilmiş bir mamul (ürün) stoku bulunmuyor. Üretim emri sayfasından üretim yapabilirsiniz.")
        
    st.write("---")
    st.subheader("📋 Fabrika Tek Parça Genel Stok ve Malzeme Dengesi Raporu")
    excel_data, df_ekran_rapor = tek_rapor_excel_olustur()
    st.dataframe(df_ekran_rapor, use_container_width=True)
    
    st.download_button(
        label="📥 Tek Raporu Excel Olarak İndir (Kg)", 
        data=excel_data, 
        file_name=f"fabrika_genel_stok_raporu_kg_{datetime.now().strftime('%Y%m%d')}.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.write("---")
    t1, t2 = st.tabs(["📋 Detaylı Hammadde Lot Giriş Listesi", "📦 Ham Mamul Depo Günlüğü"])
    with t1:
        st.dataframe(pd.DataFrame(st.session_state.hammadde_depo), use_container_width=True)
    with t2:
        if st.session_state.mamul_depo:
            st.dataframe(pd.DataFrame(st.session_state.mamul_depo), use_container_width=True)
        else:
            st.info("Mamul günlüğü henüz boş.")
# ==========================================
# SAYFA: HAMMADDE GİRİŞİ
# ==========================================
elif sayfa == "📥 1. Hammadde Giriş Sayfası":
    st.header("📥 Lot Numaralı Hammadde Girişi (Kg)")
    
    with st.form("hammadde_form"):
        g_tarih = st.date_input("Giriş Tarihi", value=datetime.now())
        h_turu = st.selectbox("Hammadde Türü", ["PTA", "MEG", "Antimon", "Fosforik Asit", "Mavi Boya", "Kırmızı Boya", "IPA", "DEG"])
        h_lot = st.text_input("Hammadde LOT Numarası")
        h_miktar = st.number_input("Gelen Miktar (Kg)", min_value=0.1, step=100.0, format="%.1f")
        
        submit = st.form_submit_button("Hammaddeyi Depoya Kabul Et")
        if submit:
            if h_lot == "":
                st.error("Lütfen hammadde lot numarasını boş bırakmayın!")
            else:
                st.session_state.hammadde_depo.append({
                    "Giriş Tarihi": str(g_tarih), "Hammadde": h_turu, "LOT No": h_lot, "Miktar (Kg)": h_miktar
                })
                st.session_state.hammadde_giren_toplam[h_turu] = st.session_state.hammadde_giren_toplam.get(h_turu, 0.0) + h_miktar
                st.success(f"✅ {h_miktar:,.1f} Kg {h_turu} ({h_lot}) depoya alındı.")

# ==========================================
# SAYFA: REÇETE OLUŞTURMA
# ==========================================
elif sayfa == "📝 2. Reçete Oluşturma Sayfası":
    st.header("📝 Yeni Ürün Reçetesi (BOM) Tanımlama")
    st.write("Tüm hammadde ve kimyasalların 1 KİLOGRAM (Kg) PET Resin üretimi için gereken standart (teorik) miktarlarını girin.")
    
    with st.form("recete_form"):
        r_adi = st.text_input("Reçete / Ürün Adı", placeholder="Örn: Şişelik PET Resin (IV 0.80)")
        st.subheader("🧪 1 Kg Ürün İçin Gereken Hammadde Oranları (Kg Oranı Olarak)")
        
        c1, c2, c3, c4 = st.columns(4)
        pta_oran = c1.number_input("PTA Oranı", min_value=0.0, max_value=1.0, value=0.850, step=0.001, format="%.3f")
        meg_oran = c2.number_input("MEG Oranı", min_value=0.0, max_value=1.0, value=0.135, step=0.001, format="%.3f")
        ant_oran = c3.number_input("Antimon Oranı", min_value=0.0, max_value=1.0, value=0.005, step=0.001, format="%.3f")
        fos_oran = c4.number_input("Fosforik Asit", min_value=0.0, max_value=1.0, value=0.002, step=0.001, format="%.3f")
        
        c5, c6, c7, c8 = st.columns(4)
        mavi_oran = c5.number_input("Mavi Boya Oranı", min_value=0.0, max_value=1.0, value=0.001, step=0.001, format="%.3f")
        kirmizi_oran = c6.number_input("Kırmızı Boya Oranı", min_value=0.0, max_value=1.0, value=0.001, step=0.001, format="%.3f")
        ipa_oran = c7.number_input("IPA Oranı", min_value=0.0, max_value=1.0, value=0.004, step=0.001, format="%.3f")
        deg_oran = c8.number_input("DEG Oranı", min_value=0.0, max_value=1.0, value=0.002, step=0.001, format="%.3f")
        
        recete_submit = st.form_submit_button("Reçeteyi Sisteme Kaydet")
        if recete_submit:
            toplam_kütle = pta_oran + meg_oran + ant_oran + fos_oran + mavi_oran + kirmizi_oran + ipa_oran + deg_oran
            if not r_adi:
                st.error("❌ Lütfen Reçete / Ürün Adı alanını boş bırakmayın.")
            elif toplam_kütle <= 0:
                st.error("❌ Girdiğiniz hammadde oranlarının toplamı sıfır olamaz.")
            else:
                yeni_recete = {
                    "Reçete Adı": r_adi,
                    "BOM (Kg/Kg)": {
                        "PTA": pta_oran, "MEG": meg_oran, "Antimon": ant_oran, "Fosforik Asit": fos_oran,
                        "Mavi Boya": mavi_oran, "Kırmızı Boya": kirmizi_oran, "IPA": ipa_oran, "DEG": deg_oran
                    }
                }
                st.session_state.receteler.append(yeni_recete)
                st.success(f"✅ '{r_adi}' reçetesi başarıyla kaydedildi!")

    st.subheader("📋 Sistemde Tanımlı Reçeteler")
    if st.session_state.receteler:
        for idx, rec in enumerate(st.session_state.receteler):
            with st.expander(f"🔹 {rec['Reçete Adı']}"):
                st.json(rec["BOM (Kg/Kg)"])
    else:
        st.info("Sistemde henüz kayıtlı reçete bulunmamaktadır.")

# ==========================================
# SAYFA: ÜRETİM EMRİ & GİRİŞİ (FİİLİ TÜKETİM GÜNCELLEMESİ)
# ==========================================
elif sayfa == "🏭 3. Üretim Emri & Giriş Sayfası":
    st.header("🏭 Üretim Emri Oluşturma ve Reaktör Besleme")
    
    if not st.session_state.receteler:
        st.warning("⚠️ Üretim emri verebilmek için öncelikle reçete tanımlamalısınız.")
    else:
        h_stok = toplam_hammadde_stok()
        
        # 1. Aşama: Reçete ve Hedef Miktar Seçimi (Form Dışında - Dinamik Alan Tetiklemesi İçin)
        recete_secenekleri = [r["Reçete Adı"] for r in st.session_state.receteler]
        secilen_recete_adi = st.selectbox("Üretilecek Ürün / Reçete Seçin", recete_secenekleri)
        hedef_miktar = st.number_input("Hedef Üretim Miktarı (Kg)", min_value=1.0, value=1000.0, step=100.0, format="%.1f")
        u_lot = st.text_input("Üretim Parti / Silo No", value=f"PET-LOT-{datetime.now().strftime('%Y%m%d%H%M')}")
        
        # Seçilen reçete verisini çekme
        secilen_recete = next(r for r in st.session_state.receteler if r["Reçete Adı"] == secilen_recete_adi)
        
        st.write("---")
        st.subheader("⚙️ Fiili Hammadde Kullanım Tartım Girişleri")
        st.info("Aşağıdaki alanlar reçeteye göre hesaplanan **Teorik İhtiyaç** miktarlarını varsayılan olarak getirir. Eğer sahada reaktöre fiilen farklı miktarda besleme yapıldıysa değerleri manuel güncelleyin.")
        
        # Operatörün manuel giriş formu
        with st.form("uretim_form"):
            fiili_girisler = {}
            
            # Form içinde hammaddeleri grid yapısında gösteriyoruz
            c1_f, c2_f, c3_f, c4_f = st.columns(4)
            cols_list = [c1_f, c2_f, c3_f, c4_f]
            
            for idx, (h_adi, oran) in enumerate(secilen_recete["BOM (Kg/Kg)"].items()):
                teorik_ihtiyac = hedef_miktar * oran
                current_col = cols_list[idx % 4]
                
                # Operatörün düzenleyebileceği fiili giriş kutusu
                fiili_girisler[h_adi] = current_col.number_input(
                    f"{h_adi} Fiili Kullanım (Kg)", 
                    min_value=0.0, 
                    value=float(teorik_ihtiyac), 
                    step=1.0, 
                    format="%.2f",
                    help=f"Teorik Hesaplanan: {teorik_ihtiyac:,.2f} Kg"
                )
            
            st.write(" ")
            uretim_submit = st.form_submit_button("Üretim Emrini Onayla ve Fiili Miktarları Stoktan Düş")
            
            if uretim_submit:
                stok_kontrol_basarili = True
                eksik_olanlar = []
                
                # Stok kontrolünü operatörün girdiği FİİLİ değerlere göre yapıyoruz
                for h_adi, fiili_kg in fiili_girisler.items():
                    mevcut_kg = h_stok.get(h_adi, 0.0)
                    if mevcut_kg < fiili_kg:
                        stok_kontrol_basarili = False
                        eksik_olanlar.append(f"{h_adi} (Fiili Talep: {fiili_kg:,.1f} Kg, Depo Mevcut: {mevcut_kg:,.1f} Kg)")
                
                if not stok_kontrol_basarili:
                    st.error(f"❌ Üretim Başarısız! Girilen fiili kullanım miktarları mevcut depo stoklarını aşıyor:\n" + "\n".join([f"- {item}" for item in eksik_olanlar]))
                else:
                    # Gerçekleşen fiili tüketimi merkezi stoktan düşüyoruz
                    for h_adi, fiili_kg in fiili_girisler.items():
                        st.session_state.hammadde_kullanilan_toplam[h_adi] += fiili_kg
                    
                    # Üretilen mamulü depoya ekliyoruz
                    st.session_state.mamul_depo.append({
                        "Üretim Tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Ürün": secilen_recete_adi,
                        "Üretim LOT / Silo": u_lot,
                        "Miktar (Kg)": hedef_miktar
                    })
                    st.success(f"🎉 {hedef_miktar:,.1f} Kg Üretim Başarıyla Tamamlandı! Stoklardan manuel girilen fiili tartım miktarları düşüldü.")
                    st.rerun()

    st.write("---")
    st.subheader("📦 Güncel Mamul (PET) Depo Stok Geçmişi")
    if st.session_state.mamul_depo:
        st.dataframe(pd.DataFrame(st.session_state.mamul_depo), use_container_width=True)
    else:
        st.info("Henüz üretilmiş bir mamul bulunmuyor.")
