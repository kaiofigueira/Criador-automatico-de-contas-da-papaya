import subprocess
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from criador_conta import CriadorConta

class CriadorContaEdge(CriadorConta):

    def __init__(self, profile_path) -> None:
        self.driver_path = r'msedgedriver.exe' 
        self.options = EdgeOptions()
        super().obter_profile(profile_path)
        super().__init__(None)  # Chama o construtor da classe base sem driver ainda

    def fechar_browser(self, mensagem):
        super().fechar_driver(mensagem)
        self.close_msedge_instances()

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

    def criar_conta(self, qtd_contas_criacao: int) -> None:
        for i in range(1, qtd_contas_criacao + 1):
            while True:
                try:
                    self.obter_driver()
                    super().obter_email_temporario()
                    super().cadastrar_conta_papaya()

                    if super().verificar_ipblock():
                        self.fechar_browser("IP bloqueado, reiniciando o driver...")
                        continue

                    if not super().validar_email_apos_criar_conta_papaya():
                        self.fechar_browser("Falha na validação do e-mail, tentando novamente...")
                        continue

                    if not super().validar_criacao_conta_papaya():
                        self.fechar_browser("Falha na validação da conta, tentando novamente...")
                        continue
                    
                    super().adicionar_conta_txt()
                    self.fechar_browser(f"Quantidade de contas geradas: {i}")
                    print()
                    print()
                    break

                except Exception as e:
                    self.fechar_browser(f"Erro inesperado: {e}, reiniciando o driver...")
                    
        self.fechar_browser("Fim")