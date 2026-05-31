import http.server
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup
import time

# Diccionarios para traducir el texto de la interfaz a los códigos internos de LinkedIn
TIME_POSTED_MAP = {
    "Mes pasado": "r2592000",
    "Semana pasada": "r604800",
    "Últimas 24 horas": "r86400"
}

WORKPLACE_MAP = {
    "Presencial": "1",
    "En remoto": "2",
    "Híbrido": "3"
}

JOB_TYPE_MAP = {
    "Jornada completa": "F",
    "Media jornada": "P",
    "Contrato": "C",
    "Temporal": "T",
    "Voluntariado": "V",
    "Prácticas": "I"
}

EXPERIENCE_MAP = {
    "Prácticas": "1",
    "Sin experiencia": "2",
    "Algo de responsabilidad": "3",
    "Intermedio": "4",
    "Director": "5",
    "Ejecutivo": "6"
}

def translate_filter(values, mapping):
    """Traduce un string o lista de strings a sus códigos correspondientes usando el diccionario provisto."""
    if not values:
        return None
    if isinstance(values, str):
        values = [values]
        
    codes = []
    for val in values:
        # Buscamos ignorando mayúsculas/minúsculas
        matched = False
        for key, code in mapping.items():
            if key.lower() == val.lower():
                codes.append(code)
                matched = True
                break
        if not matched:
            # Si el usuario ya mandó el código directamente, lo usamos
            codes.append(val)
            
    return codes

def scrape_linkedin_jobs(query, location, max_rows, radius, filters_text):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    jobs_list = []
    start = 0
    max_rows = min(max_rows, 100) 
    
    # Procesamos los filtros de texto a los códigos que la API de LinkedIn entiende
    filters = {}
    
    # Por defecto "Semana pasada"
    tp = translate_filter(filters_text.get("fecha", "Semana pasada"), TIME_POSTED_MAP)
    if tp: filters["f_TPR"] = tp[0]
    
    # Por defecto todos: Remoto, Presencial, Híbrido
    wt = translate_filter(filters_text.get("modalidad", ["En remoto", "Presencial", "Híbrido"]), WORKPLACE_MAP)
    if wt: filters["f_WT"] = wt
    
    # Por defecto todos los tipos de empleo
    jt = translate_filter(filters_text.get("tipoEmpleo", ["Jornada completa", "Media jornada", "Contrato", "Temporal", "Voluntariado", "Prácticas"]), JOB_TYPE_MAP)
    if jt: filters["f_JT"] = jt
    
    exp = translate_filter(filters_text.get("experiencia"), EXPERIENCE_MAP)
    if exp: filters["f_E"] = exp

    # Construimos los parámetros adicionales de la URL
    extra_params = ""
    for key, val in filters.items():
        if val:
            if isinstance(val, list):
                val_str = "%2C".join(urllib.parse.quote(str(v)) for v in val)
            else:
                val_str = urllib.parse.quote(str(val))
            extra_params += f"&{key}={val_str}"
            
    while start < max_rows:
        # Hacer clic en la página es exactamente lo mismo que poner los códigos en esta URL
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(query)}&location={urllib.parse.quote(location)}&distance={radius}&start={start}{extra_params}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                break
        except Exception as e:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='base-card')
        if not cards:
            cards = soup.find_all('li')
            if not cards:
                break
        
        for card in cards:
            if len(jobs_list) >= max_rows:
                break
            
            title_elem = card.find('h3', class_='base-search-card__title')
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            location_elem = card.find('span', class_='job-search-card__location')
            link_elem = card.find('a', class_='base-card__full-link')
            date_elem = card.find('time')

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True) if title_elem else 'N/A'
            company = company_elem.get_text(strip=True) if company_elem else 'N/A'
            loc = location_elem.get_text(strip=True) if location_elem else 'N/A'
            link = link_elem.get('href') if link_elem else 'N/A'
            date = date_elem.get_text(strip=True) if date_elem else 'N/A'

            clean_link = link.split('?')[0] if link != 'N/A' else link
            
            description = ""
            employment_type = "N/A"
            seniority_level = "N/A"
            
            urn = card.get('data-entity-urn', '')
            if urn:
                job_id = urn.split(':')[-1]
                desc_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                try:
                    desc_resp = requests.get(desc_url, headers=headers, timeout=5)
                    if desc_resp.status_code == 200:
                        desc_soup = BeautifulSoup(desc_resp.text, 'html.parser')
                        
                        desc_elem = desc_soup.find('div', class_='show-more-less-html__markup')
                        if desc_elem:
                            description = desc_elem.get_text(separator='\n', strip=True)
                            
                        # Extraer criterios adicionales (Jornada, Seniority, etc.)
                        criteria_items = desc_soup.find_all('li', class_='description__job-criteria-item')
                        for item in criteria_items:
                            subheader = item.find('h3', class_='description__job-criteria-subheader')
                            text_span = item.find('span', class_='description__job-criteria-text')
                            if subheader and text_span:
                                sh_text = subheader.get_text(strip=True).lower()
                                val_text = text_span.get_text(strip=True)
                                if "employment type" in sh_text or "tipo de empleo" in sh_text:
                                    employment_type = val_text
                                elif "seniority" in sh_text or "nivel de antigüedad" in sh_text:
                                    seniority_level = val_text
                except:
                    pass
                time.sleep(0.5)
                
            # Buscar links y correos dentro de la descripción (ya que LinkedIn oculta el botón externo a invitados)
            import re
            emails_in_desc = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', description)
            urls_in_desc = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', description)
            # Limpiar y quitar duplicados y urls de linkedin
            apply_hints = list(set([u for u in urls_in_desc if 'linkedin.com' not in u] + emails_in_desc))

            # Determinar si es remoto leyendo la ubicación y el título
            is_remote = "remot" in loc.lower() or "remot" in title.lower()

            # Determinar si es Easy Apply (Solicitud sencilla)
            is_easy_apply = False
            if 'desc_soup' in locals():
                buttons = desc_soup.find_all('button')
                for btn in buttons:
                    text = btn.get_text(strip=True).lower()
                    if "easy apply" in text or "solicitud sencilla" in text:
                        is_easy_apply = True
                        break

            jobs_list.append({
                "search_query": query,
                "title": title,
                "company": company,
                "location": loc,
                "is_remote": is_remote,
                "is_easy_apply": is_easy_apply,
                "employment_type": employment_type,
                "seniority_level": seniority_level,
                "published_date": date,
                "apply_hints": apply_hints,
                "description": description,
                "link": clean_link
            })
            
        start += 25
        time.sleep(1)
        
    return {"status": "success", "total_jobs_found": len(jobs_list), "jobs": jobs_list}

class LinkedinScraperHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/scrape':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                
                query = payload.get("query", "")
                location = payload.get("location", "")
                max_rows = payload.get("maxRows", 25)
                radius = payload.get("radius", "25")
                include_description = payload.get("includeDescription", False)
                
                if not query or not location:
                    raise ValueError("Please provide at least 'query' and 'location' in your JSON.")
                
                # Pasamos el JSON completo para extraer los filtros de texto
                results = scrape_linkedin_jobs(query, location, max_rows, radius, payload)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(results, indent=2).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = 8081
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, LinkedinScraperHandler)
    print(f"LinkedIn Scraper API listening on port {port}...")
    httpd.serve_forever()
