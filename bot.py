import os
import sys
import time
import threading
from time import time as current_time, strftime, gmtime, sleep
import pyfiglet

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration des métriques
metrics = {
    "views": 0,
    "hearts": 0,
    "followers": 0,
    "shares": 0
}
start_time = 0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_terminal_title(title_text):
    if os.name == 'nt':
        os.system(f'title {title_text}')

def beautify(arg):
    return format(arg, ',d').replace(',', '.')

def update_title_thread(mode_name, metric_key):
    """Met à jour le titre du terminal en arrière-plan."""
    while True:
        elapsed = strftime('%H:%M:%S', gmtime(current_time() - start_time))
        count = beautify(metrics[metric_key])
        set_terminal_title(f"TikTok Bot | {mode_name}: {count} | Temps écoulé: {elapsed}")
        sleep(1)

def run_automation_loop(driver, vid_url, btn_service_xpath, input_xpath, search_xpath, send_xpath, cooldown, metric_key, increment_val):
    """Boucle d'automatisation générique pour traiter les 4 modes d'engagement."""
    wait = WebDriverWait(driver, 15)
    
    # 1. Attente de la résolution manuelle du CAPTCHA initial
    while True:
        try:
            service_btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_service_xpath)))
            service_btn.click()
            print("[+] Service sélectionné.")
            break
        except Exception:
            print("[-] Résolvez le CAPTCHA dans le navigateur Chrome...")
            sleep(5)
            driver.refresh()

    # 2. Boucle d'envoi répétitive
    while True:
        try:
            sleep(2)
            input_elem = wait.until(EC.presence_of_element_located((By.XPATH, input_xpath)))
            input_elem.clear()
            input_elem.send_keys(vid_url)

            sleep(1)
            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
            search_btn.click()

            sleep(5)
            send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, send_xpath)))
            send_btn.click()

            metrics[metric_key] += increment_val
            print(f"[+] Succès ! {metric_key.capitalize()} envoyés.")

            driver.refresh()
            print(f"[*] Pause obligatoire de {cooldown}s (limite de la plateforme)...")
            sleep(cooldown)

        except Exception as e:
            print(f"[-] Une erreur est survenue. Nouvelle tentative dans 5 secondes...")
            driver.refresh()
            sleep(5)

def main():
    global start_time
    clear_console()
    set_terminal_title("TikTok Bot")

    print(pyfiglet.figlet_format("TikTok Bot", font="slant"))
    print("=" * 50)
    print("1. Vues\n2. Likes\n3. Followers\n4. Partages\n5. Crédits\n")

    try:
        choice = int(input("Choix (1-5) : "))
        if not 1 <= choice <= 5:
            raise ValueError
    except ValueError:
        print("Erreur : Entrez un nombre valide entre 1 et 5.")
        return

    if choice == 5:
        print("\nProjet original par @kangoka — Amélioré par la communauté.")
        return

    vid_url = input("URL de la vidéo TikTok : ").strip()
    start_time = current_time()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1024, 650)
    driver.get("https://zefoy.com/")

    # Configuration par mode : (Service XPATH, Input XPATH, Search XPATH, Send XPATH, Cooldown(s), Métrique, Incrément)
    config = {
        1: ("/html/body/div[4]/div[1]/div[3]/div/div[4]/div/button", "//*[@id='sid4']/div/form/div/input", "//*[@id='sid4']/div/form/div/div/button", "//*[@id='c2VuZC9mb2xsb3dlcnNfdGlrdG9V']/div[1]/div/form/button", 300, "views", 1000),
        2: ("/html/body/div[4]/div[1]/div[3]/div/div[2]/div/button", "//*[@id='sid2']/div/form/div/input", "//*[@id='sid2']/div/form/div/div/button", "//*[@id='c2VuZE9nb2xsb3dlcnNfdGlrdG9r']/div[1]/div/form/button", 1800, "hearts", 10),
        3: ("/html/body/div[4]/div[1]/div[3]/div/div[1]/div/button", "//*[@id='sid']/div/form/div/input", "//*[@id='sid']/div/form/div/div/button", "//*[@id='c2VuZF9mb2xsb3dlcnNfdGlrdG9r']/div[1]/div/form/button", 1800, "followers", 10),
        4: ("/html/body/div[4]/div[1]/div[3]/div/div[5]/div/button", "//*[@id='sid7']/div/form/div/input", "//*[@id='sid7']/div/form/div/div/button", "//*[@id='c2VuZC9mb2xsb3dlcnNfdGlrdG9s']/div[1]/div/form/button", 300, "shares", 100)
    }

    service_btn, input_x, search_x, send_x, cooldown, key, inc = config[choice]

    # Lancement du thread de mise à jour du titre
    t_title = threading.Thread(target=update_title_thread, args=(key.capitalize(), key), daemon=True)
    t_title.start()

    # Lancement de la boucle principale
    run_automation_loop(driver, vid_url, service_btn, input_x, search_x, send_x, cooldown, key, inc)

if __name__ == '__main__':
    main()
