import os
import json
import requests
from bs4 import BeautifulSoup
from time import sleep
from dotenv import load_dotenv

def baixar_sitemap_e_extrair_urls(url_sitemap):
    try:
        response = requests.get(url_sitemap)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar o sitemap {url_sitemap}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'xml')
    loc_tags = soup.find_all('loc')

    urls = []
    for tag in loc_tags:
        if not tag.text:
            continue
        url = tag.text.strip()
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        urls.append(url)
    return urls

def extrair_conteudo_post(url_post):
    try:
        response = requests.get(url_post, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo = soup.find('h1')
        titulo_texto = titulo.get_text(strip=True) if titulo else 'Sem título'

        content_div = soup.find(class_='textos')
        if content_div:
            parags = content_div.find_all('p')
            conteudo = "\n".join(p.get_text(strip=True) for p in parags)
        else:
            conteudo = soup.get_text(separator='\n', strip=True)

        return {
            'url': url_post,
            'titulo': titulo_texto,
            'conteudo': conteudo
        }

    except Exception as e:
        print(f"Erro ao processar {url_post}: {e}")
        return {
            'url': url_post,
            'titulo': 'Erro',
            'conteudo': ''
        }

def main():
    load_dotenv()
    base_url = os.getenv('WORDPRESS_MM_URL')  # Exemplo: https://www.meioemensagem.com.br/post-sitemap

    if not base_url:
        print("❌ Variável de ambiente WORDPRESS_MM_URL não definida.")
        return

    todos_os_posts = []

    for i in range(1, 76):
        url_sitemap = f"{base_url}{i}.xml"
        print(f"\n📥 Lendo sitemap {i}: {url_sitemap}")
        urls = baixar_sitemap_e_extrair_urls(url_sitemap)
        print(f"✔️ {len(urls)} URLs encontradas")

        for idx, url in enumerate(urls, 1):
            print(f"   → ({idx}/{len(urls)}) Processando: {url}")
            post = extrair_conteudo_post(url)
            todos_os_posts.append(post)
            sleep(0.5)  # opcional: reduz chance de bloqueio

    with open("posts_coletados_mm_total.json", 'w', encoding='utf-8') as f:
        json.dump(todos_os_posts, f, indent=2, ensure_ascii=False)

    print("\n✅ Todos os posts foram salvos em: posts_coletados_mm_total.json")

if __name__ == "__main__":
    main()
