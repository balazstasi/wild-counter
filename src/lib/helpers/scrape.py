import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import geckodriver_autoinstaller
import concurrent.futures
import sys
import os

@dataclass
class GameElement:
    id: int
    name: str
    image_url: str
    description: str
    element_type: Literal["item", "rune"]
    stats: Dict[str, str]  # For items
    price: str  # For items
    build_path: List[str]  # For items
    builds_into: List[str]  # For items

class WebScraper:
    def __init__(self, base_url: str, output_dir: str = "scraped_content"):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.visited_urls = set()
        
        # Create base output directory
        self.output_dir.mkdir(exist_ok=True)

    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse page content"""
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all relevant images from the page"""
        images = []
        
        # Find all img tags
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
                
            # Handle relative URLs
            if src.startswith("/"):
                src = f"{self.base_url.rstrip('/')}{src}"
            elif not src.startswith(("http://", "https://")):
                src = f"{self.base_url.rstrip('/')}/{src.lstrip('/')}"
                
            images.append({
                "url": src,
                "alt": img.get("alt", ""),
                "title": img.get("title", "")
            })
            
        return images

    def get_path_from_url(self, url: str) -> str:
        """Extract path from URL and convert to folder structure"""
        # Remove base URL and query parameters
        path = url.replace(self.base_url, '').split('?')[0].strip('/')
        # Use 'root' for homepage
        return path if path else 'root'

    def download_image(self, image_url: str, url_path: str) -> Optional[str]:
        """Download and save image, return saved path"""
        try:
            response = self.session.get(image_url, stream=True)
            response.raise_for_status()
            
            # Get original filename from URL
            original_filename = image_url.split('/')[-1]
            
            # Create directory structure based on URL path
            image_dir = self.output_dir / url_path / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = image_dir / original_filename
            
            # Save image in its original format
            image = Image.open(io.BytesIO(response.content))
            image.save(filepath, format=image.format if image.format else 'JPEG')
            
            return str(filepath)
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")
            return None

    def extract_text(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract relevant text content"""
        return {
            "title": soup.title.string if soup.title else "",
            "meta_description": soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else "",
            "headings": [h.text.strip() for h in soup.find_all(["h1", "h2", "h3"])],
            "paragraphs": [p.text.strip() for p in soup.find_all("p") if p.text.strip()],
        }

    def get_all_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all internal links from the page"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                links.append(f"{self.base_url}{href}")
            elif href.startswith(self.base_url):
                links.append(href)
            elif not href.startswith(('http://', 'https://', 'mailto:', '#')):
                links.append(f"{self.base_url}/{href.lstrip('/')}")
        return links

    def scrape(self, url: str = None, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Main scraping method with recursive functionality"""
        if current_depth >= max_depth:
            return {}
        
        url = url or self.base_url
        if url in self.visited_urls:
            return {}
        
        self.visited_urls.add(url)
        url_path = self.get_path_from_url(url)
        print(f"Scraping: {url} (depth: {current_depth}) -> {url_path}")
        
        soup = self.get_page_content(url)
        if not soup:
            return {}
        
        # Extract content from current page
        images = self.extract_images(soup)
        text = self.extract_text(soup)
        
        # Download images
        downloaded_images = []
        for img in images:
            saved_path = self.download_image(img["url"], url_path)
            if saved_path:
                downloaded_images.append({
                    **img,
                    "local_path": saved_path
                })
        
        # Save text content
        content_dir = self.output_dir / url_path
        content_dir.mkdir(parents=True, exist_ok=True)
        with open(content_dir / "content.txt", "w", encoding="utf-8") as f:
            f.write(f"Title: {text['title']}\n")
            f.write(f"Meta Description: {text['meta_description']}\n")
            f.write("\nHeadings:\n")
            for h in text['headings']:
                f.write(f"- {h}\n")
            f.write("\nParagraphs:\n")
            for p in text['paragraphs']:
                f.write(f"{p}\n\n")
        
        # Get all internal links and recursively scrape them
        all_content = {
            "images": downloaded_images,
            "text": text,
            "sub_pages": {}
        }
        
        for link in self.get_all_links(soup):
            if link not in self.visited_urls:
                sub_content = self.scrape(link, max_depth, current_depth + 1)
                if sub_content:
                    all_content["sub_pages"][link] = sub_content
        
        return all_content

class WildRiftScraper:
    ELEMENT_CONFIGS = {
        "item": {
            "max_id": 196,
            "relation_type": "Item",
            "output_file": "wild_rift_items.json",
            "html_dir": "item_html"
        },
        "rune": {
            "max_id": 133,
            "relation_type": "Rune",
            "output_file": "wild_rift_runes.json",
            "html_dir": "rune_html"
        }
    }

    def __init__(self, output_dir: str = ".", element_type: Literal["item", "rune"] = "item"):
        self.base_url = "https://www.wildriftfire.com"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.element_type = element_type
        self.config = self.ELEMENT_CONFIGS[element_type]
        
        self.html_dir = self.output_dir / self.config["html_dir"]
        self.html_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest"
        })

    def fetch_element_html(self, element_id: int) -> Optional[str]:
        """Fetch HTML content for a game element"""
        try:
            url = f"{self.base_url}/ajax/tooltip?relation_type={self.config['relation_type']}&relation_id={element_id}"
            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
                # Save HTML content to file
                os.makedirs(self.config['html_dir'], exist_ok=True)
                html_file_path = os.path.join(self.config['html_dir'], f"{self.element_type}_{element_id}.html")
                with open(html_file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                return html_content
            return None
        except Exception as e:
            print(f"Error fetching {self.element_type} {element_id}: {e}")
            return None

    def parse_element_html(self, html_content: str, element_id: int) -> GameElement:
        soup = BeautifulSoup(html_content, 'html.parser')
        name_elem = soup.find("div", class_="tt__info__title").find("span")
        name = name_elem.text.strip() if name_elem else "Unknown"
        
        image_elem = soup.find("div", class_="tt__image").find("img")
        image_url = f"https://www.wildriftfire.com{image_elem['src']}" if image_elem else ""
        
        if self.element_type == "item":
            price_elem = soup.find("div", class_="tt__info__cost").find("span")
            price = price_elem.text.strip() if price_elem else ""
            
            stats_elem = soup.find("div", class_="tt__info__stats")
            stats = {}
            if stats_elem:
                for stat in stats_elem.find_all("div"):
                    stat_text = stat.text.strip()
                    if ":" in stat_text:
                        key, value = stat_text.split(":", 1)
                        stats[key.strip()] = value.strip()
            
            description_elem = soup.find("div", class_="tt__info__uniques")
            description = description_elem.text.strip() if description_elem else ""
        else:  # rune
            description_elem = soup.find("div", class_="tt__info__uniques")
            if description_elem:
                span_elem = description_elem.find("span")
                description = span_elem.text.strip() if span_elem else description_elem.text.strip()
            else:
                description = ""
            price = ""
            stats = {}
        
        return GameElement(
            id=element_id,
            name=name,
            image_url=image_url,
            description=description,
            element_type=self.element_type,
            stats=stats,
            price=price,
            build_path=[],
            builds_into=[]
        )

    def fetch_and_parse_element(self, element_id: int) -> Optional[Dict]:
        """Fetch and parse a single game element"""
        html_content = self.fetch_element_html(element_id)
        if html_content:
            element_data = self.parse_element_html(html_content, element_id)
            if element_data:
                return asdict(element_data)
        return None

    def scrape_elements(self, start_id: int = 1) -> List[Dict]:
        """Scrape all elements using multiple threads"""
        elements = []
        end_id = self.config["max_id"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {
                executor.submit(self.fetch_and_parse_element, element_id): element_id
                for element_id in range(start_id, end_id + 1)
            }
            
            for future in concurrent.futures.as_completed(future_to_id):
                element_id = future_to_id[future]
                try:
                    element_data = future.result()
                    if element_data:
                        elements.append(element_data)
                        print(f"Successfully processed {self.element_type} {element_id}: {element_data['name']}")
                except Exception as e:
                    print(f"Error processing {self.element_type} {element_id}: {e}")
        
        # Save all elements at once
        self.save_to_json(elements)
        return elements

    def save_to_json(self, elements: List[Dict]):
        """Save scraped elements to JSON file"""
        output_file = self.output_dir / self.config["output_file"]
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({f"{self.element_type}s": elements}, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(elements)} {self.element_type}s to {output_file}")

def main():
    # Scrape items
    item_scraper = WildRiftScraper(element_type="item")
    items = item_scraper.scrape_elements()
    item_scraper.save_to_json(items)
    
    # Scrape runes
    rune_scraper = WildRiftScraper(element_type="rune")
    runes = rune_scraper.scrape_elements()
    rune_scraper.save_to_json(runes)

if __name__ == "__main__":
    element_type = sys.argv[1] if len(sys.argv) > 1 else "item"
    scraper = WildRiftScraper(element_type=element_type)
    scraper.scrape_elements()