import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
import os
from pathlib import Path
import hashlib
from typing import Dict, List, Optional

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

# Update the usage example
if __name__ == "__main__":
    scraper = WebScraper("https://www.wildriftfire.com")
    content = scraper.scrape(max_depth=3)  # Adjust max_depth as needed
    
    # Count total images across all pages
    def count_images(content_dict):
        total = len(content_dict.get('images', []))
        for sub_page in content_dict.get('sub_pages', {}).values():
            total += count_images(sub_page)
        return total
    
    total_images = count_images(content)
    print(f"Total images scraped: {total_images}")