import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

def baixar_sitemap_e_extrair_urls(url_sitemap):
    """
    Baixa o sitemap XML (VTEX) e extrai todas as URLs de produtos.
    Retorna uma lista de URLs.
    """
    response = requests.get(url_sitemap)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'xml')
    loc_tags = soup.find_all('loc')

    urls = []
    for tag in loc_tags:
        if tag.text:
            urls.append(tag.text.strip())
    return urls

def extrair_informacoes_produto(url_produto):
    """
    Acessa a página do produto (VTEX), faz o parse do HTML
    e tenta extrair:
      - nome_produto => da primeira div depois do h1.mz-product-name
      - conteudo => todo texto <p> encontrado (descrição e/ou detalhes).
    Retorna um dicionário com:
      { 'url': ..., 'nome_produto': ..., 'conteudo': ... }
    """
    try:
        response = requests.get(url_produto)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1) Localiza a tag h1 com classe "mz-product-name"
        h1_produto = soup.find('h1', class_='mz-product-name')
        if h1_produto:
            # Pega o próximo elemento 'div' após a tag h1
            # Pode ser o irmão seguinte (next_sibling), ou 
            # usar find_next() de forma mais robusta:
            nome_div = h1_produto.find_next('div')
            # Se a div for mesmo o elemento que contém o nome, pegamos o texto
            if nome_div:
                nome_produto = nome_div.get_text(strip=True)
            else:
                nome_produto = "Nome não encontrado"
        else:
            nome_produto = "Tag h1.mz-product-name não encontrada"

        # 2) Coletar todo o texto das tags <p> (conteudo)
        # Vamos juntar todos os <p> em uma string
        paragraphs = soup.find_all('p')
        # Filtrar apenas o texto e unir com quebras de linha
        conteudo = "\n".join(p.get_text(strip=True) for p in paragraphs)

        return {
            'url': url_produto,
            'nome_produto': nome_produto,
            'conteudo': conteudo
        }

    except Exception as e:
        print(f"Erro ao processar URL {url_produto}: {e}")
        return {
            'url': url_produto,
            'nome_produto': 'Erro',
            'conteudo': ''
        }

def main():
    load_dotenv()
    url_sitemap = os.getenv("VTEX_URL")

    print("Baixando sitemap e extraindo URLs de produtos...")
    urls_produtos = baixar_sitemap_e_extrair_urls(url_sitemap)
    print(f"Foram encontradas {len(urls_produtos)} URLs de produtos.")

    lista_produtos = []
    for url in urls_produtos:
        print(f"Processando: {url}")
        dados = extrair_informacoes_produto(url)
        lista_produtos.append(dados)

    # Salvar todos os produtos num único arquivo JSON
    nome_arquivo_json = "content/produtos_coletados.json"
    with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(lista_produtos, f, indent=2, ensure_ascii=False)

    print(f"Todos os produtos foram salvos em: {nome_arquivo_json}")

if __name__ == "__main__":
    main()
