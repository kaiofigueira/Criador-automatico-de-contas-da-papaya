import subprocess
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from criador_conta_browser import CriadorContaBrowser

class CriadorContaEdge(CriadorContaBrowser):

    def __init__(self, profile_path) -> None:
        self.driver_path = r'msedgedriver.exe' 
        self.options = EdgeOptions()
        super().obter_profile(profile_path)
        super().__init__(None)  # Chama o construtor da classe base sem driver ainda

    @staticmethod
    def close_msedge_instances():
        try:
            # Fechar instâncias do Microsoft Edge
            subprocess.run("taskkill /F /IM msedge.exe", shell=True)
            print("Instancias deletadas")
        except Exception as e:
            print(f"Erro ao fechar as instâncias do Chrome: {e}")

    def obter_driver(self):
        self.driver = webdriver.Edge(service=EdgeService(executable_path=self.driver_path), options=self.options)
        super().__init__(self.driver)  # Agora inicializa o driver na classe base

