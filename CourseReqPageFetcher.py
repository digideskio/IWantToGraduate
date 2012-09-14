import httplib, urllib

def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()

headers = {
#'Host' : 'sdb.admin.washington.edu',
#'Connection' : 'keep-alive',
#'Content-Length' : '179',
#'Cache-Control' : 'max-age=0',
#'Origin' : 'http://www.washington.edu',
'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
'Content-Type' : 'application/x-www-form-urlencoded',
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Referer' : 'http://www.washington.edu/students/timeschd/genedinq.html',
#'Accept-Encoding' : 'gzip,deflate,sdch',
'Accept-Language' : 'en-US,en;q=0.8',
'Accept-Charset' : 'gb18030,utf-8;q=0.7,*;q=0.3',
#'Cookie' : '__unam=736a372-1371492887c-2498d28c-8; ASPSESSIONIDCADDDQST=IHEHKIFAMJOOJEPJONLOKGEL; __utma=80390417.2007068299.1317506665.1345920025.1345957806.181; __utmb=80390417.8.10.1345957806; __utmc=80390417; __utmz=80390417.1345920025.180.24.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)'
}
#httpServ = httplib.HTTPConnection('http://sdb.admin.washington.edu', 80)
httpServ = httplib.HTTPConnection('sdb.admin.washington.edu')
httpServ.connect()

params = urllib.urlencode({'QTRYR' : 'AUT 2012',
'REQ' : '1',
'STARTTIME' : '0000',
'ENDTIME' : '2400',
'STARTCREDIT' : '0',
'ENDCREDIT' : '4',
'STARTCOURSE' : '000',
'ENDCOURSE' : '999',
'SEATTLE' : 'Y',
'submit1' : 'Find open courses',
'NEXTPAGE' : 'N',
'NEXTTIME' : '0000',
'NEXTSLN' : '0000' })
httpServ.request('POST', '/timeschd/public/genedinq.asp', params, headers)
response = httpServ.getresponse()
print response.read()
if response.status == httplib.OK:
    printText (response.read())


httpServ.close()
