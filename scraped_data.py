import requests
from bs4 import BeautifulSoup
import csv
import re

pattern = re.compile(r"[^a-zA-Z0-9\u0621-\u064A]+")
pattern1 = re.compile(r'[\x00-\x20\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+')
pattern2 = re.compile(r'[\s+]')


def get_page_links():
    """
    This function will return a list of links to all the pages of the forum
    """
    with open("scraped_data.txt", "w") as file:
        for i in range(2, 872):
            file.write("https://www.tawjihnet.net/vb/forums/26/page-" + str(i) + "\n")

def extract_thread_classes(url):
    """
    this function will extract the thread classes from a given page
    """

    # send an HTTP GET request to the URL and get the page source HTML code
    response = requests.get(url)
    html = response.content

    # parse the HTML code using BeautifulSoup's BeautifulSoup class
    soup = BeautifulSoup(html, 'html.parser')
    class_list = []
    for tag in soup.find_all(class_=True):
        class_list.extend(tag['class'])
    c = [ c.split('-')[-1] for c in class_list if c.startswith('js-threadListItem') ]
    print(c)
    with open("question_links.txt", "a") as file:
        for i in c:
            file.write("https://www.tawjihnet.net/vb/threads/" + str(i) + "\n")


with open("scraped_data.txt", "r") as file:
    for line in file:
        line = line.strip()
        print('extracting from: |{}|'.format(line))
        extract_thread_classes(line)

with open("question_links.txt", "r") as file:
    header = ['index', 'questions', 'answers']
    i = 0
    with open('scraped_dataPPP.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for line in file:
            print('\r{} / 17442'.format(i))
            i = i + 1
            line = line.strip()
            response = requests.get(line)
            soup = BeautifulSoup(response.content, "html.parser")
            divs = soup.find_all(class_="message-body")
            try:
                content = []
                for div in divs:
                    content.append(div.text.strip())
                content = [ pattern.sub(' ', c) for c in content if c != '' ]
                content = [ pattern2.sub(' ', c) for c in content]
                q = content[0]
                a = " ".join(content[1:])
                a = a.replace(',', ' ').replace('\n', '').replace('\t', ' ')
                if len(a) < 25 and len(q) < 25:
                    continue
                line_outpu = "'{}', '{}', '{}'\n".format(line, q, a)
                writer.writerow([i, q, a])
            except Exception as e:
                print(e)
