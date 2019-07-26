from xhtml2pdf import pisa
import urllib.request as ur
from bs4 import BeautifulSoup


def convert_html_to_pdf(sourceHtml, outputFilename):
    resultFile = open(outputFilename, "w+b")
    pisaStatus = pisa.CreatePDF(sourceHtml, resultFile)
    resultFile.close()
    return pisaStatus.err


def urls_to_pdf(url, article_no, file_name):
    website = ur.urlopen(url)
    html = website.read()

    soup = BeautifulSoup(html, "html5lib")
    s = soup.find_all('article')
    for div in s[0].find_all("div", {'class': 'recommendedPostsDiv'}):
        div.decompose()

    for div in s[0].find_all("div", {'class': 'author_info_box'}):
        div.decompose()

    for div in s[0].find_all("div", {'clear hideIt'}):
        div.decompose()
    for div in s[0].find_all("div", {'personalNoteHeader'}):
        div.decompose()
    for div in s[0].find_all("div", {'collapsableDivPersonalNotes'}):
        div.decompose()
    for div in s[0].find_all("div", {'improvedBy'}):
        div.decompose()
    for div in s[0].find_all("footer", {'entry-meta'}):
        div.decompose()
    for div in s[0].find_all("div", {'class': 'editor-buttons'}):
        div.decompose()
    for div in s[0].find_all("div", {'class': 'output-block'}):
        div.decompose()
    for div in s[0].find_all("a", {'target': '_blank'}):
        div.decompose()

    s[0] = str(s[0])
    s[0] += '''<div style="width: 100%; height: 20px; border-bottom: 1px solid black; text-align: center">
                <span style="font-size: 10px; background-color: #F3F5F6; padding: 0 10px;">''' + 'article number : ' + str(article_no) + '''</span></div>'''

    with open(file_name + ".html", "a+", encoding='utf-8') as file:
        file.write(str(s[0]))


def get_all_links(url, file_name):
    article_no = 1
    website = ur.urlopen(url)

    html = website.read()

    soup = BeautifulSoup(html, "html.parser")
    s = soup.find_all('article')
    for div in s[0].find_all("div", {'class':'recommendedPostsDiv'}):
        div.decompose()

    for div in s[0].find_all("div", {'class':'author_info_box'}):
        div.decompose()

    for div in s[0].find_all("div", {'clear hideIt'}):
        div.decompose()
    for div in s[0].find_all("div", {'personalNoteHeader'}):
        div.decompose()
    for div in s[0].find_all("div", {'collapsableDivPersonalNotes'}):
        div.decompose()
    for div in s[0].find_all("div", {'improvedBy'}):
        div.decompose()
    for div in s[0].find_all("footer", {'entry-meta'}):
        div.decompose()
    soup = str(s[0])
    soup = BeautifulSoup(soup)
    for link in soup.findAll('a', href=True):
        try:
            urls_to_pdf(str(link['href']), article_no, file_name)
            article_no += 1
            print(link['href'])
        except:
            print(link['href'], 'link not working')
            pass

    for div in s[0].find_all("a", {'target':'_blank'}):
        div.decompose()


if __name__ == '__main__':
    # print('Enter the url: ')
    # url = input()
    # print('Enter the file name with which you want to save')
    # fila_name = input()
    # get_all_links(url, fila_name)
    urls_to_pdf('https://www.geeksforgeeks.org/english-reading-comprehension-set-1/', 0, 'cognizant')
    # file = codecs.open(file_name + ".html", 'r', encoding='utf-8')
    # convert_html_to_pdf(str(file.read()), file_name + '.pdf')

