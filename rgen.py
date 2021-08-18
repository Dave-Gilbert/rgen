#!/usr/bin/python3

import curses
from curses import wrapper
from pathlib import Path
import os

from cwidgets import *
from dataIO import *
from editRubric import *
from commGrades import *

def getQuestionToGrade(stdscr, rubric: list, qi: int, ass: str):
    """
    Show selection menu for question to grade

    @param stdscr: curses root window object
    @param rubric: full assignment rubric
    @param qi: selected question row, as integer
    @param ass: assignment name

    @return: qlist - question list, qi - question row int, error
    """
    
    stdscr.clear()

    stdscr.addstr(2, 0, "Assignment " + ass + ": Select Question to Grade")
    error = ""

    qsel = []
    for row in rubric:
        if ')' in row[0]:
            qsel += [row]

    qsel += [['       Comma separated list','','']]

    qi = arrayRowSelect(stdscr, qsel, 5, 0, 0, 8, 0, qi, False)

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
    insert a new comment into the rubric

    @param HwkCommCodes: string representation of a comma separated list of comment codes
    @param q: string question id Q##)
    @param qi: integer index into question
    @param acs: comment selection from qRubric
    @param qRubric: question rubric with some menu items appended
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

def gradeQTopMenu(stdscr, menu: list, acs:str, m:int , ass:str, q:str, qRubric:list, YPOS_STDGR:int, filterq:str):
    """
    Handle the horizontal menu selection for the top portion of grade Question view

    @param stdscr: curses root window object
    @param menu: top menu, horizontal selection items
    @param acs: previous comment selection
    @param m: previous horizontal row menu selection
    @param ass: assignment
    @param q: question to grade, prefixed by 'Q' suffixed by ')'
    @param qRubric: the rubric for this question
    @param YPOS_STDGR: the y position for the student grade display
    @param filterq: restricts search to students with a specific comment
    
    @return: cont, acs, m, filterq
    """

    m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)
    if m == 0:
        cont = "Cont"
    elif m == 1:
        cont = "PrevS"
    elif m == 2:
        cont = "NextQ"
    elif m == 3:
        editAssRubric(stdscr, ass, 2, q[1:].split(')')[0])
        cont = "Cont"
    elif m == 4:
        stdscr.addstr(3, 0, "Find All Students that have specific comment")
        acs = arrayRowSelect(stdscr, qRubric, 6, 0, YPOS_STDGR - 2, 8, 0, 1, False)
        filterq = qRubric[acs][0]
        if '.' not in filterq and ')' not in filterq:
            filterq = None 
        cont = "NewFilter"
    elif m == 5:
        cont = "Done"

    return cont, acs, m, filterq


def gradeQAddComment(stdscr, menu, acs, m, ass, q, qi, rubric, qRubric, HwkCommCodesList, YPOS_STDGR, filterq):    
    """
    The Comment Menu both adds comments, and provides access to other common functions, next, del, comment, menu...

    @param stdscr: curses root window object
    @param menu: top menu, horizontal selection items
    @param acs: previous comment selection
    @param m: previous horizontal row menu selection
    @param ass: assignment
    @param q: question to grade, prefixed by 'Q' suffixed by ')'
    @param qi: integer pointer to question in Rubric
    @param rubric: assignment rubric
    @param qRubric: the rubric for this question
    @param HwkCommCodesList: student assignment questions with comment codes
    @param YPOS_STDGR: the y position for the student grade display
    @param filterq: restricts search to students with a specific comment

    return: HwkCommCodesList, rubric, cont, acs, m, filterq
    """

    cont = "loop"

    if acs == len(qRubric) - 4:    # --> menu
        cont, acs, m, filterq = gradeQTopMenu(stdscr, menu, acs, m, ass, q, qRubric, YPOS_STDGR, filterq)
    elif acs == len(qRubric) - 3:  # --> del comment
        sel, delCode = showHwkComments(stdscr, HwkCommCodesList, qRubric, q, YPOS_STDGR, 1, False, False) 
        cList = HwkCommCodesList[qi][2].split(',')
        # N.B. selected row will not reliably point to delCode in cList
        # this is due to some inconsistencies between ordering of codes
        # debug(stdscr, (cList, sel, delCode))
        if sel <= len(cList) and sel > 0:             
            cList.remove(delCode)
            newCom = ",".join(cList)
            newCom = [HwkCommCodesList[qi][0], HwkCommCodesList[qi][1], newCom]
            HwkCommCodesList[qi] = newCom
    elif acs == len(qRubric) - 2:  # --> new rubric item
        error, rubric, q, row = editAssRubricAddComm(stdscr, rubric, q[1:].split(')')[0], False, ass=='NN')
        if error == "":
            pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
            exportCSV(pathR, rubric)             
        cont = "Cont"
    elif acs == len(qRubric) - 1: # --> next student
        cont = "NextS"
    else:
        # insert a new comment if no special menu selection
        HwkCommCodesList = insNewComment(stdscr, HwkCommCodesList, q, qi, acs, qRubric)

    return HwkCommCodesList, rubric, cont, acs, m, filterq

def gradeQ(stdscr, HwkCommCodesList: list, q: str, rubric, acs: int, ass: str, studident: list, filterq: str):
    """
    Grade an individual question

    @param stdscr: curses root window object
    @param HwkCommCodesList: student assignment questions with comment codes
    @param q: question to grade, prefixed by 'Q' suffixed by ')'
    @param rubric: assignment rubric
    @param acs: previous comment selection
    @param ass: assignment
    @param studident: student name and id
    @param filterq: restricts search to students with a specific comment

    return: HwkCommCodesList - revised comments, cont - whether to continue marking, acs - menu selection, filterq - updated filter
    """

    assert (q[0] == 'Q' and q[-1] == ')') or (q[0:3] == '  Q' and '.' in q), "q arg not correctly formatted '" + q + "'"


    qRubric = getQRubric(rubric, q)

    qRubric += [["Menu", "", ""]]
    qRubric += [["del comment", "", ""]]
    qRubric += [["new rubric comment", "", ""]]
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
        menu = [" Grading " + ass + " " + q, "Prev Stud", "Next Q)", "Edit Rubric", "Find", "Done"]
    else:
        menu = [" Grading " + ass + " " + filterq, "Prev Stud", "Next Q)", "Edit Rubric", "Find", "Done"]
    m = 0

    # cont controls how we break out of the loop and gives a reason why
    cont = "loop"
    while cont == "loop":

        stdscr.clear()
        maxy, maxx = stdscr.getmaxyx()
        # Leave enough room for all student comments plus several extra.
        # Dynamically reposition student comments section so all comments are visible
        # scroll rubric only if absolutely necessary

        YPOS_STDGR = min(len(qRubric) + 12, maxy - max(HwkCommCodesList[qi][2].count('.') + 6, 4) )
        menuInputH(stdscr, menu, 2, 0, 10, 0, m, True)
        stdscr.addstr(YPOS_STDGR - 1, 0, studident[0] + " " + studident[1])
        error = ""

        sel, ignore = showHwkComments(stdscr, HwkCommCodesList, qRubric, q, YPOS_STDGR, 0, True, False)
        if sel == -1:
            acs = 1
        else:
            if acs < len(qRubric) - 3:
                acs = len(qRubric) - 1
        acs = arrayRowSelect(stdscr, qRubric, 6, 0, YPOS_STDGR - 2, 8, 0, acs, False)

        HwkCommCodesList, rubric, cont, acs, m, filterq = gradeQAddComment(stdscr, menu, acs, m, 
                ass, q, qi, rubric, qRubric, HwkCommCodesList, YPOS_STDGR, filterq)    

    return HwkCommCodesList, cont, acs, filterq


def enterGrades(stdscr, ass: str, s, selectStudent: bool):
    """
    Show a list of students to grade for a particular assignment, select student to grade

    @param stdscr: root curses window object
    @param ass: assignment name
    @param s: previous student selection
    @param selectStudent show the student selection menu, or not if false
    """

    assert selectStudent or s > 0

    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
    rubric = importCSV(pathR)
    stdList, stdDict = getStudList()

    m = 0
    error = ""
    qi = 0
    cont = "loop"
    filterq = None
    while cont != "Done":
       stdscr.clear()
       klist, kdict = genStudKeysScores(rubric, ass, filterq)
       assert len(klist)> 0, "keyword list = " + str(klist)
       if len(klist) == 1 and filerq != None:
           # 1st line of klist shows question #s, last 2 show averages
           menuInputH(stdscr, ["no results for filter =" + filterq], 3, 0, 10, 0, 0, False)
           return
       if s == 0 or s >= len(klist) - 2:           
           s = 1 
       if selectStudent or filterq != None:
           stdscr.addstr(2, 0, "Select Student to Grade for " + ass)
           s = arrayRowSelect(stdscr, klist, 3, 0, 0, 0, 50, s, False)
       studkey = klist[s][0]
       if studkey == "" or studkey[0] == ' ':
           break
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
                      if s >= len(klist) - 2:  # last 2 rows show avgs
                          s = 1
              elif cont == "Cont":
                  pass
              elif cont == "NewFilter":
                  break
              elif cont == "NextQ":
                  filter = None
                  break
                
def showGradeDetails(stdscr, hwkComments: list, klistQs: list, klistItem: list, stdInfo: list, ass: str, rubric: list, mg: int):
    """
    Show student / instructor view. Notes appear at the bottom of the screen

    @param stdscr: curses root window object
    @param hwkComments: a list of student questions and comments codes for each question
    @param klistQs: a list of assignment question and grades derived from the student key, last item is total
    @param stdInfo: student info, name and e-mail address
    @param ass: assignment name
    @param rubric: assignment rubric
    @param mg: previous menu selection, if -1 then only "Back" will be shown.

    @return: current menu selection, menu selection integer

    """

    stdscr.clear()
    stdscr.addstr(3, 0, stdInfo[2])
    stdscr.addstr(5, 0, stdInfo[1] + " . . . Grade = "+ klistItem[-1])
    stdscr.addstr(6, 0, "ID: " + stdInfo[0])
    stdscr.addstr(8, 0, ass)
    
    if mg == -1:
        menu = ["Back"]
        mg = 0
    else:
        menu = ["Next", "Prev", "Edit", "Done"]

    ypos = 10
    for q in klistQs[1:-2]:
        qRubric = getQRubric(rubric, q)
        rowt, ignore = showHwkComments(stdscr, hwkComments, qRubric, q, ypos, 0, True, True)
        ypos += rowt + 1

    ypos += 1
    q = "Q99)"
    qRubric = getQRubric(rubric, q)
    rowt, ignore = showHwkComments(stdscr, hwkComments, qRubric, q, ypos, 0, True, True)
    mg = menuInputH(stdscr, menu, 1, 0, 10, 0, mg, False)
    
    return menu[mg], mg

def showGrades(stdscr, ass: str, s: int, filterq):
    """
    Display the grades for a single assignment

    @param ass: assignment
    @param s: previous selection
    @param filterq: filter list, (None for get all)
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
        s = arrayRowSelect(stdscr, klist, 3, 0, 0, 8, 50, s, False)
        
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
                enterGrades(stdscr, ass, s, False)
                pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
                rubric = importCSV(pathR)                
                klist, kdict = genStudKeysScores(rubric, ass, filterq)


def editAssRubric(stdscr, ass: str, m: int, lq: str):
    """
    Edit the rubric for a given assignment

    @param ass: assignment id
    @param m: last menu item used 
    @param lq: string version of numeric question, may be ""
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

    menu = ["Add Question", "Add Comment", "Move Comment", "Edit", "Delete", "Find", "Save/Done"]

    while True:
        stdscr.clear()
        if error == "":
            exportCSV(pathR, rubric)
        else:
            stdscr.addstr(3,0, error)
        error = ""
        s = arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, s, True)
        m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)

        if m == 5:
            stdscr.addstr(4, 0, "Find All Students that have specific comment")

        if m == 0:
            error, rubric, lq, s = editAssRubricAddQ(stdscr, rubric)
        elif m == 1:
            error, rubric, lq, s = editAssRubricAddComm(stdscr, rubric, lq, True, ass=='NN')
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
                            'Q99.' in rubric[s][0] or 'Q99)' in rubric[s][0], True, ass=='NN')

                if error == "":
                    edItem = [rubric[s][0], pts, descr]
                    rubric[s] = edItem
            elif m == 4:
                key = rubric[s][0]
                if '.' in key or ')' in key:
                    klist, kdict = genStudKeysScores(rubric, ass, key)
                    if len(klist) > 3:
                        error = "Found " + str(len(klist) - 3) + " students referencing " + key + ", cannot delete"
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

def noteWeight(note:str):
    """
    @param note: string representing note types "%!*?"
    
    @return: numeric value representing the weight

    Notes are weighted as follows, by severity / lookup importance:

    % = 50 special grade calculation
    ! = 10 per assignment note (often academic dishonesty related)
    * = 3  per student note, asides / generic remarks
    ? = 1  odd questions about students
    """

    stab = {'A':300, '1':100,'2':100,'3':100,'4':100,'5':100,'6':100,'7':100,'8':100,'9':100,
            '%':50, '!':10, '*':3, '?':1, ' ':0 }
    score = 0
    for ch in note:
        score -= stab[ch]

    return score

def sortTable(table:list, sort):
    """
    Sort the data in a table by sort key, don't include the first row

    @param table: list of student info
    @param sort: sort order

    """
    sorted_table = table[1:]
    
    heading = [table[0]]

    if sort in (1,2,3):
        sorted_table.sort(key = lambda row: row[sort])
    elif sort == 4:
        sorted_table.sort(key = lambda row: float(row[-3]))
    elif sort == 5:
        sorted_table.sort(key = lambda row: float(row[-2].split('/')[0]))
    elif sort == 6:
        sorted_table.sort(key = lambda row: noteWeight(row[-1]))

    sorted_table = heading + sorted_table

    return sorted_table

def getAllStudGrades(stdList, stdDict, cAss, sort):
    """
    Construct a table of all grade results and all scores. Calculate grade totals based on comments.

    @param stdList: list of all student data from fast suite
    @param stdDict: dictionary of student keys vs. basic infor
    @param cAss: array of all all assignments

    @return allStudentGrades - master table of all scores vs. student details
    """

    studKeyVsZtimeDict = importZoomAttendData(stdList, stdDict)

    allStudGrRow = ['key', 'ID', 'Name', 'e-mail']
    for row in cAss:
        allStudGrRow += [row[0]]

    allStudGrades = [allStudGrRow + ['   Hours', '   Grade', '   Notes']]

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
        gradekey = 0
        # first lookup general notes for student
        # we need this so we can extract the grading scheme
        for row in cAss:
            if row[0] == 'NN':
                kdict = allDicts[row[0]]
                N99 += kdict[stud[0]][1]
        for ch in N99:
            if ch in '123456789':
                gradekey = int(ch)
                if gradekey + 2 >= len(cAss[0]):
                    debug(None, "Grade Key " + ch + " not defined in " + str(cAss[0]))
                    gradekey = 0
                break

        for row in cAss:
            kdict = allDicts[row[0]]
            score = kdict[stud[0]][0]
            allStudGrRow += [kdict[stud[0]][0]]

            if row[0] != 'NN':  # already accounted for
                N99 += kdict[stud[0]][1]

            if score.split('/')[0] != '':
                scorenum = float(score.split('/')[0])
                scoreden = float(score.split('/')[1])
                if scoreden > 0:
                    tweight += float(row[2 + gradekey]) # XXX select alt grade schemes
                    tscore += float(row[2 + gradekey]) * scorenum / scoreden

        row_w_totals = allStudGrRow + [ float2str1d(studKeyVsZtimeDict[stud[0]])] + \
                [float2str1d(tscore) + ' /'  + float2str1d(tweight)] + ['   ' + N99]
        allStudGrades += [row_w_totals]
     

    return sortTable(allStudGrades, sort)

def getSummaryFrAll(allStudGrades: list):
    """
    @param allStudGrades master table of all final scores

    @return brief summary of totals
    """

    summStudGrades = []
    for row in allStudGrades:
        summStudGrades += [row[1:4] + row[-3:] ]

    return summStudGrades

def showAllStudGrades(allStudGrades: list, s):
    """
    @param allStudGrades: complete student grade information for all students / all assignments
    @param s: selected student
    """
    g = -1
    while True:
        stdscr.clear()
        stdscr.addstr(3, 0, allStudGrades[s][3])
        stdscr.addstr(5, 0, allStudGrades[s][2])
        stdscr.addstr(6, 0, "ID: " + allStudGrades[s][1])
        studkey = allStudGrades[s][0]

        getNotes = False
        if allStudGrades[s][-1] != '':
            getNotes = True

        showArray = []
        for col in range(4, len(allStudGrades[s]) - 1):

            ass = allStudGrades[0][col]
            if '0 /0' not in allStudGrades[s][col] or ass == 'NN':
                Q99Notes = ''
                if getNotes and col < len(allStudGrades[0]) - 3:

                    pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
                    rubric = importCSV(pathR)
                    q = "Q99)"
                    qRubric = getQRubric(rubric, q)
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
                ass = showArray[g][0]
                #showGrades(stdscr, ass, s, None)
                #break

                #
                # Limits drill down to viewing grade details, it removes
                # the next/prev/edit option from that display.
                # The list of calling parameters is too complicated, 
                # Need to identify or clarify the pinch points 
                # for argument selection. 

                pathR=os.getcwd()+'/course_data/assignments/'+ass+'/0_rubric.csv'
                rubric = importCSV(pathR)
                hwkCommCodesList, error = getHwkCommCodes(ass, studkey, rubric)

                stdinfo = [allStudGrades[s][1], allStudGrades[s][2], allStudGrades[s][3]]
                klist, kdict = genStudKeysScores(rubric, ass, None)

                # klist will be in default order, we need to find the same row
                # in allStudGrades, which might be sorted by grade, match by key value
                key = allStudGrades[s][0]
                for k2 in range(0, len(klist)):
                    if key == klist[k2][0]:
                        break
                cont, mg = showGradeDetails(stdscr, hwkCommCodesList, klist[0], klist[k2], stdinfo, ass, rubric, -1)
                    
            


def mgrc(stdscr_in):
    """
    Root level menu presenting main options, student info & grade assignments

    @param stdscr_in: curses initial root level window
    """
    
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
    sort = 0
    menu = ["Student Info", "e-mail list", "Show Assignment Grades", "Enter Grades", "Edit Rubric", "Import myCanvas Grades", "Sort order"]
    menu2 = ["Sortby: default", "id", "name", "e-mail", "hours", "grade", "notes"]
    error = ""
    while True:    
        # redraw screen
        allStudGrades = getAllStudGrades(stdList, stdDict, cAss, sort)
        summStudGrades = getSummaryFrAll(allStudGrades)

        stdscr.clear()
        if error != "":
            stdscr.addstr(3,0, error)
        error = ""
        Atitle = "Assignment         points    %weight[def] %weight[v1]  %weight[v2]   "
        if m == 0 or m == 6:
            s = arrayRowSelect(stdscr, summStudGrades, 5, 0, 0, 12, 0, s, True)
            sort = menuInputH(stdscr, menu2, 3, 0, 10, 0, sort, True)
        else:
            stdscr.addstr(4, 0, Atitle)
            s = arrayRowSelect(stdscr, cAss, 5, 0, 0, 12, 50, s, True)
        
        m = menuInputH(stdscr, menu, 2, 0, 10, 0, m, False)
        
        if m == 0 or m == 6:
            stdscr.clear()
            menuInputH(stdscr, menu, 2, 0, 10, 0, m, True)
            arrayRowSelect(stdscr, summStudGrades, 5, 0, 0, 12, 0, s, True)
            if m == 6:
                sort = menuInputH(stdscr, menu2, 3, 0, 10, 0, sort, False)
            if m == 0:
                sort = menuInputH(stdscr, menu2, 3, 0, 10, 0, sort, True)
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
            stdscr.addstr(4, 0, Atitle)
            s = arrayRowSelect(stdscr, cAss, 5, 0, 0, 12, 50, s, False)
            if m == 2:
                showGrades(stdscr, cAss[s][0], 1, None)
            elif m == 3:
                enterGrades(stdscr, cAss[s][0], 0, True)
            elif m == 4:
                editAssRubric(stdscr, cAss[s][0], 0, "")
            elif m == 5:
                importMyCanvasData(stdscr, cAss[s][0])
    

msg = wrapper(mgrc)			


	

