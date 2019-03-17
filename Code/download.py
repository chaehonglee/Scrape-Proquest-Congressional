import csv

import urllib2


def download(congress, filename):
    """
    Simple function to download files from given URL
    :return: None
    """
    count = 0
    with open(filename, 'r') as f:
        readcsv = csv.DictReader(f)
        for row in readcsv:
            try:
                resp = urllib2.urlopen(row['URL'])
                with open('../Old_hearing_transcripts_pdf/' + row['File Name'] + '.pdf', 'wb') as pdf:
                    pdf.write(resp.read())
                    pdf.close()
                count += 1
            except:
                pass
    print('Download completed for Congress %d' % congress)
    print('Total of %d files downloaded.' % count)
    return


if __name__ == '__main__':
    download(104, '../Old_hearing_processing/meta_congress_104.csv')
    download(103, '../Old_hearing_processing/meta_congress_103.csv')
    download(102, '../Old_hearing_processing/meta_congress_102.csv')
    download(98, '../Old_hearing_processing/meta_congress_98.csv')
    download(93, '../Old_hearing_processing/meta_congress_93.csv')
    download(88, '../Old_hearing_processing/meta_congress_88.csv')
