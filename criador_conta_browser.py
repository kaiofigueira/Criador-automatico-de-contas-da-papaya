import time
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

        # Chama a função de esperar resolução do CAPTCHA
        if not self.verificar_resolucao_captcha():
            return False  # Retorna False se "Try again later" for detectado

        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[2]/div/form/button'))
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        button.click()
        
        self.usuario_conta = usuario_conta
        return True  # Retorna True se a criação da conta continuar normalmente

    def verificar_ipblock(self):
        div_xpath = '//*[@id="toast-container"]/div/div'
        try:
            # Espera até que o div com o xpath especificado esteja presente na página
            div_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, div_xpath))
            )
            # Verifica se o texto do elemento contém a mensagem de bloqueio
            if "Sign up not allowed. Please contact our support." in div_element.text:
                print("Cadastro bloqueado: IP bloqueado ou problema relacionado.")
                return True
            else:
                print("Cadastro permitido.")
                return False
        except TimeoutException:
            print("Mensagem de bloqueio não apareceu dentro do tempo especificado.")
            return False
        
    def verificar_try_again_captcha(self):
        captcha_try_again_xpath = '//div[@class="rc-doscaptcha-header"]//div[@class="rc-doscaptcha-header-text"]'
        try:
            # Espera até que o elemento com a classe especificada esteja presente na página
            captcha_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, captcha_try_again_xpath))
            )
            # Verifica se o texto do elemento contém "Try again later"
            if "Try again later" in captcha_element.text:
                print("Captcha detectado: Try again later.")
                return True
            else:
                print("Captcha presente, mas o texto não corresponde.")
                return False
        except TimeoutException:
            print("Try again não detectado dentro do tempo especificado.")
            return False
        
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

    def verificar_resolucao_captcha(self, timeout=1200, check_interval=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )
            
            captcha = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            )

            print("Resolvendo o reCAPTCHA")

            start_time = time.time()

            while True:
                if "recaptcha-checkbox-checked" in captcha.get_attribute("class"):
                    print("reCAPTCHA foi verificado com sucesso!")
                    return True  # Retorna False se o CAPTCHA foi verificado com sucesso
                
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    raise TimeoutException("Tempo limite alcançado ou o reCAPTCHA não foi verificado dentro do tempo especificado.")

                if elapsed_time % check_interval < 1:
                    if self.verificar_try_again_captcha():
                        print("Captcha detectou 'Try again later'.")
                        return False  # Retorna True se "Try again later" foi detectado
                
                time.sleep(1)

        except TimeoutException:
            print("Tempo limite alcançado ou o reCAPTCHA não foi verificado dentro do tempo especificado.")
            return False  # Considera como um "Try again later" se o tempo expirar
        
        finally:
            self.driver.switch_to.default_content()

    def validar_caminho(path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado. Verifique o caminho.")
        
    def obter_profile(self, path):
        # Configura as opções do Edge para carregar o perfil
        self.options.add_argument(f'user-data-dir={path}')