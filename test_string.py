import pytest, string2time

numbers = [
'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
'seventeen', 'eighteen', 'nineteen']
extNumbers = [
'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
timeTypes = ['second', 'minute', 'hour']

testStrings = []
for t in range(0,len(timeTypes)):
    multiplier = 1
    if t == 1:
        multiplier = 60
    elif t == 2:
        multiplier = 3600
        
    for i in range(1,len(numbers)):
        testStrings.append(("{0} {1}".format(numbers[i],timeTypes[t]),i*multiplier))
    for o in range(0,len(extNumbers)):
        testStrings.append(("{0} {1}".format(extNumbers[o],timeTypes[t]),(o+2)*10*multiplier))
        for i in range(1,10):
            testStrings.append(("{0} {1} {2}".format(extNumbers[o],numbers[i],timeTypes[t]),((o+2)*10+i)*multiplier))

testTimes = []
for h in range(0,20):
    for m in range (0,60):
        if m < 20:
            testTimes.append(("{0} oh {1}".format(numbers[h],numbers[m]),"{:02d}:{:02d}".format(h,m)))
        elif m % 10 == 0:
            testTimes.append(("{0} {1}".format(numbers[h],extNumbers[m/10-2]),"{:02d}:{:02d}".format(h,m)))
        else:
            testTimes.append(("{0} {1} {2}".format(numbers[h],extNumbers[m/10-2],numbers[m%10]),
                              "{:02d}:{:02d}".format(h,m)))

for m in range (0,60):
    if m < 20:
        testTimes.append(("12 oh {0} am".format(numbers[m]),"00:{:02d}".format(m)))
    elif m % 10 == 0:
        testTimes.append(("12 {0} am".format(extNumbers[m/10-2]),"00:{:02d}".format(m)))
    else:
        testTimes.append(("12 {0} {1} am".format(extNumbers[m/10-2],numbers[m%10]),
                          "00:{:02d}".format(m)))

for m in range (0,60):
    if m < 20:
        testTimes.append(("12 oh {0} pm".format(numbers[m]),"12:{:02d}".format(m)))
    elif m % 10 == 0:
        testTimes.append(("12 {0} pm".format(extNumbers[m/10-2]),"12:{:02d}".format(m)))
    else:
        testTimes.append(("12 {0} {1} pm".format(extNumbers[m/10-2],numbers[m%10]),
                          "12:{:02d}".format(m)))

for h in range(0,24):
    if h < 20:
        testTimes.append(("{0}".format(numbers[h]),"{:02d}:00".format(h)))
    elif h % 10 == 0:
        testTimes.append(("{0}".format(extNumbers[h/10-2]),"{:02d}:00".format(h)))
    else:
        testTimes.append(("{0} {1}".format(extNumbers[h/10-2],numbers[h%10]),
                          "{:02d}:00".format(h)))

@pytest.mark.parametrize("str,val",testStrings)

def test_conversions(str,val):
    s = string2time
    assert s.convert(str) == val


@pytest.mark.parametrize("str,timeStr",testTimes)
def test_times(str,timeStr):
    s = string2time
    assert s.convert(str) == timeStr