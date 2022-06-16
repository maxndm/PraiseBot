import requests
import re
import html

response = requests.get('https://lol.fandom.com/wiki/Category:Champion_Square_Images')

regex1 = '<img.*>'
regex2 = '(?<=src=\")(https.*?)(?=\")'
regex3 = '(?<=name=\")(.*?)(?=\.png)'

x = re.findall(regex1,response.text)
x = ' '.join(x)
links = re.findall(regex2,x)
names = re.findall(regex3,x)
name_index = 0
count = len(links)
# print(names)

for link in links:
    response = requests.get(link)
    name = names[name_index]+'.png'
    file = open(html.unescape(name),'wb')
    file.write(response.content)
    file.close()
    name_index+=1
    print(f'{name_index}/{count}')

print('all done')
