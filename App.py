import pickle
import json
import datefinder
import re
from flask import Flask, request

# this is how we initialize a flask application
app = Flask(__name__)
def get_Receipt_Date(ocr):
    all = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", ocr)  # dd/MM/YYYY
    if len(all) == 0:
        all = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{1,2}", ocr)  # dd/MM/YY
    if len(all) == 0:
        all = re.findall(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", ocr)  # dd-MM-YYYY
    if len(all) == 0:
        all = re.findall(r"[\d]{1,2}-[\d]{1,2}-[\d]{2}", ocr)  # dd-MM-YY
    if len(all) == 0:  # 10 OCT 2015  10 October 2015
        all = re.findall(r"([\d]{1,2}\s(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)\s[\d]{4})",ocr)
    if len(all) == 0:  # 10 OCT 15  10 October 15
        all = re.findall(r"([\d]{1,2}\s(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)\s[\d]{2})",ocr)
    if len(all) == 0:  # 10-OCT-2012  10-October-2015
        all = re.findall(r"([\d]{1,2}-(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)-[\d]{4})",ocr)
    if len(all) == 0:  # 10-OCT-15  10-October-15
        all = re.findall(r"([\d]{1,2}-(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)-[\d]{2})",ocr)
    if len(all) == 0:  # Jun 16' 18 JUN 16, 18
        all = re.findall(r"((?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)[\d]{2}[',]\s[\d]{2})",ocr)  # ['][\d]{2}\s[\d]{2}
    if len(all) == 0:  # Jun 16'18 JUN 16,18
        all = re.findall(r"((?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)[\d]{2}[',][\d]{2})",ocr)  # ['][\d]{2}\s[\d]{2}
    if len(all) == 0:
        all = re.findall(r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)\s[.,][\d]{2}[.,]\s[\d]{2})",ocr)  # ['][\d]{2}\s[\d]{2}
    print(all)
    if len(all) != 0:
        receiptDate = all[0]
        print("receiptDate:" + receiptDate)
        matches = datefinder.find_dates(receiptDate)
        print(matches)
        matche = list(matches)
        if len(matche) == 0:
            return receiptDate
        else:
            return str(matche[0])
    else:
        return 'Invalid Date format'

@app.route("/classification", methods=["POST"])
def get_Receipt_Category():
#CODE TO CLASSIFY RECEIPT CATEGORY
    value = request.get_json();
    data = value['RawText']
    clf = pickle.load(open('test_finalized_Receipt_model1.sav', 'rb'))
    count_vect = pickle.load(open('test_countvector1.sav', 'rb'))
    test = count_vect.transform([data])
    result=clf.predict(test)
    category= result[0]

#CODE FOR EXTRACT DATE
    receiptDate=get_Receipt_Date(data)

#CODE FOR MAX TOTAL AMOUNT
    numbers = re.findall('\d*\.\d+',data)
    numbers=map(float,numbers)
    totalAmount= str(max(numbers))
    #print('totalAmount'+totalAmount)
    return Flask.response_class(json.dumps({
        'receiptCategory':category,
        'totalAmount': totalAmount,
         'receiptDate':receiptDate
    }), mimetype=u'application/json')

if __name__ == '__main__':
    app.run(host="localhost", debug=True, use_reloader=False)
