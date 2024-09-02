from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.common.exceptions import TimeoutException

class CriadorContaBrowser():

    def __init__(self, driver) -> None:
        self.driver = driver

    def adicionar_conta_txt(self):
        arquivo_txt = f'../contas/contas_criadas.txt'
        os.makedirs(os.path.dirname(arquivo_txt), exist_ok=True)
        with open(arquivo_txt, 'a') as f:
            f.write(self.usuario_conta + '\n')
        print(f'Conta {self.usuario_conta} gravada em {arquivo_txt}')

    def configurar_proxy(options, proxy: str):
        options.add_argument(f'--proxy-server={proxy}')
        return options
    
    def entrar_site(self, site):
        self.driver.get(site)

    def cadastrar_conta_papaya(self):
        self.entrar_site('https://www.papayaplay.com/account/signup.do')
        campo_usuario = self.driver.find_element(By.NAME, 'userid')
        campo_email = self.driver.find_element(By.ID, 'equalEmail')
        campo_confirma_email = self.driver.find_element(By.ID, 'confirmEmail')
        campo_senha = self.driver.find_element(By.NAME, 'pwd')
        campo_checkbox = self.driver.find_element(By.ID, 'custCheckbox')

        usuario_conta = self.email_temporario.split('@')[0]
        campo_usuario.send_keys(usuario_conta)
        campo_email.send_keys(self.email_temporario)
        campo_confirma_email.send_keys(self.email_temporario)
        campo_senha.send_keys(usuario_conta)
        if not campo_checkbox.is_selected():
            self.driver.execute_script("arguments[0].click();", campo_checkbox)

        self.esperar_resolucao_captcha()

        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[2]/div/form/button'))
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        button.click()
        
        self.usuario_conta = usuario_conta

    def obter_email_temporario(self):
        self.site_email_temporario = 'https://www.invertexto.com/gerador-email-temporario'
        self.entrar_site(self.site_email_temporario)
        email_element = self.driver.find_element(By.ID, 'email-input')
        email_temporario = email_element.get_attribute('value')
        print(f'Email gerado: {email_temporario}')

        self.email_temporario = email_temporario

    def esperar_recebimento_email(self, tbody_xpath, timeout=360):
        # Espera até que um novo email apareça na tabela de emails
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, tbody_xpath + '/tr'))
            )
            print("e-mail recebido")
        except TimeoutException:
            print(f"O email não foi recebido dentro de {timeout} segundos.")
            return

    def clicar_email(self, timeout=180):
        tbody_xpath = '/html/body/main/div[1]/div[3]/div[1]/table/tbody'

        self.esperar_recebimento_email(tbody_xpath)

        tbody_element = self.driver.find_element(By.XPATH, tbody_xpath)
        tr_elements = tbody_element.find_elements(By.XPATH, './tr')

        for tr_element in tr_elements:
            try:
                element_id = tr_element.get_attribute('id')
                if element_id:
                    print(f'ID encontrado: {element_id}')
                    script = """
                        var element = arguments[0];
                        if (element) {
                            element.click();
                        }
                    """
                    self.driver.execute_script(script, tr_element)
                    break
            except Exception as e:
                print(f'Erro ao encontrar o ID: {e}')

        # Espera até que o elemento do email clicado esteja presente na página
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, f'//*[@id="{element_id}"]'))
            )
        except TimeoutException:
            print("Falha ao clicar no email ou o email não foi carregado corretamente.")

    def clicar_link(self):
        shadow_host_xpath = '//*[@id="body"]'
        shadow_host = self.driver.find_element(By.XPATH, shadow_host_xpath)

        script_shadow = """
            var shadowHost = arguments[0];
            var shadowRoot = shadowHost.shadowRoot;
            if (shadowRoot) {
                return Array.from(shadowRoot.querySelectorAll('a')).map(a => a.href);
            }
            return [];
        """
        links = self.driver.execute_script(script_shadow, shadow_host)

        if links:
            first_link = links[0]
            print(f"Primeiro link encontrado: {first_link}")
            self.entrar_site(first_link)
        else:
            print("Nenhum link encontrado.")

    def validar_email_apos_criar_conta_papaya(self):
        self.entrar_site(self.site_email_temporario + f"?email={self.email_temporario}")
    
        self.clicar_email()
        self.clicar_link()

    def validar_criacao_conta_papaya(self):
        body_element = self.driver.find_element(By.ID, "portal")
        h2_elements = body_element.find_elements(By.XPATH, '//*[@id="sign-up-complete"]/div/h2')

        for h2_element in h2_elements:
            try:
                h2_value = h2_element.get_attribute('value')
                if h2_value == "Sign Up Completed":
                    print("Conta cadastrada com sucesso")
                    break
            except Exception as e:
                print(f'Erro ao cadastrar conta')

    def esperar_resolucao_captcha(self, timeout=1200):
        try:
            # Espera até que o iframe do reCAPTCHA esteja disponível e faz a troca para ele
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )
            
            # Espera até que o elemento do CAPTCHA esteja presente
            captcha = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            )

            print("Resolvendo o reCAPTCHA")

            # Espera até que a classe 'recaptcha-checkbox-checked' apareça
            WebDriverWait(self.driver, timeout).until(
                lambda d: "recaptcha-checkbox-checked" in captcha.get_attribute("class")
            )
            
            print("reCAPTCHA foi verificado com sucesso!")

        except TimeoutException:
            print("Tempo limite alcançado ou o reCAPTCHA não foi verificado dentro do tempo especificado.")
        
        # Retorna ao contexto principal da página
        self.driver.switch_to.default_content()

    def validar_caminho(path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado. Verifique o caminho.")
        
    def obter_profile(self, path):
        # Configura as opções do Edge para carregar o perfil
        self.options.add_argument(f'user-data-dir={path}')