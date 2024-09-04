import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os        
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

class CriadorConta():

    def __init__(self, driver) -> None:
        self.driver = driver
        self.usuario_conta = None
        self.email_temporario = None
        self.site_email_temporario = 'https://www.invertexto.com/gerador-email-temporario'
        self.site_papaya = 'https://www.papayaplay.com/account/signup.do'
        
    def fechar_driver(self, mensagem: str) -> None:
        print(mensagem)
        self.driver.quit()

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

    def cadastrar_conta_papaya(self, timeout=20):
        self.entrar_site(self.site_papaya)
        campo_usuario = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.NAME, 'userid'))
        )
        campo_email = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'equalEmail'))
        )
        campo_confirma_email = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'confirmEmail'))
        )
        campo_senha = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.NAME, 'pwd'))
        )
        campo_checkbox = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'custCheckbox'))
        )

        usuario_conta = self.email_temporario.split('@')[0]
        campo_usuario.send_keys(usuario_conta)
        campo_email.send_keys(self.email_temporario)
        campo_confirma_email.send_keys(self.email_temporario)
        campo_senha.send_keys(usuario_conta)
        if not campo_checkbox.is_selected():
            self.driver.execute_script("arguments[0].click();", campo_checkbox)

        # Chama a função de esperar resolução do CAPTCHA
        self.verificar_resolucao_captcha()

        button = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[2]/div/form/button'))
        )

        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        self.driver.execute_script("arguments[0].click();", button)
        
        self.usuario_conta = usuario_conta

    def verificar_ipblock(self, timeout=20):
        div_xpath = '//*[@id="toast-container"]/div/div'
        try:
            # Espera até que o div com o xpath especificado esteja presente na página
            div_element = WebDriverWait(self.driver, timeout).until(
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
            print("Mensagem de bloqueio de ip não apareceu dentro do tempo especificado.")
            return False

    def verificar_try_again_captcha(self, timeout=20):
        try:
            # Espera até que o iframe esteja presente e alterna o contexto para ele
            iframe = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[4]/iframe'))
            )
            self.driver.switch_to.frame(iframe)
            
            try:
                # Espera até que o elemento com a classe 'rc-doscaptcha-header-text' esteja presente dentro do iframe
                captcha_header = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "rc-doscaptcha-header-text")]'))
                )
                
                # Verifica se o texto do elemento contém "Try again later"
                if "Try again later" in captcha_header.text:
                    print("Captcha detectado: Try again later.")
                    return True
                else:
                    print(f"Texto do captcha: {captcha_header.text}")
                    return False
            except NoSuchElementException:
                #print("Elemento com a classe 'rc-doscaptcha-header-text' não encontrado dentro do iframe.")
                return False
            except StaleElementReferenceException:
                #print("Elemento com a classe 'rc-doscaptcha-header-text' tornou-se obsoleto.")
                return False
            finally:
                # Retorna ao contexto principal do documento
                self.driver.switch_to.default_content()

        except TimeoutException:
            #print("Tempo limite excedido ao tentar encontrar o iframe ou o elemento dentro do iframe.")
            return False

    def obter_email_temporario(self, timeout=20):
        self.entrar_site(self.site_email_temporario)
        
        email_element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, 'email-input'))
        )
        
        email_temporario = email_element.get_attribute('value')
        print(f'Email gerado: {email_temporario}')

        self.email_temporario = email_temporario

    def verificar_recebimento_email(self, tbody_xpath, timeout=360):
        print("Verificando recebimento de e-mail")
        # Espera até que um novo email apareça na tabela de emails
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, tbody_xpath + '/tr'))
            )
            print("e-mail recebido")
            return True
        except TimeoutException:
            print(f"O email não foi recebido dentro de {timeout} segundos.")
            return False
        
        return False

    def clicar_email(self, timeout=20):
        print("Clicando no e-mail")
        tbody_xpath = '/html/body/main/div[1]/div[3]/div[1]/table/tbody'

        if not self.verificar_recebimento_email(tbody_xpath):
            return False

        tbody_element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, tbody_xpath))
        )

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
                    return True
            except Exception as e:
                print(f'Erro ao encontrar o ID: {e}')
                return False
            
        return False

    def clicar_link(self, timeout=20):
        print("Clicando no link de confirmação de registro")
        try:
            shadow_host_xpath = '//*[@id="body"]'
            shadow_host = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, shadow_host_xpath))
            )

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
            
            return True
        except Exception as e:
            print(f"Erro na etapa de clicar no link: {e}")
            return False
        
        return False
        

    def validar_email_apos_criar_conta_papaya(self):
        print("Validando e-mail após criação da conta no papaya")
        self.entrar_site(self.site_email_temporario + f"?email={self.email_temporario}")
    
        if not self.clicar_email():
            return False
        
        if not self.clicar_link():
            return False

        return True

    def validar_criacao_conta_papaya(self, timeout=10):
        print("Validando criação da conta no papaya")

        body_element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "portal"))
        )
        h2_elements = body_element.find_elements(By.XPATH, '//*[@id="sign-up-complete"]/div/h2')

        for h2_element in h2_elements:
            try:
                h2_text = h2_element.text
                if h2_text == "Sign Up Completed":
                    print("Conta cadastrada com sucesso")
                    return True
            except Exception as e:
                print(f'Erro ao cadastrar conta: {e}')
                return False
        
        return False

    def verificar_resolucao_captcha(self, timeout=1200):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )
            
            captcha = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            )

            print("Resolvendo o reCAPTCHA")

            while True:
                if "recaptcha-checkbox-checked" in captcha.get_attribute("class"):
                    print("reCAPTCHA foi verificado com sucesso!")
                    return True
                
                time.sleep(1)

        except TimeoutException:
            print("Tempo limite alcançado ou o reCAPTCHA não foi verificado dentro do tempo especificado.")
            return False
        
        finally:
            self.driver.switch_to.default_content()

    def validar_caminho(path: str):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"O arquivo '{path}' não foi encontrado. Verifique o caminho.")
        
    def obter_profile(self, path):
        # Configura as opções do Edge para carregar o perfil
        self.options.add_argument(f'user-data-dir={path}')