import httplib, urllib, cgi
import HTMLParser
from bs4 import BeautifulSoup
import json

QUARTER_YEAR = 'QTRYR'
COURSE_CATEGORY = 'REQ'
START_TIME = 'STARTTIME'
END_TIME = 'ENDTIME'
START_CREDIT = 'STARTCREDIT'
END_CREDIT = 'ENDCREDIT'
START_COURSE = 'STARTCOURSE'
END_COURSE = 'ENDCOURSE'
SEATTLE_CAMPUS = 'SEATTLE'
BOTHELL_CAMPUS = 'BOTHELL'
TACOMA_CAMPUS = 'TACOMA'
NEXT_PAGE = 'NEXTPAGE'
NEXT_SLN = 'NEXTSLN'
NEXT_TIME = 'NEXTTIME'
EXCLUDE_ENTRY_CODE = 'ENTRYCODE'
EXCLUDE_PREREQUISITES = 'PREREQCODE'
EXCLUDE_REGISTRATION_RESTRICTION = 'REGRESCODE'

headers = {
'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
'Content-Type' : 'application/x-www-form-urlencoded',
'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Referer' : 'http://www.washington.edu/students/timeschd/genedinq.html',
'Accept-Language' : 'en-US,en;q=0.8',
'Accept-Charset' : 'gb18030,utf-8;q=0.7,*;q=0.3',
}

def convertJsonToFormEntity(jForm):
    entity = []
    form = json.loads(jForm)

    entity.append((QUARTER_YEAR, form[QUARTER_YEAR][0]));
    entity.append((COURSE_CATEGORY, form[COURSE_CATEGORY][0]));
    entity.append((START_TIME, form[START_TIME][0]));
    entity.append((END_TIME, form[END_TIME][0]));
    entity.append((START_CREDIT, form[START_CREDIT][0]));
    entity.append((END_CREDIT, form[END_CREDIT][0]));
    entity.append((START_COURSE, form[START_COURSE][0]));
    entity.append((END_COURSE, form[END_COURSE][0]));
    specifiedCampus = False
    if SEATTLE_CAMPUS in form and form[SEATTLE_CAMPUS][0]:
        entity.append((SEATTLE_CAMPUS, 'Y'));
        specifiedCampus = True
    if BOTHELL_CAMPUS in form and form[BOTHELL_CAMPUS][0]:
        entity.append((BOTHELL_CAMPUS, 'Y'))
        specifiedCampus = True
    if TACOMA_CAMPUS in form and form[TACOMA_CAMPUS][0]:
        entity.append((BOTHELL_CAMPUS, 'Y'))
        specifiedCampus = True
    if not specifiedCampus:
        return None
    hasNextPage = form[NEXT_PAGE][0]
    if hasNextPage == True:
        entity.append((NEXT_PAGE, 'Y'))
        entity.append((NEXT_SLN, form[NEXT_SLN][0]));
        entity.append((NEXT_TIME, form[NEXT_TIME][0]));
    else:
        entity.append(('submit1', 'Find open courses'));
            

    if EXCLUDE_ENTRY_CODE in form and form[EXCLUDE_ENTRY_CODE][0]:
        entity.append((EXCLUDE_ENTRY_CODE, 'N'))
    
    if EXCLUDE_PREREQUISITES in form and form[EXCLUDE_PREREQUISITES][0]:
        entity.append((EXCLUDE_PREREQUISITES, 'N'))

    if EXCLUDE_REGISTRATION_RESTRICTION in form and form[EXCLUDE_REGISTRATION_RESTRICTION][0]:
        entity.append((EXCLUDE_REGISTRATION_RESTRICTION, 'N'))
    return urllib.urlencode(entity)
    
def getCourseHtmlPage(httpBody):
    formEntity = convertJsonToFormEntity(httpBody) 
    httpServ = httplib.HTTPConnection('sdb.admin.washington.edu')
    httpServ.connect()

    httpServ.request('POST', '/timeschd/public/genedinq.asp', formEntity, headers)
    response = httpServ.getresponse()
    #print response.status
    if response.status == httplib.OK:
        return response.read()
    
    httpServ.close()

def processTable(table):
    if table == None:
        return
    courses = []
    tableSchema = table.tr
    firstRow = True
    for tableRow in table.find_all('tr'):
        if firstRow:#get rid of schema
            firstRow = False
            continue
        course = {}
        entryIndex = 0
        for column in tableRow.find_all('td'):
            try:
                if entryIndex == 0:
                    slnRecord = column.find('a')
                    course['slnLink'] = slnRecord['href'].strip()
                    course['sln'] = int(slnRecord.string.strip())
                elif entryIndex == 1: 
                    course['course'] = column.string.strip()
                elif entryIndex == 2:
                    course['courseSection'] = column.string.strip()
                elif entryIndex == 3:
                    courseTitleRecord = column.contents[0]
                    course['courseTitleLink'] = courseTitleRecord['href'].strip()
                    course['courseTitle'] = courseTitleRecord.string.strip()
                elif entryIndex == 4:
                    try:
                        course['credits'] = float(column.string.strip())
                    except valueError:
                        entryIndex += 1
                elif entryIndex == 5:
                    course['spaceAvailable'] = int(column.string.strip())
                elif entryIndex == 6:
                    course['meetingsDay'] = column.contents[0].strip()
                    if column.contents[1] != None:
                        course['meetingsDay'] += ' ' + column.contents[1].string.strip()
                elif entryIndex == 7:
                    course['meetingsTime'] = column.contents[0].string.strip()
                elif entryIndex == 8:
                    checkPreR = column.find('a') 
                    if checkPreR != None:
                        course['checkPrerequestLink'] = checkPreR['href'].strip()
                    else:
                        notes = column.string.strip()
                        if notes:
                            course['notes'] = notes
                elif entryIndex == 9:
                    course['campus'] = column.string.strip()
                entryIndex += 1
            except:
                entryIndex += 1
                continue
        courses.append(course)
    return courses

def hasNextPage(soup):
    return soup.find('form', id='form1', action='http://sdb.admin.washington.edu/timeschd/public/genedinq.asp') != None
        
def parseHtmlPage(htmlPage):
    result = {}
    if htmlPage == None:
        result['courses'] = None
        result['hasNextPage'] = False
        return json.dumps(result)
    soup = BeautifulSoup(htmlPage)
    table = soup.find('table', border='1', cellpadding='3')
    
    courses = processTable(table)
    result['courses'] = courses
    result['hasNextPage'] = hasNextPage(soup)
    return json.dumps(result) 
    
def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()

if __name__ == '__main__':
    import sys
    f = open(sys.argv[1], "r")
    fileContent = f.read()
    parseHtmlPage(fileContent)

