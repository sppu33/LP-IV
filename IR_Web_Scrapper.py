import requests
from bs4 import BeautifulSoup
from xlwt import Workbook
import time

# Web Crawler
workbook = Workbook(encoding='utf-8')
sheet = workbook.add_sheet('HackerNews')
sheet.write(0, 0, 'Number')
sheet.write(0, 1, 'Title')
sheet.write(0, 2, 'Link')
sheet.write(0, 3, 'Points')
sheet.write(0, 4, 'Submitter')

url = "https://news.ycombinator.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

print("Fetching Hacker News homepage...")
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch page! Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.content, 'lxml')

# Find story rows
story_rows = soup.find_all('tr', class_='athing')
print(f"Found {len(story_rows)} stories.")

line = 1
for num, story in enumerate(story_rows[:50], start=1):  # Top 50
    try:
        title_tag = story.find('a', class_='storylink')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            if link.startswith('/'):
                link = "https://news.ycombinator.com" + link
        else:
            title = "No title"
            link = "N/A"

        # Get subtext row (points, submitter)
        subtext_row = story.find_next_sibling('tr')
        subtext = subtext_row.find('td', class_='subtext') if subtext_row else None
        if subtext:
            points_tag = subtext.find('span', class_='score')
            points = points_tag.get_text(strip=True) if points_tag else '0 points'
            user_tag = subtext.find('a', class_='hnuser')
            submitter = user_tag.get_text(strip=True) if user_tag else 'N/A'
        else:
            points = '0 points'
            submitter = 'N/A'

        # Print progress
        print(f"{num}. {title}")
        print(f"Link: {link}")
        print(f"Points: {points}, Submitter: {submitter}")
        print("-"*50)

        # Write to Excel
        sheet.write(line, 0, num)
        sheet.write(line, 1, title)
        sheet.write(line, 2, link)
        sheet.write(line, 3, points)
        sheet.write(line, 4, submitter)
        line += 1

        time.sleep(0.2)  

    except Exception as e:
        print(f"Skipped a story due to error: {e}")
        continue


workbook.save('hackernews_top50.xls')
print("Excel file saved as hackernews_top50.xls")
