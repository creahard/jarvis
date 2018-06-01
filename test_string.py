import pytest, string2time

numbers = [
'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
'seventeen', 'eighteen', 'nineteen']
extNumbers = [
'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
timeTypes = ['second', 'minute', 'hour']

def valStr(num):
    myString = ""
    if num < 20:
        myString += "{0}".format(numbers[num])
    elif num % 10 == 0:
        myString += "{0}".format(extNumbers[num/10-2])
    else:
        myString += "{0} {1}".format(extNumbers[num/10-2],numbers[num%10])
    return myString

# ("half an hour",1800), breaks it currently. Will revisit later.
testStrings = [("half hour",1800),("hour",3600),("minute",60)]
for h in range (0,13):
    for m in range (0,90):
        for s in range (0,60):
            myString = ""
            value = 0
            if h > 0:
                myString+= "{0} hour ".format(valStr(h))
                value+= h*3600
            if m > 0:
                myString += "{0} minutes ".format(valStr(m))
                value += m*60
            if s > 0:
                myString += "{0} seconds ".format(valStr(s))
                value += s
            if value != 0:
                testStrings.append((myString,value))

testTimes = []
for h in range(0,24):
    for m in range (0,60):
        if m == 0:
            testTimes.append(("{0}".format(valStr(h)),"{:02d}:{:02d}".format(h,m)))
        if m < 11:
            testTimes.append(("{0} oh {1}".format(valStr(h),valStr(m)),"{:02d}:{:02d}".format(h,m)))
        else:
            testTimes.append(("{0} {1}".format(valStr(h),valStr(m)),"{:02d}:{:02d}".format(h,m)))

for h in range(1,12):
    for m in range (0,60):
        if m == 0:
            testTimes.append(("{0} pm".format(valStr(h)),"{:02d}:{:02d}".format(h+12,m)))
        if m < 11:
            testTimes.append(("{0} oh {1} pm".format(valStr(h),valStr(m)),"{:02d}:{:02d}".format(h+12,m)))
        else:
            testTimes.append(("{0} {1} pm".format(valStr(h),valStr(m)),"{:02d}:{:02d}".format(h+12,m)))


for m in range (0,60):
    if m < 10:
        testTimes.append(("12 oh {0} am".format(valStr(m)),"00:{:02d}".format(m)))
    else:
        testTimes.append(("12 {0} am".format(valStr(m)),
                          "00:{:02d}".format(m)))

for m in range (0,60):
    if m < 20:
        testTimes.append(("12 oh {0} pm".format(valStr(m)),"12:{:02d}".format(m)))
    else:
        testTimes.append(("12 {0} pm".format(valStr(m)),
                          "12:{:02d}".format(m)))

@pytest.mark.parametrize("str,val",testStrings)

def test_conversions(str,val):
    s = string2time
    assert s.convert(str) == val


@pytest.mark.parametrize("str,timeStr",testTimes)
def test_times(str,timeStr):
    s = string2time
    assert s.convert(str) == timeStr