from bs4 import BeautifulSoup
import urllib.request

base_url = "https://www.pref.aichi.jp"

def download_pdf(url):
    page_url = base_url + url
    raw_html = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(raw_html, "html.parser")
    for aa in soup.find_all("a"):
        link = aa.get("href")
        name = aa.get_text()
        if "県内発生事例一覧" in name:
            table_link = link
            break
    return table_link  
    
if __name__ == "__main__":
    page_link = "/site/covid19-aichi/kansensya-kensa.html"
    print(download_pdf(page_link))