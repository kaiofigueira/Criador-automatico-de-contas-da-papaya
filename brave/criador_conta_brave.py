import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from criador_conta import CriadorConta

class CriadorContaBrave(CriadorConta):

    def __init__(self, profile_path, binary_location) -> None:
        self.driver_path = r'chromedriver.exe' 
        
        self.options = Options()
        self.options.binary_location = binary_location

        super().obter_profile(profile_path)
        super().__init__(None)  # Chama o construtor da classe base sem driver ainda

    def fechar_browser(self, mensagem):
        super().fechar_driver(mensagem)
        self.close_brave_instances()
        print()
        print()

    @staticmethod
    def close_brave_instances():
        try:
            # Fechar instâncias do Brave
            subprocess.run("taskkill /F /IM brave.exe", shell=True)
            print("Instancias deletadas")
        except Exception as e:
            print(f"Erro ao fechar as instâncias do Chrome: {e}")

    def obter_driver(self):
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
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
                    break

                except Exception as e:
                    self.fechar_browser(f"Erro inesperado: {e}, reiniciando o driver...")
                    
        self.fechar_browser("Fim")