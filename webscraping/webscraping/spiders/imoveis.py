import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from scrapy.http import HtmlResponse


class ImoveisSeleniumSpider(scrapy.Spider):
    name = 'imoveis_selenium'
    start_urls = ['https://www.baseimobiliarias.com.br/']

    def __init__(self, *args, **kwargs):
        super(ImoveisSeleniumSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)

        # Realiza a interação com a caixa de seleção
        checkbox = self.driver.find_element_by_css_selector('#finalidade-input')
        checkbox.click()

        # Seleciona a opção de "compras"
        compras_option = self.driver.find_element_by_css_selector('body > div.banner > div > div > div > div > div > div:nth-child(1) > div:nth-child(1) > div > div > div > ul > li.selected.active > a > span.text')
        compras_option.click()

        # Clica no botão de pesquisa
        search_button = self.driver.find_element_by_css_selector('body > div.banner > div > div > div > div > div > div:nth-child(2) > div:nth-child(3) > div > button')
        search_button.click()

        # Espera a página carregar e obtém o HTML
        response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

        # Selecionar links para os anúncios de imóveis à venda
        for anuncio in response.css('div.listing-title a::attr(href)').getall():
            yield response.follow(anuncio, self.parse_anuncio)

        # Seguir para a próxima página, se disponível
        next_page = response.css('a.next.page-numbers::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_anuncio(self, response):
        yield {
            'titulo': response.css('h1::text').get(),
            'preco': response.css('span.price::text').get(),
            'descricao': response.css('div.description::text').get(),
            'endereco': response.css('span.address::text').get(),
            'quartos': response.css('span.rooms::text').get(),
            'banheiros': response.css('span.bathrooms::text').get(),
            'garagem': response.css('span.garage::text').get(),
        }

    def closed(self, reason):
        self.driver.quit()