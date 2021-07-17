#!/usr/bin/python3
#
# curses for screen rendering
# https://docs.python.org/3/howto/curses.html

import curses
from curses import wrapper
from pathlib import Path
import os

from cwidgets import *
from dataIO import *
from editRubric import *
from commGrades import *

# Coordinates are always passed in the order y,x, 
# the top-left corner of a window is coordinate (0,0).

def getQuestionToGrade(stdscr, rubric: list, qi, ass):
    
    stdscr.clear()

    stdscr.addstr(2, 0, "Assignment " + ass + ": Select Question to Grade")
    error = ""

    qsel = []
    for row in rubric:
        if ')' in row[0]:
            qsel += [row]

    qsel += [['       Comma separated list','','']]

    qi = arrayRowSelect(stdscr, qsel, 5, 0, 0, 8, 50, qi, False)

    if qi < len(qsel) - 1:
        qlist = [qsel[qi][0]]
        return qlist, qi, error
    else:
        qstr = input(stdscr, "Question List (#, #, ...)", "", 4, 0).strip()

        qlist_nums = qstr.split(',')

        qlist = []
        for item in qlist_nums:
            for row in qsel[0:-1]:
                qitem = 'Q' + item + ')'
                if qitem == row[0]:
                    qlist += [qitem]
    
    return qlist, qi, error
    

def insNewComment(stdscr, HwkCommCodes: str, q: str, qi: int, acs:int, qRubric: list):
    """
    @param HwkCommCodes - string representation of a comma separated list of comment codes
    @param q - string question id Q##)
    @param qi - integer index into question
    @param acs - comment selection from qRubric
    @param qRubric - question rubric with some menu items appended
    """

    # only allow a single arbitrary number
    if qRubric[acs][1] == '#.#' and '{' in  HwkCommCodes[qi][2]:
        return HwkCommCodes
    elif qRubric[acs][1] == '#.#':
        pts = input(stdscr, "item points #.#", "", 3, 0).strip()
        try: 
            f = float(pts)
            ok = True
        except e:
            ok = False
        if not ok:
            return HwkCommCodes
        newComment = qRubric[acs][0][2:] + '{' + str(round(f,1)) + '}'
    else:
        newComment = qRubric[acs][0][2:] 
 
    # trim spaces that prefix comment codes from rubric
    if '.' in qRubric[acs][0]:
        newComCodes = ""
        sep = ""
        #
        # reconstruct the comment list, inserting the new comment
        # at the same position that it appears in the rubric
        if HwkCommCodes[qi][2] == '':
            oldCommCodes = [newComment]
        else:
            oldCommCodes = HwkCommCodes[qi][2].split(',') + [newComment]
        for rk in qRubric[1:]:
            if not '.' in rk[0]:
                continue
            for commCode in oldCommCodes:
                if rk[0][2:] == commCode.split('{')[0]:
                    newComCodes += sep + commCode
                    sep = ','
                    break

        error, calc_ok, g = grCalc(q, newComCodes, qRubric)

        if error == '':
            newComRow = [HwkCommCodes[qi][0], HwkCommCodes[qi][1], newComCodes]
            HwkCommCodes[qi] = newComRow
        else:
            if calc_ok:
                debug(None, "failed to add " + newComment + ' ' + error +  ' ('+float2str1d(g)+')')
            else:
                debug(None, "failed to add " + newComment + ' ' + error )

    return HwkCommCodes


def gradeQ(stdscr, HwkCommCodesList: list, q: str, rubric, acs: int, ass: str, studident: list, filterq):

    assert (q[0] == 'Q' and q[-1] == ')') or (q[0:3] == '  Q' and '.' in q), "q arg not correctly formatted '" + q + "'"

    qRubric = getQRubric(rubric, q)

    qRubric += [["Menu", "", ""]]
    qRubric += [["del comment", "", ""]]
    qRubric += [["Next", "", ""]]

    found = False
    for qi in range(0, len(HwkCommCodesList)):
        if HwkCommCodesList[qi][0] == q:
            found = True
            break
    if not found:
        debug(stdscr, q+ " not found in Rubric ")
        # if question was removed from rubric, return with menu item "NextQ"
        return HwkCommCodesList, "NextQ", 0, filterq
    
    if filterq == None:
        menu = [" Grading " + ass + " " + q, "Prev Stud", "Next Q)", "Find", "Edit Rubric", "Done"]
    else:
        menu = [" Grading " + ass + " " + filterq, "Prev Stud", "Next Q)", "Find", "Edit Rubric", "Done"]


    m = 0

    cont = "Cont"
    while True:

        stdscr.clear()
        maxy, maxx = stdscr.getmaxyx()
        # Leave enough room for all student comments plus 2 extra.
        # Dynamically reposition student comments section so all comments are visible
        # scroll rubric only if absolutely necessary

        YPOS_STDGR = min(len(qRubric) + 10, maxy - max(HwkCommCodesList[qi][2].count('.') + 2, 4) )
        menuInputH(stdscr, menu, 2, 0, 10, 0, m, True)
        stdscr.addstr(YPOS_STDGR - 1, 0, studident[0] + " " + studident[1])
        error = ""

        sel = showHwkComments(stdscr, HwkCommCodesList, qRubric, q, YPOS_STDGR, 0, True, False)
        if sel == -1:
            acs = 1
        else:
            if acs < len(qRubric) - 3:
                acs = len(qRubric) - 1
        acs = arrayRowSelect(stdscr, qRubric, 4, 0, YPOS_STDGR - 2, 8, 0, acs, False)
        if acs == len(qRubric) - 3:
            m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)
            if m == 0:
                pass
            elif m == 1:
                cont = "PrevS"
                break
            elif m == 2:
                cont = "NextQ"
                break
            elif m == 3:
                stdscr.addstr(3, 0, "Find All Students that have specific comment")
                acs = arrayRowSelect(stdscr, qRubric, 4, 0, YPOS_STDGR - 2, 8, 0, 1, False)
                filterq = qRubric[acs][0]
                if '.' not in filterq and ')' not in filterq:
                    filterq = None 
                cont = "NewFilter"
                break
            elif m == 4:
                editAssRubric(stdscr, ass, 2, q[1:].split(')')[0])
                break
            elif m == 5:
                cont = "Done"
                break
                 
        elif acs == len(qRubric) - 1:
            cont = "NextS"
            break
        elif acs == len(qRubric) - 2:
            # adjust for qRubric selection, ignore -1 and 0, 
            sel = showHwkComments(stdscr, HwkCommCodesList, qRubric, q, YPOS_STDGR, 1, False, False) -1
            cList = HwkCommCodesList[qi][2].split(',')
            # debug(stdscr, (cList, sel))
            if sel < len(cList) and sel >= 0:             
                del cList[sel]
                newCom = ",".join(cList)
                newCom = [HwkCommCodesList[qi][0], HwkCommCodesList[qi][1], newCom]
                HwkCommCodesList[qi] = newCom
        else:
            # insert a new comment if no special menu selection
            HwkCommCodesList = insNewComment(stdscr, HwkCommCodesList, q, qi, acs, qRubric)


    return HwkCommCodesList, cont, acs, filterq


def enterGrades(stdscr, ass, s):

    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
    rubric = importCSV(pathR)
    stdList, stdDict = getStudList()

    m = 0
    error = ""
    qi = 0
    cont = ""
    filterq = None
    while cont != "Done":
       stdscr.clear()
       klist, kdict = genStudKeysScores(rubric, ass, filterq)
       assert len(klist)> 0, "keyword list = " + str(klist)
       if s == 0 or s >= len(klist):  
           s = 1 
           stdscr.addstr(2, 0, "Select Student to Grade for " + ass)
           s = arrayRowSelect(stdscr, klist, 3, 0, 0, 0, 50, s, False)
       studkey = klist[s][0]
       if studkey == "":
           continue
       if filterq == None:
           qlist, qi, error = getQuestionToGrade(stdscr, rubric, qi, ass)
           if len(qlist) == 0:
               return
       else:
           if ')' not in filterq:
               # convert filter comment into question format
               qlist = [(filterq.split('.')[0]+')').strip()]
           else:
               qlist = [filterq]
       qnum = 0       

       while error == "":
          q = qlist[qnum] 
          studkey = klist[s][0]
          if not studkey in stdDict:
              break
          pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
          rubric = importCSV(pathR)
          pathC=os.getcwd()+'/course_data/assignments/'+ass+'/'+studkey+'.csv'
          hwkCommCodesList, error = getHwkCommCodes(ass, studkey, rubric)
          acs = 0
          if error == "":
              hwkCommCodesList, cont, acs, filterq = gradeQ(stdscr, hwkCommCodesList, q, 
                      rubric, acs, ass, stdDict[studkey], filterq)
              # update hwkCommCodesList
              exportCSV(pathC, hwkCommCodesList)
              if cont == "Done":
                  break
              elif cont == "PrevS":
                  if s > 1:
                      s -= 1                  
                  qnum = 0
              elif cont == "NextS":
                  if qnum < len(qlist) - 1:
                      qnum += 1
                  else:
                      qnum = 0
                      s += 1
                      if s >= len(klist):
                          s = 1
              elif cont == "Cont":
                  pass
              elif cont == "NewFilter":
                  break
              elif cont == "NextQ":
                  filter = None
                  break
                
def showGradeDetails(stdscr, hwkComments, klistQs, klistItem, stdListItem, ass, rubric, mg):

    stdscr.clear()
    stdscr.addstr(3, 0, stdListItem[2])
    stdscr.addstr(5, 0, stdListItem[1] + " . . . Grade = "+ klistItem[-1])
    stdscr.addstr(6, 0, "ID: " + stdListItem[0])
    stdscr.addstr(8, 0, ass)
    
    menu = ["Next", "Prev", "Edit", "Done"]

    ypos = 10
    for q in klistQs[1:-2]:
        qRubric = getQRubric(rubric, q)
        rowt = showHwkComments(stdscr, hwkComments, qRubric, q, ypos, 0, True, True)
        ypos += rowt + 1

    ypos += 1
    q = "Q99)"
    qRubric = getQRubric(rubric, q)
    rowt = showHwkComments(stdscr, hwkComments, qRubric, q, ypos, 0, True, True)
    mg = menuInputH(stdscr, menu, 1, 0, 10, 0, mg, False)
    
    return menu[mg], mg

def showGrades(stdscr, ass: str, s: int, filterq):
    """
    @param ass - assignment
    @param s - previous selection
    @param filterq - filter list, (None for get all)
    """

    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
    rubric = importCSV(pathR)
    stdList, stdDict = getStudList()

    m = 0
    error = ""
    qi = 0
    cont = ""
    mg = 0
    while cont != "Done":
        stdscr.clear()
        klist, kdict = genStudKeysScores(rubric, ass, filterq)
        if len(klist) == 1:
            debug(None, "No Matches for filter = '" + str(filterq) + "'")
            return

        stdscr.addstr(2, 0, "Select Student to Show Grade for " + ass)
        s = arrayRowSelect(stdscr, klist, 3, 0, 0, 12, 50, s, False)

        
        studkey = klist[s][0]
        if studkey == "":
            break
        while error == "":
            if s < 0: 
                s = 0
            elif s >= len(klist):
                s = len(klist) - 1
            studkey = klist[s][0]
            if len(studkey) == 0 or studkey[0] == ' ':
                break
            hwkCommCodesList, error = getHwkCommCodes(ass, studkey, rubric)
            cont, mg = showGradeDetails(stdscr, hwkCommCodesList, klist[0], klist[s], stdDict[klist[s][0]], ass, rubric, mg)
            if cont == "Done":
                break
            elif cont == "Next":
                if s < len(klist) - 1:
                    s += 1
            elif cont == "Prev":
                if s > 1:
                    s -= 1
            elif cont == "Edit":
                enterGrades(stdscr, ass, s)
                pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
                rubric = importCSV(pathR)                
                klist, kdict = genStudKeysScores(rubric, ass, filterq)


def editAssRubric(stdscr, ass: str, m: int, lq: str):
    """
    @param ass - assignment id
    @param lq - string version of numeric question, may be ""
    @param m - last menu item used 
    """

    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
    rubric = importCSV(pathR)

    error = ""

    # if we know what question we are working on, move the selector
    # to the end of that question.
    s = 0
    if lq != "":
        fq = False
        for row in rubric:
            if row[0] == 'Q'+lq+')':
                fq = True
            if fq == True and row[0] == '':
                break
            s += 1

    while True:
        stdscr.clear()
        if error == "":
            exportCSV(pathR, rubric)
        else:
            stdscr.addstr(3,0, error)
        error = ""
        s = arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, s, True)
        m = menuInputH(stdscr, ["Add Question", "Add Comment", "Move Comment", "Edit", "Delete", "Find", "Save/Done"], 2, 0, 10, 0, m, False)

        if m == 5:
            stdscr.addstr(4, 0, "Find All Students that have specific comment")

        if m == 0:
            error, rubric, lq, s = editAssRubricAddQ(stdscr, rubric)
        elif m == 1:
            error, rubric, lq, s = editAssRubricAddComm(stdscr, rubric, lq)
        elif m in (2,3,4,5):  # Edit / move / delete find
            s = arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, s, False)
            if ')' not in rubric[s][0] and '.' not in rubric[s][0]:
                pass
            elif m == 2:
                if '.' not in rubric[s][0]:
                    error = "Can only move comments, not whole question"
                else:
                    error, rubric, s = editAssRubricMov(stdscr, rubric, s)

            elif m == 3:
                if ')' in rubric[s][0]:
                    error, pts, descr = editAssRubricQ(stdscr, rubric[s][1], rubric[s][2])
                elif '.' in rubric[s][0]:
                    error, pts, descr = editAssRubricComm(stdscr, rubric[s][1], rubric[s][2], 
                            'Q99.' in rubric[s][0] or 'Q99)' in rubric[s][0])

                if error == "":
                    edItem = [rubric[s][0], pts, descr]
                    rubric[s] = edItem
            elif m == 4:
                key = rubric[s][0]
                if '.' in key or ')' in key:
                    klist, kdict = genStudKeysScores(rubric, ass, key)
                    if len(klist) > 1:
                        error = "Found " + str(len(klist) - 1) + " students referencing " + key + ", cannot delete"
                    else:
                        if ')' in rubric[s][0]:
                            error, rubric = editAssRubricRemQ(stdscr, rubric, rubric[s][0])
                        elif '.' in rubric[s][0]:
                            del rubric[s]
                        if s > len(rubric) - 1:
                            s = len(rubric) - 1
            elif m == 5:
                filterq = rubric[s][0]
                if '.' in filterq or ')' in filterq:
                    showGrades(stdscr, ass, 0, filterq)

        elif m == 6:
            break

    exportCSV(pathR, rubric)

def getAllStudGrades(stdList, stdDict, cAss):
    """
    @param stdList - list of all student data from fast suite
    @param stdDict - dictionary of student keys vs. basic infor
    @param cAss - array of all all assignments

    @return allStudentGrades - master table of all scores vs. student details
    """

    studKeyVsZtimeDict = importZoomAttendData(stdList, stdDict)

    allStudGrRow = ['key', 'ID', 'Name', 'e-mail']
    for row in cAss:
        allStudGrRow += [row[0]]

    allStudGrades = [allStudGrRow + ['     Hours', '     Grade', '    Notes']]

    allDicts = {}
    for row in cAss:
        ass = row[0]
        pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
        rubric = importCSV(pathR)

        klist, kdict = genStudKeysScores(rubric, ass, None)
        allDicts[ass] = kdict

    for stud in stdList:
        allStudGrRow = stud[0:4]
        tweight = 0
        tscore = 0
        N99 = ''

        for row in cAss:
            kdict = allDicts[row[0]]
            score = kdict[stud[0]][0]
            allStudGrRow += [kdict[stud[0]][0]]
            N99 += kdict[stud[0]][1]

            if score.split('/')[0] != '':
                scorenum = float(score.split('/')[0])
                scoreden = float(score.split('/')[1])
                if scoreden > 0:
                    tweight += float(row[2])
                    tscore += float(row[2]) * scorenum / scoreden

        last_row = allStudGrRow + [ float2str1d(studKeyVsZtimeDict[stud[0]])] + \
                [float2str1d(tscore) + ' /'  + float2str1d(tweight)] + ['   ' + N99]
        allStudGrades += [last_row]
     

    return allStudGrades

def getSummaryFrAll(allStudGrades: list):
    """
    @param allStudGrades master table of all final scores

    @return brief summary of totals
    """

    summStudGrades = []
    
    for row in allStudGrades:
        summStudGrades += [row[1:4] + [row[-3], row[-2], row[-1]] ]


    return summStudGrades

def showAllStudGrades(allStudGrades: list, s):

    menu = ["Next", "Prev", "Done"]

    g = -1
    while True:
        stdscr.clear()
        stdscr.addstr(3, 0, allStudGrades[s][3])
        stdscr.addstr(5, 0, allStudGrades[s][2])
        stdscr.addstr(6, 0, "ID: " + allStudGrades[s][1])

        getNotes = False
        if allStudGrades[s][-1] != '':
            getNotes = True

        showArray = []
        for col in range(4, len(allStudGrades[s]) - 1):

            ass = allStudGrades[0][col]
            if '0 /0' not in allStudGrades[s][col] or ass == 'NN':
                studkey = allStudGrades[s][0]
                Q99Notes = ''
                if getNotes and col < len(allStudGrades[0]) - 3:

                    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
                    rubric = importCSV(pathR)
                    q = "Q99)"
                    qRubric = getQRubric(rubric, q)
                    pathC=os.getcwd()+'/course_data/assignments/'+ass+'/'+studkey+'.csv'
                    hwkCommCodesList, error = getHwkCommCodes(ass, studkey, rubric)
                    dispComment, commentCodesQ = getDispComments(hwkCommCodesList, qRubric, q, False)
                    sep = ''
                    for row in dispComment[1:]:
                        Q99Notes += sep + str(row[2])
                        sep = ', '

                if ass == 'NN':
                    showArray += [[ass, '', Q99Notes]]
                else:
                    showArray += [[ass, allStudGrades[s][col],Q99Notes]]
                showArray += [['','','']]
        showArray += [['','','']]
        showArray += [['Next','','']]
        showArray += [['Prev','','']]
        showArray += [['Done','','']]
            
        if g == -1:
            g = len(showArray) - 3
        g = arrayRowSelect(stdscr, showArray, 8, 0, 0, 12, 0, g, False)
 
        if g == len(showArray) - 3:
            s += 1
            if s>= len(allStudGrades):
                s = 1
        elif g == len(showArray) - 2:
            s -= 1
            if s< 1:
                s = 1
        elif g == len(showArray) - 1:
            break
        else:
            if showArray[g][0] in allStudGrades[0][4:-2]:
                showGrades(stdscr, showArray[g][0], s, None)
                break
            


def mgrc(stdscr_in):
    
    global stdscr
    stdscr = stdscr_in
    debug(stdscr, None)
    # verify that a class list file is present in the current directory
    # open will throw an exception otherwise
    pathCa=os.getcwd()+'/course_data/'+'course_assignments.csv'
    open(pathCa)

    stdList, stdDict = getStudList()
    cAss = importCSV(pathCa)

    buildAssDir(cAss)
    

    # display class list

    s = 0
    m = 0
    menu = ["Student Info", "e-mail list", "Show Assignment Grades", "Enter Grades", "Edit Rubric", "Import myCanvas Grades"]
    error = ""
    while True:    
        # redraw screen
        allStudGrades = getAllStudGrades(stdList, stdDict, cAss)
        summStudGrades = getSummaryFrAll(allStudGrades)

        stdscr.clear()
        if error != "":
            stdscr.addstr(3,0, error)
        error = ""
        if m == 0:
            s = arrayRowSelect(stdscr, summStudGrades, 5, 0, 0, 12, 0, s, True)
        else:
            stdscr.addstr(4, 0, "          points    %weight")
            s = arrayRowSelect(stdscr, cAss, 5, 0, 0, 8, 50, s, True)
        
        m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)
        
        if m == 0:
            stdscr.clear()
            m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, True)
            s = arrayRowSelect(stdscr, summStudGrades, 5, 0, 0, 12, 0, s, False)
            if s > 0:
                showAllStudGrades(allStudGrades, s)
        elif m == 1 and len(summStudGrades) >= 2:
            stdscr.clear()
            yp = 4
            rstr = summStudGrades[1][2] + '; '
            maxy, maxx = stdscr.getmaxyx()
            rp = 2
            while rp < len(summStudGrades):
                if len(rstr + summStudGrades[rp][2] + '; ') >= maxx:
                    stdscr.addstr(yp, 0, rstr)
                    rstr = summStudGrades[rp][2] + '; '
                    yp += 1
                else:
                    rstr += summStudGrades[rp][2] + '; '
                rp += 1

            stdscr.addstr(yp, 0, rstr)

            m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)
  
        elif m in (2, 3, 4, 5):
            stdscr.clear()
            m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, True)
            if m == 5:
                stdscr.addstr(3, 0, "Import myCanvas Grades for Which Assignment")
            stdscr.addstr(4, 0, "          points    %weight")
            s = arrayRowSelect(stdscr, cAss, 5, 0, 0, 8, 50, s, False)
            if m == 2:
                showGrades(stdscr, cAss[s][0], 1, None)
            elif m == 3:
                enterGrades(stdscr, cAss[s][0], 0)
            elif m == 4:
                editAssRubric(stdscr, cAss[s][0], 0, "")
            elif m == 5:
                importMyCanvasData(stdscr, cAss[s][0])
    

msg = wrapper(mgrc)			


	
