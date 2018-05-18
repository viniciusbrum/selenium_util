#! python3
# selenium_util.py - Funções auxiliares para uso do módulo selenium.

from abc import ABCMeta
from abc import abstractmethod
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import time


class DriverBase(metaclass=ABCMeta):
    """Driver auxiliar para selenium.webdriver"""

    def __init__(self, caminho_driver, tempo_espera):
        """Inicializa e configura uma instância de DriverBase."""
        self._caminho_driver = caminho_driver
        self._tempo_espera = tempo_espera
        self._inicializa_driver()
        self._inicializa_wait()

    def __getattr__(self, atributo):
        """Delega atributos para o objeto driver."""
        return getattr(self._driver, atributo)

    def _aguarda_carregamento(self):
        """Aguarda carregamento da página de acordo com o tempo limite."""
        js_script = 'return document.readyState;'
        tempo_inicial = time.time()
        tempo_limite = tempo_inicial + self._tempo_espera
        carregando = self.execute_script(js_script).lower() != 'complete'

        while time.time() < tempo_limite and carregando:
            carregando = self.execute_script(js_script).lower() != 'complete'

    @abstractmethod
    def _encerra_driver(self):
        """Encerra a instância de webdriver."""
        pass

    @abstractmethod
    def _inicializa_driver(self):
        """Inicializa e configura uma instância de webdriver."""
        pass

    def _inicializa_wait(self):
        """Inicializa e configura uma instância de WebDriverWait."""
        self._wait = WebDriverWait(self._driver, self._tempo_espera)

    def acessa_url(self, url):
        """Acessa uma url."""
        self._driver.get(url)

    def aponta_para_elemento(self, tipo_seletor, seletor):
        """Simula a ação de mouseover em um elemento."""
        self._aguarda_carregamento()
        ActionChains(self._driver).move_to_element(
            self.busca_elemento_visivel(tipo_seletor, seletor)).perform()

    def busca_elemento_clicavel(self, tipo_seletor, seletor):
        """Busca e retorna elemento clicável."""
        self._aguarda_carregamento()
        return self._wait.until(expected_conditions.element_to_be_clickable(
            (tipo_seletor, seletor)))

    def busca_elemento_visivel(self, tipo_seletor, seletor):
        """Busca e retorna elemento visível."""
        self._aguarda_carregamento()
        return self._wait.until(
            expected_conditions.visibility_of_element_located(
                (tipo_seletor, seletor)))

    def busca_elementos(self, tipo_seletor, seletor):
        """Busca e retorna elementos."""
        self._aguarda_carregamento()
        return self._wait.until(
            expected_conditions.presence_of_all_elements_located(
                (tipo_seletor, seletor)))

    def clica_elemento(self, tipo_seletor, seletor):
        """Busca e clica em elemento."""
        self._aguarda_carregamento()
        ActionChains(self._driver).move_to_element(
            self.busca_elemento_visivel(tipo_seletor,
                                        seletor)).click().perform()

    def clica_botao_direito_elemento(self, tipo_seletor=None, seletor=None):
        """Busca e clica com o botão direito no elemento ou na posição
        atual do mouse."""
        self._aguarda_carregamento()

        if tipo_seletor is not None:
            ActionChains(self._driver).context_click(
                self.busca_elemento_clicavel(tipo_seletor, seletor)).perform()
        else:
            ActionChains(self._driver).context_click().perform()

    def insere_opcao_elemento(self, tipo_seletor, seletor, valor_opcao):
        """Busca e seleciona opção por opção em elemento."""
        self._aguarda_carregamento()
        Select(self.busca_elemento_visivel(tipo_seletor,
                                           seletor)).select_by_value(valor_opcao)

    def insere_texto_elemento(self, tipo_seletor, seletor, texto, enter=False):
        """Busca, insere texto e "tecla" ENTER em elemento."""
        self._aguarda_carregamento()
        elemento = self.busca_elemento_visivel(tipo_seletor, seletor)
        elemento.clear()
        elemento.send_keys(texto)

        if enter:
            elemento.send_keys(Keys.ENTER)

    def retorna_atributo_elemento(self, tipo_seletor, seletor, atributo):
        """Busca e retorna um atributo do elemento."""
        self._aguarda_carregamento()
        self.busca_elemento_visivel(tipo_seletor,
                                    seletor).get_attribute(atributo)

    def retorna_atributo_elementos(self, tipo_seletor, seletor, atributo,
                                   funcao_condicao=None, funcao_formato=None):
        """Busca e retorna um atributo dos elementos de acordo com
        determinada condição em determinada formatação."""

        def funcao_aux_condicao(atributo):
            return True

        def funcao_aux_formato(atributo):
            return atributo

        if funcao_condicao is None:
            funcao_condicao = funcao_aux_condicao

        if funcao_formato is None:
            funcao_formato = funcao_aux_formato

        self._aguarda_carregamento()
        elementos = self.busca_elementos(tipo_seletor, seletor)
        atributos = [funcao_formato(e.get_attribute(atributo))
                     for e in elementos if funcao_condicao(
                        e.get_attribute(atributo))]
        return atributos

    def retorna_numero_elementos(self, tipo_seletor, seletor, atributo=None,
                                 funcao_condicao=None):
        """Busca e retorna o número de elementos nos quais determinado
        atributo atende determinada condição."""
        self._aguarda_carregamento()

        if atributo is not None:
            return len(self.retorna_atributo_elementos(tipo_seletor,
                                                       seletor, atributo,
                                                       funcao_condicao))

        return len(self.busca_elementos(tipo_seletor, seletor))

    def retorna_texto_elemento(self, tipo_seletor, seletor):
        """Busca e retorna o texto do elemento."""
        self._aguarda_carregamento()
        return self.busca_elemento_visivel(tipo_seletor, seletor).text

    def retorna_texto_elementos(self, tipo_seletor, seletor,
                                funcao_condicao=None, funcao_formato=None):
        """Busca e retorna o texto dos elementos de acordo com
        determinada condição em determinada formatação."""

        def funcao_aux_condicao(texto):
            return True

        def funcao_aux_formato(texto):
            return texto

        if funcao_condicao is None:
            funcao_condicao = funcao_aux_condicao

        if funcao_formato is None:
            funcao_formato = funcao_aux_formato

        self._aguarda_carregamento()
        elementos = self.busca_elementos(tipo_seletor, seletor)
        textos = [funcao_formato(e.text)
                  for e in elementos if funcao_condicao(
                    e.text)]
        return textos

    def troca_frame(self, tipo_seletor=None, seletor_frame=None):
        """Troca o foco do river para outro frame."""
        self._aguarda_carregamento()

        if tipo_seletor is None or seletor_frame is None:
            self._driver.switch_to_default_content()
        else:
            self._wait.until(
                expected_conditions.frame_to_be_available_and_switch_to_it(
                    (tipo_seletor, seletor_frame)))


class ChromeDriver(DriverBase):
    """Driver Chrome auxiliar para selenium.webdriver."""

    def _encerra_driver(self):
        """Encerra a instância de webdriver."""
        self._driver.close()

    def _inicializa_driver(self):
        """Inicializa e configura uma instância de webdriver."""
        self._driver = webdriver.Chrome(self._caminho_driver)
