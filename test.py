from bs4 import BeautifulSoup

# Example HTML content
html_content = "<html><head><title>Test Page</title></head><body><p>Hello World!</p> <h1>header1</h1><p>Hi</p></body></html>"
soup = BeautifulSoup(html_content, 'html.parser')

# Prettify the soup object
pretty_html = soup.prettify()
print(soup.body.find_all(['p', 'h1'])[-1].get_text())
