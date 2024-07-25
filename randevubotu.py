import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def start_bot():
    global driver
    driver = None

    try:
        user_email = entry_email.get()
        user_password = entry_password.get()
        appointment_number = entry_appointment_number.get()
        consulate_address = consulate_var.get()
        earliest_date = start_date_entry.get_date().strftime("%Y-%m-%d")
        latest_date = end_date_entry.get_date().strftime("%Y-%m-%d")
        notification_email = entry_notify_email.get()
        
        # Kontrol: X saniyede bir tarih kontrolü ve açık tarih yoksa X saniye bekle
        check_interval = int(entry_check_interval.get())
        wait_time_if_no_appointment = int(entry_wait_interval.get())

    except ValueError as ve:
        messagebox.showerror("Giriş Hatası", f"Giriş hatası: {ve}")
        return

    def check_for_earlier_appointment():
        # 3. Tarih kontrolü
        available_date = "2024-08-01"  # Bu tarih örnektir. Gerçek tarih siteden çekilmelidir.
        if earliest_date <= available_date <= latest_date:
            # 4. Randevu değişikliği
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "change_appointment_button"))).click()
                time.sleep(2)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "confirm_button"))).click()
                
                # 5. Bilgilendirme
                send_email_notification(notification_email, available_date)
                return True
            except Exception as e:
                messagebox.showerror("Hata", f"Randevu değişiklik işlemi sırasında bir hata oluştu: {e}")
        return False

    def send_email_notification(to_email, new_date):
        msg = MIMEMultipart()
        msg["From"] = user_email
        msg["To"] = to_email
        msg["Subject"] = "New Visa Appointment Date Available"
        
        body = f"New visa appointment date available: {new_date}"
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP("smtp.example.com", 587) as server:
                server.starttls()
                server.login(user_email, user_password)
                text = msg.as_string()
                server.sendmail(user_email, to_email, text)
        except smtplib.SMTPException as e:
            messagebox.showerror("E-posta Hatası", f"E-posta gönderimi sırasında bir hata oluştu: {e}")

    try:
        # WebDriver'ı başlat
        service = Service(executable_path="path/to/chromedriver")  # Chromedriver yolu
        driver = webdriver.Chrome(service=service)
        driver.get("https://ais.usvisa-info.com/tr-tr/niv/users/sign_in")
        time.sleep(2)

        # Giriş yapma
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "user[email]"))).send_keys(user_email)
        driver.find_element(By.NAME, "user[password]").send_keys(user_password)
        driver.find_element(By.NAME, "policy_confirmed").click()  # Gizlilik politikasını onaylama
        driver.find_element(By.NAME, "commit").click()
        time.sleep(2)

        # Konsolosluk seçimi
        if consulate_address == "Istanbul":
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "istanbul_consulate"))).click()
        elif consulate_address == "Ankara":
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ankara_consulate"))).click()
        time.sleep(2)

        # Ana döngü
        while True:
            if check_for_earlier_appointment():
                break
            else:
                time.sleep(wait_time_if_no_appointment)

    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")
    finally:
        if driver:
            driver.quit()

# GUI
root = tk.Tk()
root.title("Amerika Erken Randevu Botu")

# Pencere boyutu ayarları
root.geometry("400x400")
root.minsize(400, 400)

tk.Label(root, text="Ais E-posta:").grid(row=0, column=0, padx=10, pady=5)
entry_email = tk.Entry(root)
entry_email.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Ais Şifre:").grid(row=1, column=0, padx=10, pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Randevu Numarası:").grid(row=2, column=0, padx=10, pady=5)
entry_appointment_number = tk.Entry(root)
entry_appointment_number.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Konsolosluk:").grid(row=3, column=0, padx=10, pady=5)
consulates = ["Istanbul", "Ankara"]
consulate_var = tk.StringVar(root)
consulate_var.set(consulates[0])  # Varsayılan olarak Istanbul seçili
consulate_menu = tk.OptionMenu(root, consulate_var, *consulates)
consulate_menu.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Başlangıç Tarihi:").grid(row=4, column=0, padx=10, pady=5)
start_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
start_date_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Bitiş Tarihi:").grid(row=5, column=0, padx=10, pady=5)
end_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
end_date_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Bilgilendirme E-posta:").grid(row=6, column=0, padx=10, pady=5)
entry_notify_email = tk.Entry(root)
entry_notify_email.grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="X Saniyede Bir Tarih Kontrolü:").grid(row=7, column=0, padx=10, pady=5)
entry_check_interval = tk.Entry(root)
entry_check_interval.grid(row=7, column=1, padx=10, pady=5)

tk.Label(root, text="Açık Tarih Yoksa X Saniye Bekle:").grid(row=8, column=0, padx=10, pady=5)
entry_wait_interval = tk.Entry(root)
entry_wait_interval.grid(row=8, column=1, padx=10, pady=5)

tk.Button(root, text="Başlat", command=start_bot).grid(row=9, column=1, padx=10, pady=20)

root.mainloop()
