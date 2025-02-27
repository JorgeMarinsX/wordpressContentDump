import os
from dotenv import load_dotenv
import requests
import json
from bs4 import BeautifulSoup

def baixar_sitemap_e_extrair_urls(url_sitemap):
    """
    Baixa o sitemap XML e extrai todas as URLs dos posts,
    ignorando links para imagens (terminadas em .jpg, .jpeg e .png).
    Retorna uma lista de URLs.
    """
    response = requests.get(url_sitemap)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'xml')
    loc_tags = soup.find_all('loc')

    urls = []
    for tag in loc_tags:
        if not tag.text:
            continue
        
        url = tag.text.strip()
        url_lower = url.lower()
        
        # Ignora se a URL termina com .jpg, .jpeg ou .png
        if url_lower.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            print(f"Ignorando URL de imagem: {url}")
            continue
        
        urls.append(url)
    return urls

def extrair_conteudo_post(url_post):
    """
    Acessa a página do post, faz o parse do HTML
    e tenta extrair o título (tag <h1>) e o conteúdo principal 
    (classe 'elementor-widget-theme-post-content').
    Retorna um dicionário com 'url', 'titulo' e 'conteudo'.
    """
    try:
        response = requests.get(url_post)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Busca o H1 principal
        h1_element = soup.find('h1')
        titulo = h1_element.get_text(strip=True) if h1_element else 'Sem título'

        # Localiza o container do conteúdo
        content_div = soup.find(class_='elementor-widget-theme-post-content')
        if content_div:
            # Seleciona todas as tags <p> filhas
            paragraphs = content_div.find_all('p')
            # Une o texto de cada parágrafo
            conteudo = "\n".join(p.get_text(strip=True) for p in paragraphs)
        else:
            # Se não encontrar a classe, obtém o texto de toda a página como fallback
            conteudo = soup.get_text(separator='\n', strip=True)

        return {
            'url': url_post,
            'titulo': titulo,
            'conteudo': conteudo
        }
    except Exception as e:
        print(f"Erro ao processar URL {url_post}: {e}")
        return {
            'url': url_post,
            'titulo': 'Erro',
            'conteudo': ''
        }

def main():
    load_dotenv()
    url_sitemap = os.getenv("WORDPRESS_URL")

    print("Baixando sitemap e extraindo URLs...")
    urls_posts = baixar_sitemap_e_extrair_urls(url_sitemap)
    print(f"Foram encontradas {len(urls_posts)} URLs (não de imagens).")

    todos_os_posts = []
    for url in urls_posts:
        print(f"Processando: {url}")
        dados_post = extrair_conteudo_post(url)
        todos_os_posts.append(dados_post)

    # Salva todos os posts em um único arquivo JSON
    nome_arquivo_json = "content/posts_coletados.json"
    with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(todos_os_posts, f, indent=2, ensure_ascii=False)

    print(f"Todos os posts foram salvos em: {nome_arquivo_json}")

if __name__ == "__main__":
    main()
