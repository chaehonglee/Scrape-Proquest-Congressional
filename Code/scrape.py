import re
import csv

import requests
from bs4 import BeautifulSoup


class ScrapeProquest():

    def __init__(self, congressN):
        self.congress = str(congressN)

        with open('../Old_hearing_processing/meta_congress_' + str(congressN) + 'csv', 'w') as f:
            # Initiate meta log file
            writecsv = csv.writer(f)
            writecsv.writerow(
                ('Congress', 'Title', 'Citation', 'Sudoc', 'Committee', 'Hearing Date', 'File Name', 'URL'))

    def run(self, cookie=None, pgId=None, rsId=None):
        """
        Manually scrapes info from congressional.proquest.com
        :param congressN: Congress number
        :param cookie: manually saved cookie info from Chrome inspection
        :param pgId: manually saved pgId generated from network GET request
        :param rsId: manually saved rsId generated from network GET request
        :return:
        """
        # Manual initial session ID (this may be subject to change depending on the user/IP):
        results_link = 'https://congressional.proquest.com/congressional/result/pqpresultpage?'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': cookie,
            'Host': 'congressional.proquest.com',
            'Referer': 'Fill in by inspecting Chrome Network Inspection',
            'Upgrade-Insecure-Requests': 'Fill in by inspecting Chrome Network Inspection',
            'User-Agent': 'Fill in by inspecting Chrome Network Inspection'
        }
        query = {
            'accountid': 'Fill in by inspecting Chrome Network Inspection',
            'groupid': 'Fill in by inspecting Chrome Network Inspection',
            'pgId': pgId,
            'rsId': rsId
        }

        # Start a session with the specified headers & query
        s = requests.Session()
        s.headers.update(headers)

        # Excel sheet to save info in
        with open('../Old_hearing_processing/meta_congress_' + self.congress + '.csv', 'a') as f:
            writecsv = csv.writer(f)

            count = 0
            while True:
                # Find all result entries
                r = s.post(results_link, query)
                soup = BeautifulSoup(r.content, 'html.parser')
                results_itm = soup.find_all('div', {'class': 'resItem-inner1'})

                # 20 entries per page, scrape their info
                for itm in results_itm:
                    count += 1

                    title = [itm.findChild('a', {'title': 'Link to item'}).text]

                    spans = itm.findChild('div', {'class': 'field-row'}).findChildren('span')
                    tempstr = ''
                    try:
                        for span in spans:
                            tempstr += span.text
                        try:
                            regex = r"[\s\S]*Citation: (.*).*Sudoc: (.*).*Committee: (.*)"
                            matches = re.findall(regex, tempstr)[0]
                            citation = matches[0]
                            sudoc = matches[1]
                            committee = matches[2]
                        except:
                            try:
                                regex = r"[\s\S]*Citation: (.*).*Sudoc: (.*).*"
                                matches = re.findall(regex, tempstr)[0]
                                citation = matches[0]
                                sudoc = matches[1]
                                committee = 'not found'
                            except:
                                citation = 'not found'
                                sudoc = 'not found'
                                committee = 'not found'
                    except:
                        citation = 'not found'
                        sudoc = 'not found'
                        committee = 'not found'

                    hearing_date = self.between(itm.findChild('div', {'class': 'snippet rtl_font_size'}).text,
                                                'Hearing Date: ', '')
                    file_name = 'Congress_' + self.congress + '_' + str(count)

                    # ----------- Dirty, but gets the pdf link by opening the permanent link ----------- #
                    pdflink = itm.findChild('ul', {
                        'class': 'horizontal clear_left rtl_float_right rtl_clear_none rtl_IeR iconsRow'}).findChild(
                        'div', {
                            'class': 'hiddenNoteBox'}).findChild('a')['href']
                    resp = s.post(pdflink, query)
                    url = self.between(resp.text, 'PDF - Full Text', 'Replica of Original - Complete')
                    url = 'https://congressional.proquest.com' + self.between(url, 'href=\"', '\" target=')
                    # ---------------------------------------------------------------------------- #

                    writecsv.writerow(
                        (self.congress, str(title)[3:-2], citation, sudoc, committee, hearing_date, file_name, url))

                print("Congress %s, %d documents found" % (self.congress, count))

                # Find the "Next Page" button
                next_pg = soup.find('a', {'title': 'Next page'})
                if next_pg is None:
                    break
                else:
                    next_pg_link = 'https://congressional.proquest.com' + next_pg['href']

                    # Force direct to next page
                    r = s.get(next_pg_link)

                    # Update query with response header
                    query['pgId'] = self.between(r.history[0].headers['Location'], 'pgId=', '&')
                    query['rsId'] = self.between(r.history[0].headers['Location'], 'rsId=', '')

            print('Found total of %d items for Congress %s' % (count, self.congress))
            return

    @staticmethod
    def between(value, a, b):
        """
        Simple Regex to find str in between
        :param value: str
        :param a: start str
        :param b: end str
        :return: str
        """
        pos_a = value.find(a)
        if pos_a == -1:
            return ""
        pos_b = value.rfind(b)
        if pos_b == -1:
            return ""
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b:
            return ""
        return value[adjusted_pos_a:pos_b]


if __name__ == '__main__':
    CPQ = ScrapeProquest(88)
    CPQ.run(cookie='Fill in by inspecting Chrome Network Inspection',
            pgId='Fill in by inspecting Chrome Network Inspection',
            rsId='Fill in by inspecting Chrome Network Inspection')
