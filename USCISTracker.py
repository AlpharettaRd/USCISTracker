import requests
import bs4
import re
import json
import io
from datetime import datetime
from datetime import date
import os, errno
from os import path

def getCaseInfo(caseNumber):
    requestResult = requests.get("https://egov.uscis.gov/casestatus/mycasestatus.do?appReceiptNum={0}".format(caseNumber))
    if requestResult.status_code == 200:
        soup = bs4.BeautifulSoup(requestResult.text, "lxml")
        caseState = soup.select('.text-center h1')[0].text
        caseDescription = soup.select('.text-center p')[0].text
        formPattern = r"Form I-\d{3}"
        formSearchrequestResult = re.search(formPattern, caseDescription)
        formType = 'None'
        if formSearchrequestResult is not None:
            formType = caseDescription[formSearchrequestResult.start():formSearchrequestResult.end()]
        datePattern = r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}"
        dateSearchrequestResult = re.search(datePattern, caseDescription)
        lastUpdateDate = 'None'
        if dateSearchrequestResult is not None:
            lastUpdateDate = datetime.strptime(caseDescription[dateSearchrequestResult.start():dateSearchrequestResult.end()], '%B %d, %Y').date().strftime("%Y-%m-%d")
        return {'caseNumber':caseNumber, 'formType':formType, 'caseState':caseState, 'lastUpdatedDate':lastUpdateDate}
    else:
        print("Cannot conect to egov.uscis.gov. The status code is ", requestResult.status_code)
        return None

def findRelatedCase(caseNumber, nextCaseNumber):
    prefix = caseNumber[0:3]
    sequency = caseNumber[3:]
    myCaseInfo = getCaseInfo(caseNumber)
    result = []
    if nextCaseNumber > 0:
        indexStep = 1
    else:
        indexStep = -1
        nextCaseNumber = -nextCaseNumber
    index = indexStep
    while True:
        temp = getCaseInfo("{0}{1}".format(prefix, int(sequency) + index))
        index += indexStep
        if (temp['formType'] == myCaseInfo['formType'] and 
           temp['caseState'] != 'Card Was Mailed To Me' and 
           temp['caseState'] != 'Case Was Denied' and 
           temp['caseState'] != 'Case Was Approved' and
           'Rejected' not in temp['caseState']):
            result.append(temp)
            if len(result) >= nextCaseNumber:
                print("Total processed {1} cases, Find {0} cases.".format(len(result), (index if index > 0 else -index) - 1))
                return result
        print("Total processed {1} cases, Find {0} cases.\r".format(len(result), (index if index > 0 else -index) - 1), end='')


def main():
    myCase = 'MSC2090000000'
    caseCacheFile = myCase + '.cache'
    if path.exists(caseCacheFile):
        myCaseInfo = getCaseInfo(myCase)
        print(myCaseInfo)
        inputFile = open(caseCacheFile, 'r')
        jsonCaseDict = json.load(inputFile, encoding='utf8')
        isUpdate = False
        for index, oneCase in enumerate(jsonCaseDict['cases']):
            oneCaseUpdated = getCaseInfo(oneCase['caseNumber'])
            if oneCase['caseState'] != oneCaseUpdated['caseState'] or oneCase['lastUpdatedDate'] != oneCaseUpdated['lastUpdatedDate']:
                if not isUpdate:
                    isUpdate = True
                jsonCaseDict['cases'][index] = oneCaseUpdated
                print("{0} is updated on {1} from {2} to {3}.".format(oneCase['caseNumber'], oneCaseUpdated['lastUpdatedDate'], oneCase['caseState'], oneCaseUpdated['caseState']))
            print('Processed {0}/{1}\r'.format(index + 1, len(jsonCaseDict['cases'])), end='')
        if isUpdate:
            outfile = io.open(caseCacheFile, 'w', encoding='utf8')
            jsonCaseDict['refreshDate'] = date.today().strftime("%Y-%m-%d")
            data = json.dumps(jsonCaseDict, sort_keys=False, ensure_ascii=False, indent=2)
            outfile.write(data)
        print('Complete {0}'.format(len(jsonCaseDict['cases'])))
    else:
        monitorNumber = -100
        relatedCaseList = findRelatedCase(myCase, monitorNumber)
        casesDict = {'caseNumber': myCase, 'trackNumber': monitorNumber, 'createdDate:': date.today().strftime("%Y-%m-%d"), 'refreshDate': date.today().strftime("%Y-%m-%d"), 'cases': relatedCaseList}
        outfile = io.open(caseCacheFile, 'w', encoding='utf8')
        data = json.dumps(casesDict, sort_keys=False, ensure_ascii=False, indent=2)
        outfile.write(data)

if __name__ == "__main__":
   main()
