
import os
from dataIO import *
from cwidgets import *

# Coordinates are always passed in the order y,x, 
# the top-left corner of a window is coordinate (0,0).


def getHwkCommCodes(ass: str, studkey: str, rubric: list)-> list:
    """
    @param ass - assignment abreviation
    @param studkey - studentId_lastname key
    @param rubric - list of comment items.

    @return all comment Codes listed by question
    """

    pathC=os.getcwd()+'/course_data/assignments/'+ass+'/'+studkey+'.csv'
    error = ""

    oldcomments = importCSV(pathC)

    if oldcomments == None:
        oldcomments = []
    hwkcomments = []
    for item in rubric:
        if ')' in item[0]:
            have = False
            for hcom in oldcomments:
                if item[0] == hcom[0]:
                    have = True
                    break
            if have:
                hwkcomments += [hcom]
            else:
                # Rubric may have had questions added. 
                # include any new questions in student comments
                hwkcomments += [[item[0], item[1],""]]

    if hwkcomments != oldcomments:
        exportCSV(pathC, hwkcomments)

    if len(hwkcomments) == 0:
        error = "No Homework Comments Found. Verify Rubric is Ok."

    return hwkcomments, error

def float2str1d(gr: float)-> str:
    """
    @param gr - a floating point grade number

    @return a grade value with a single decimal point, or no decimal if .0
    """

    gr = str(round(gr, 1))

    if gr[-1] == '0':
        gr = gr.split('.')[0]

    return gr

def checkFilter(qnum: str, commCodeList: str, filterq: str):
    
    if filterq == None:
        return True

    if filterq == qnum:
        return True

    if filterq in commCodeList.split(','):
        return True

    # if the comment encodes a number, remove the 
    # specific number
    if '{' in filterq:
        filterq = filterq.split('{')[0]

    for item in commCodeList.split(','):
        if filterq == item.split('{')[0]:
            return True

    return False
     

def updateScoreFrComments(q: str, qi: int, qRubric: list, hwkCommCodes, ass: str, fmatch: bool, hcom: list, filterq: str,
        total: float, errc: int, avgs: list, cnts: list, N99: str, glist: list):
    """
    @param q - the question string
    @param qi - the question integer index
    @param qRubric - the question Rubric
    @param ass - assignment string
    @param hwkCommCodes - comment codes for this student
    @param fmatch - whether a question has been found that matches the filter
    @param hcom - homework comment list for a single question, 3 item row
    @param filterq - the filter, if any, used for the match. None if unused.
    @param total - the score computed so far
    @param errc - the error count
    @param errl - the last error descrition
    @param avgs - question average computed so far
    @param cnts - total # of questions found so far
    @param N99 - comments
    @param glist - grade list

    @return - updates most inputs with grade scores / comments
    """

    fmatch |= checkFilter(hcom[0], hcom[2], filterq)
    error, calc_ok, g = grCalc(q, hcom[2], qRubric)
    assert calc_ok, error
    if error != '':
        errc += 1
        errl = error
    total += g
    avgs[qi] += g
    cnts[qi] += 1
    strscore = float2str1d(g) + ' /' + qRubric[0][1] 
    if q == 'Q99)':
        dispComment, commentCodesQ = getDispComments(hwkCommCodes, qRubric, q, False)
        strscore = ''
        for row in dispComment:
            if row[0] == '':
                m='!'
                if ass == 'NN':
                    m = '*'
                if row[2][0] == ':' and row[2][1] in '?%':
                    m = row[2][1]
                strscore += m
        if strscore != '':
            N99 += strscore
    glist += [strscore]

    return error, fmatch, errc, avgs, cnts, N99, glist, total


def genStudKeysScores(rubric, ass, filterq):
    """
    @param rubric - list
    @param ass - assignment
    @param filterq - select only students with specific comments, on Q#) or Q#. None to match all

    @return table and dictionary including student keys, and scores for specific assignment
    """

    assert filterq == None or '.' in filterq or ')' in filterq, "Bad filter option= '" + filterq + "'"

    if filterq != None:
        filterq = filterq.lstrip()

    stdList, stdDict = getStudList()

    qlist = []
    for row in rubric:
        if ')' in row[0]:
            qlist += [row[0]]

    klist = [[""] + qlist + ["total"]]
    avgs = [0] * (len(klist[0]) - 1)
    cnts = [0] * (len(klist[0]) - 1)
    mpts = [0] * (len(klist[0]) - 1)
    
    kdict = {}
    fmatch = True
    errc = 0
    errl = ''
    for row in stdList:
        if filterq != None:
            fmatch = False
        studkey = row[0]

        glist = []
        hwkCommCodes, error = getHwkCommCodes(ass, studkey, rubric)
        assert error == ""

        total = 0
        maxsc = 0
        fin = True
        stot = ''
        N99 = ''
        qi = 0
        for q in qlist:
            for hcom in hwkCommCodes:
                if hcom[0] == q:
                    break
            qRubric = getQRubric(rubric, q)
            maxsc += int(qRubric[0][1])
            mpts[qi] = int(qRubric[0][1])
            if hcom[2] != '':
               error, fmatch, errc, avgs, cnts, N99, glist, total =  updateScoreFrComments(
                  q, qi, qRubric, hwkCommCodes, ass, fmatch, hcom, filterq, total, errc, avgs, cnts, N99, glist)
            else:
                if int(qRubric[0][1]) > 0:
                    fin = False
                glist += ['  ']

            if fin:
                stot = float2str1d(total) + ' /' + str(maxsc)

            qi += 1

        if fmatch:
            avgs[qi] += total
            cnts[qi] += 1
            if '/' in stot:
                mpts[qi] = float(stot.split('/')[1].strip())
            klist += [[studkey] + glist + [stot]]
            kdict[studkey] = [stot, N99]
    
    if filterq == None:
        avgstr = ['   averages']
        for qi in range(0, len(avgs)):
            if cnts[qi] == 0 or mpts[qi] == 0:
                avgstr += ['']
            else:
                av = avgs[qi]/cnts[qi]
                avgstr += [str(round(av, 1))+
                        ' ('+str(round(100 * av/mpts[qi],1))+'%)']
        klist += [[''] * len(avgstr)]
        klist += [avgstr]
        if errc > 0:
            klist += [[''] * len(avgstr)]
            klist += [[' ' + str(errc) + ' errors, ' + errl] + [''] * (len(avgstr) - 1)]

    return klist, kdict

def getDispComments(AllHwkCommCodes: list, qRubric: list, q: str, stdview: bool):
    """
    @param HwkCommCodes - student assignment questions w comment codes
    @param qRubric - a rubric for a single question
    @param q - question in Q#) format
    @param stdview - if True check comment for special fields

    @return 2d array of comments, a list of comment Codes
    """
    dispComment = []
    commentCodesQ = ['']
    reorderedCommentCodesQ = ['']

    for row in AllHwkCommCodes:
        if q == row[0]:
            commentCodesQ = row[2].split(',')
            if commentCodesQ == ['']:
                gr = ' '
            else:
                error, calc_ok, g = grCalc(q, row[2], qRubric)
                assert calc_ok, error
                if error == '':
                    gr = float2str1d(g) + ' /' + row[1]
                elif calc_ok:
                    gr = error + ' ('+float2str1d(g)+')'
                else:
                    gr = error
                
            # hide certain details in the student's view
            if stdview and qRubric[0][2][0:2] == ":h": # hide description
                    dispComment += [[q, gr, ""]]
            elif stdview and qRubric[0][2][0:2] == ":H": # hide all question info 
                    dispComment += [["","",""]]
            else:
                dispComment += [[q, gr, ". . . " + qRubric[0][2]]]

            if commentCodesQ != ['']:
                # display items in the same order that they appear in rubric
                reorderedCommentCodesQ = []
                for ritem in qRubric:                    
                    for cCode in commentCodesQ:
                        #if '{' in cCode:
                        #    debug(None, (cCode.split('{')[0], ritem[0]))
                        #
                        # Currently does not display imported numbers, just summs
                        #
                        if '{' in cCode and "  " + cCode.split('{')[0] == ritem[0]:
                            pts = cCode.split('{')[1].split('}')[0]
                            pts = "( "+pts+" pts )"

                            if stdview and ritem[2][0:2] == ':n':
                                dispComment += [["", pts, ritem[2][2:]]]
                            elif stdview and ritem[2][0:2] == ':i':
                                pass # don't show import details in student view
                            else:
                                dispComment += [["", pts, ritem[2]]]
                                reorderedCommentCodesQ += [cCode]

                        elif "  " + cCode == ritem[0]:
                            pts = ""
                            if ritem[1] != "":
                                pts = "("+ritem[1]+" pts )"

                            dispComment += [["", pts, ritem[2]]]
                            reorderedCommentCodesQ += [cCode]

    return dispComment, reorderedCommentCodesQ


def showHwkComments(stdscr, allHwkCommCodes: list, qRubric: list, q: str, py: int, sel: int, nowait: bool, stdview: bool):
    """
    @param allHwkCommCodes - student assignment questions w comments
    @param qRubric - a rubric for a single question
    @param q - question in Q#) format
    @param py - y position to display table at
    @param sel - selected comment also default
    @param nowait - if True just display and return
    @param stdview - if True check comment for special fields

    @return display 
    """

    dispComment, commentCodesQ = getDispComments(allHwkCommCodes, qRubric, q, stdview)

    if commentCodesQ == ['']:
        sel = arrayRowSelect(stdscr, dispComment, py, 0, 0, 8, 0, sel, True)
        return -1, ''

    sel = arrayRowSelect(stdscr, dispComment, py, 0, 0, 8, 0, sel, nowait)
    if nowait:
        return len(dispComment), ''

    return sel, commentCodesQ[sel - 1]

def grCalc(q: str, comCodes: str, qRubric: list):
    """
    @param q - question to grade in 'Q#)' format
    @param comCodes - a string representation of a list of comment codes, i.e. "Q2.1,Q2.3,Q2.8"
    @param qRubric - the Rubric for a single question

    @return an integer grade computed based on the Rubric and the comments
    """

    comList = comCodes.split(',')
    error = ""

    if len(comList) == 0:
        return 0
    
    glist = []
    maxgr = float(qRubric[0][1])
    allneg = True
    settot = 0
    for com in comList:
        
        # raw gradevalue
        if '{' in com:            
            strg = (com.split('{')[1]).split('}')[0]
            if strg == '':
                strg = '0'
            glist += [strg]
            settot += 1
            maxgr = float(strg)
            # debug(None, "XXXXXXXX> " + com)
            continue
        
        match = False
        for rrow in qRubric:
            if "  " + com == rrow[0]:
                match = True
                break
        assert match, "Comment Code '" + com + "' from list '"+comCodes+"'not found in Rubric " + str(qRubric)

        if rrow[1].isspace() or rrow[1] == '' or rrow[1] == '#.#':
            continue
        elif rrow[1][0] != '-':
            allneg == False
            if rrow[1][0] != '+':
                settot += 1
                maxgr = float(rrow[1])
        glist += [rrow[1]]

    if settot > 1:
        return "Cannot specify multiple fixed values", False, -1

    if allneg == False and settot == 0:
        maxgr = 0

    for gr in glist:
        if gr[0] in '+-':
            maxgr += float(gr)

    if maxgr < 0:
        error = "Grade < 0, " + comCodes
    if maxgr > float(qRubric[0][1]):
        error = "Grade > " + qRubric[0][1]+ ", " + comCodes

    return error, True, maxgr

def getQRubric(rubric: list, q: str):

    assert ')' in q
    qRubric = []
    fq = False
    for row in rubric:
        if row[0] == "" and fq:
            break
        if row[0] == q or fq == True:
            fq = True
            qRubric += [row]
    return qRubric

