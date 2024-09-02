import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from criador_conta_browser import CriadorContaBrowser

class CriadorContaChrome(CriadorContaBrowser):

    def __init__(self, profile_path) -> None:
        self.driver_path = r'chromedriver.exe' 
        self.options = Options()
        super().obter_profile(profile_path)
        super().__init__(None)  # Chama o construtor da classe base sem driver ainda

    @staticmethod
    def close_chrome_instances():
        try:
            # Fechar instâncias do Chrome
            subprocess.run("taskkill /F /IM chrome.exe", shell=True)
            print("Instancias deletadas")
        except Exception as e:
            print(f"Erro ao fechar as instâncias do Chrome: {e}")

    def obter_driver(self):
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
        super().__init__(self.driver)  # Agora inicializa o driver na classe base

