url = 'https://vnexpress.net/nhom-hoi-thanh-duc-chua-troi-me-dung-70-kich-ban-thao-tung-nguoi-5069142.html'
import requests
from bs4 import BeautifulSoup
def get_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1', class_='title-detail').get_text()
    content = soup.find('article', class_='fck_detail').get_text()
    return title,content
title,content = get_content(url)
print(title, content)