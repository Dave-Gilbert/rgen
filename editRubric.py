#!/usr/bin/python3
#
from cwidgets import *
from dataIO import *
from pathlib import Path
from commGrades import *

import os
    

def editAssRubricQ0(stdscr, pts: str, descr: str):
    """
    Q0 is special and defines group membership, does basic input validation

    @param stdscr: curses root object
    @param pts: default point value, or "" for empty
    @param descr: default description, or "" for empty

    @return: error, pts, descr
 
    """

    error = ""
    stdscr.addstr(4,0, "Group definition, Q0 will by default display 'Group'. ':H' Hide all")
    descr = input(stdscr, "Item Description ", descr, 5, 0)
    if descr == None:
        error = "cancelled"
    if descr != '' and descr[0] == ':' and descr[1] not in 'H':
        error = "Unsupported description prefix"

    return error, " 0", descr

def editAssRubricQ(stdscr, pts: str, descr: str):
    """
    Edits a rubric question, does basic input validation

    @param stdscr: curses root object
    @param pts: default point value, or "" for empty
    @param descr: default description, or "" for empty

    @return: error, pts, descr
    """

    error = ""
    stdscr.addstr(4,0, "Description prefixes = ':H' Hide all, ':h' hide Q#")
    descr = input(stdscr, "Item Description ", descr, 5, 0)
    if descr == None:
        error = "cancelled"
    if descr != '' and descr[0] == ':' and descr[1] not in 'Hh':
        error = "Unsupported description prefix"
    else:
        pts = input(stdscr, "Total Points", pts, 6, 0)
        if pts == None:
            error = "cancelled"
        else:
            pts = pts.strip()
            if not isfloat(pts):
                if len(pts) > 0:
                    error = "Expected Integer Point Total"
                else:
                    pts = " "
            else:
                if len(pts) == 1:
                    pts = " " + pts

    return error, pts, descr

def editAssRubricCommQ0Disp(stdscr, ass, oglist, stdList, stdDict, grView, show):
    """
    Display Static information about group membership and class details

    @param stdscr: curses root object
    @param ass: assignment
    @param oglist: original or current group list
    @param stdList: student list
    @param stdDick: student dictionary
    @param grView: which group view to show, 1=details, 2=name only, 3=email list only
    @param show: True - just shows the list, False returns a studentid selection, or empty for quit

    @return a student id, grView 

    @note
    returned student id == '_' to indicate quit
    returned student id == '' if grView is updated
    """


    ilen = len(stdList[0])

    erow = [""] * ilen

    grName=""
    if len(oglist) > 0:
        grName = oglist[0]

    if grView == 1:
        vmenu = "View = [ALL]  Name  Email "
    elif grView == 2:
        vmenu = "View =  All  [NAME] Email "
    else:
        vmenu = "View =  All   Name [EMAIL]"

    glistok = True
    for stdid in oglist[1:]:
        if stdid not in stdDict:
            glistok = False
            grView = 1

    hrow1 = [">> Current Members"] + [grName] + [vmenu] + [""]
    hrowd = [">> Total = " + str(max(len(oglist) - 1, 0)) + "      ---> save","", "", ""]
    hrow2 = [">> Students not assigned to groups"] + [""] * (ilen - 1)
    hrow3 = [">> Students assigned to Other groups"] + [""] * (ilen - 1)

    dispInfo = []
    dispInfo.append(hrow1)
    if grView == 1:
        for stdid in oglist[1:]:
            if stdid in stdDict:
                dispInfo.append([stdid] + stdDict[stdid])
            else:
                dispInfo.append([stdid, "Missing from DB", "", "XXX Error XXX"])
    elif grView == 2:
        for stdid in oglist[1:]:
            dispInfo.append([stdDict[stdid][1], "", "", ""])
    else:
        for stdid in oglist[1:]:
            dispInfo.append([stdDict[stdid][2] + ';', "", "", ""])
        

    dispInfo.append(hrowd)
    dispInfo.append(erow)
    dispInfo.append(hrow2)

    otGroups=[]

    for student in stdList:
        stdident = student[0].strip()
        pathSt = os.getcwd()+'/course_data/assignments/' + ass + '/' + stdident + '.csv'
        if not Path(pathSt).is_symlink():
            dispInfo.append(student)
        elif stdident not in oglist and glistok:
            otGroups.append(student)

    dispInfo.append(erow)
    dispInfo.append(hrow3)
    dispInfo = dispInfo + otGroups

    sel = arrayRowSelect(stdscr, dispInfo, 8, 0, 0, 12, 0, 0, show)
    stid = ""
    if not show:
        # an update was selected
        if sel > 0:
            stid = dispInfo[sel][0]
            if '_' not in stid:
                stid = "_"
        else:
            grView += 1
            if grView > 3:
                grView = 1

    return stid, grView


def editAssRubricCommQ0lnks(ass, glist, oglist, rubric):
    """
    Update links between the group file and the individual files

    When an individual file is removed from a group we just delete the link and repopulate with empty 

    @param ass: assignment
    @param glist: group member list
    @param oglist: old group member list, prior to any changes
    @param rubric: grading rubric for this assignment
    
    """

    # try to make template group grading scheme

    hwkcomments, error = getHwkCommCodes(ass, '0_' + glist[0], rubric)

    if error == "":
        # if we successfully created a group rubric, then link 
        # each individual student to that rubric, assuming they
        # are not already linked to some other group

        pathGR=os.getcwd()+'/course_data/assignments/' + ass + '/0_' + glist[0] + '.csv'
        if not os.path.exists(pathGR):
            debug(stdscr,"Unable to find " + pathGR)

        for stdident in glist[1:]:
            pathSt = os.getcwd()+'/course_data/assignments/' + ass + '/' + stdident + '.csv'
            if Path(pathSt).is_symlink():
                gpath = str(Path(pathSt).resolve())
                grpst = gpath.split('/')[-1]
                grpst = grpst[2:-4]
                if grpst != glist[0]:
                    error = "Student '" + stdident + "' is already part of group '" + grpst + "'"

    if error == "":

        for stdident in glist[1:]:
            pathSt = os.getcwd()+'/course_data/assignments/' + ass + '/' + stdident + '.csv'
            if os.path.exists(pathSt):
                os.remove(pathSt)

            os.symlink(pathGR, pathSt)
        
        for stdident in oglist[1:]:
            if stdident not in glist:
                pathSt = os.getcwd()+'/course_data/assignments/' + ass + '/' + stdident + '.csv'
                if os.path.exists(pathSt):
                    os.remove(pathSt)
                    getHwkCommCodes(ass, stdident, rubric) # should rebuild missing report

    return error

def sortGroup(descr):
    """
    Resort the group list, return both the string version and the list version

    @param descr: group description, i.e. a group name followed by a space separated member list


    @return: sorted descr, and sorted member list
    """
    glist=[]
    if len(descr) > 0:
        suff = descr.split()[1:]
        suff.sort()
        suff2 = []
        for member in suff:
            if member not in suff2:
                suff2.append(member)

        glist = [descr.split()[0]] + suff2
        descr = glist[0] + " " + " ".join(suff2)

    return descr, glist

def editAssRubricCommQ0(stdscr, descr: str, qask: bool, ass: str, rubric: list):
    """
    Q0 is used to define groups, editing a Q0 comment manages group members, does basic input validation.

    @param stdscr: curses root object
    @param descr: default description, or "" for empty
    @param qask: whether the question # was asked for or implied, determines placement of prompts
    @param ass: assignment for this group
    @param rubric: existing rubric

    @return: error, pts(updated point value), descr(update description)
    """

    shift = 0
    if not qask:
        shift = -1

    get_id = True
    phase = 0
    grView = 1
    while get_id:
        phase += 1     # alternate between plain text input and menu input
        stdscr.clear()

        oglist = descr.split()
        stdList, stdDict = getStudList()

        editAssRubricCommQ0Disp(stdscr, ass, oglist, stdList, stdDict, grView, True)

        error = ""
        stdscr.addstr(3 + shift,0, "Question#>> 0<") 
        stdscr.addstr(4 + shift,0, "'Group_Name' followed by SPACE separated member list in student id format <lastnm>_<stud_id>.")
        if phase %2 == 1:
            prompt = "Group_Nm M1 M2 ... Mn"
            descr = input(stdscr, prompt, descr, 5 + shift, 0)
            if descr == None:
                error = "cancelled"
                break
            descr = descr.strip()

            if len(oglist) == 0 and len(descr.split()) > 0: 
                # list is new, check that the group name is unique
                error = ""
                for row in rubric:
                    if 'Q0.' in row[0]:
                        gname=row[2].split()[0]
                        if descr.split()[0] == gname:
                            error = "Group Name '" + gname + "' is already defined at " + row[0]
                            return error, "", ""


        if phase %2 == 0 or (not " " in descr and len(descr) > 4):
            displayInp(stdscr, descr, 5 + shift, len(prompt), 0, False)
            newid, grView = editAssRubricCommQ0Disp(stdscr, ass, oglist, stdList, stdDict, grView, False)
            if newid == "_":
                get_id = False
            else:
                descr = descr + " " + newid

        descr, glist = sortGroup(descr)
    
        if ',' in descr:
            error = "List must be separated by spaces, don't use commas"
        elif len(glist) < 2:
            error = "Group must have name and at least 1 member"
        elif len(oglist) >=1 and len(oglist[0]) > 1 and oglist[0] != glist[0]:
            error = "Group name cannot be modified. Delete old group, add new. old='" + oglist[0] + "' new=" + glist[0]
        elif glist[0][0:6] != 'Group_':
            error = "Group name must use 'Group_' as prefix"
        else:
            # stdList, stdDict = getStudList()  # redudant search
            for stdident in glist[1:]:
                if not stdident in stdDict:
                    error = "Student '" + stdident + "' not found in class. Use <last_name>_<student_id>."
                    break

            if error == "":
                error = editAssRubricCommQ0lnks(ass, glist, oglist, rubric)

        if error != "":
            get_id = False

    return error, "", descr


def editAssRubricComm(stdscr, pts: str, descr: str, qnum: int, qask: bool, nnass: bool):
    """
    Edits a rubric comment, does basic input validation.

    @param stdscr: curses root object
    @param pts: default point value, or "" for empty
    @param descr: default description, or "" for empty
    @param qnum: whether this is special question 99, or 98, None otherwise
    @param qask: whether the question # was asked for or implied, determines placement of prompts
    @param nnass: allows definition of alt grading scheme prefix for q99

    @return: error, pts(updated point value), descr(update description)
    """

    shift = 0
    if not qask:
        shift = -1

    error = ""
    if qnum == 99:
        if nnass:
            stdscr.addstr(4 + shift,0, "q99 always hidden, ':?', ':%', ':A' notes, :[1-8] alt grading scheme, :9=50%, :8=45%, :[a-i] notes.")
            okprefix='?%A123456789abcdefghi'
        else:
            stdscr.addstr(4 + shift,0, "q99 always hidden, ':?', ':%', ':A' notes, :[a-i] notes.")
            okprefix='?%Aabcdefghi'
    elif qnum == 98:
            stdscr.addstr(4 + shift,0, "q98 special reports, ':r' report comment.")
            okprefix='r'
    else:
        stdscr.addstr(4 + shift,0, "Description prefixes = ':H' Hide Comment, ':n' custom value")
        okprefix='Hn'
    descr = input(stdscr, "Item Description", descr, 5 + shift, 0)
   
    if descr == None:
        descr = ""
        error = "cancelled"
    elif len(descr.strip()) < 3:
        error = "Description can't be empty and must have at least 3 characters."
    elif descr[0] == ':' and descr[1] not in okprefix:
        error = "Unsupported description prefix"
    else:
        if descr[0:2] == ':n':
            pts = '#.#'
        else:
            pts = input(stdscr, "item points [+-]#", pts, 6 + shift, 0).strip()
            if pts == None:
                error = "cancelled"
            elif not (pts == "" or
                   (pts[0] in "+-" and isfloat(pts[1:]) or 
                    isfloat(pts) )):
                error = "Incorrect score format, use [+-]#, or empty for no score" 
            else:
                if len(pts) == 1:
                    pts = " " + pts

    return error, pts, descr


prev_q="99"
def editAssRubricAddComm(stdscr, rubric: list, q: str, qask: bool, ass: str):
    """
    Add a new comment to the rubric.

    @param stdscr: curses root object
    @param rubric: complete grading scheme
    @param q: default question, can be ""
    @param qask: if false, request is coming from grading tool, don't ask for q, don't show rubric
    @param ass: the assignment number encoded as a string

    @return: error, rubric, q
    """
    global prev_q

    # nnass: the special notes assignment supports additional ':' comment codes
    nnass = ass == 'NN'

    error = ""
    if qask:
        if len(q) == 0:
            q = prev_q
        q = input(stdscr, "Question#", q, 3, 0).strip()
    else:
        assert q.isdecimal(), "Error in q parameter while adding comment to rubric"

    if q == None:
        error = "cancelled"
    elif not q.isdecimal():
        error = "Expected Integer Question #"
        row = len(rubric) - 1
    else:
        irow = -1
        for row in range(0, len(rubric)):
            if rubric[row][0] == "Q"+q+")":
                irow = row
        if irow == -1:
            error = "Question#" + q + " not defined"
        else:
            prev_q=q
            if q == "0" :
                error, pts, descr = editAssRubricCommQ0(stdscr, "", qask, ass, rubric)                
            else:
                error, pts, descr = editAssRubricComm(stdscr, "", "", int(q), qask, nnass)

            lrow = irow + 1
            maxit = 1;
            if pts.strip() == "0":   # put zeros at the top of the menu, no submission etc.
                pmatch = True
                lrow = irow + 1
            else:
                pmatch = False

            # find the longest match (min 2 chars) XXX new 2024
            lm = 2
            for row in range(irow+1, len(rubric)):
                ml=0
                while(len(rubric[row][2]) > (ml + 1) and len(descr) > (ml + 1) and 
                        rubric[row][2][ml] == descr[ml]):
                    ml += 1
                if ml > lm:
                    lm = ml

            #debug(None, str("longest match = " + str(lm) + " chars"))
            for row in range(irow+1, len(rubric)):
                # check for good match (first 8 chars)   # XXX fixed 2024.12.15
                # debug(None, str(str(row) + " " + str(lm)))
                if len(rubric[row][2]) >= lm and len(descr) >= lm:
                    if rubric[row][2][0:lm] == descr[0:lm]:   # if the lengths match convert scores to #s
                        if pmatch == False:
                            lrow = row  # start by placing it at the top.
                        pmatch = True
                        try: 
                            newFloat = float(pts)
                        except:
                            newFloat = 99999
                        try:
                            oldFloat = float(rubric[row][1])
                        except:
                            oldFloat = 99999
                        if newFloat > oldFloat or newFloat == 99999: # push it lower if we can       
                            lrow = row
                        # debug(None, str([lm, newFloat, oldFloat, pmatch]))
                # check for rough match for short items (first 4 chars)
                #elif pmatch == False and len(rubric[row][2]) > 3 and len(descr) > 3 and rubric[row][2][0:4] == descr[0:4]:
                #    pmatch = True
                #    lrow = row + 1
                # add to end of this question
                if ")" in rubric[row][0] or rubric[row][0] == "":
                    break
                if not pmatch: # if no match was found place the new item at the end 
                    lrow = row + 1
                maxit = max(int(rubric[row][0].split('.')[1]) + 1, maxit)

            # reposition highlight
            if qask:
                arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, lrow, True)

            if error == "":
               rubric.insert(lrow, ["  Q"+q+"."+str(maxit), pts, descr])

    return error, rubric, q, row


def editAssRubricAddQ(stdscr, rubric):
    """
    Adds a new question to the rubric

    @param stdscr: curses root object
    @param rubric: complete grading scheme

    @return: error, rubric(list of questions and comments), q(string numeric value), row# 
    """
 
    error = ""
    q = input(stdscr, "Question#", "", 3, 0)
    if q == None:
        error = "cancelled"
    elif not q.isdecimal():
        error = "Expected Integer Question #" + q
        row = len(rubric) - 1
    else:
        qok = True
        row = 0 
        while row < len(rubric):
            if ')' in rubric[row][0]:
                qnum = int(rubric[row][0][1:].split(')')[0])
                if qnum == int(q):
                    error = "Question#" + q + " Already Defined"
                    qok = False
                    break
                if qnum > int(q):
                    break
            row = row + 1
        if qok:    

            if int(q) == 0:
                error, pts, descr = editAssRubricQ0(stdscr, "", "")
            else:
                error, pts, descr = editAssRubricQ(stdscr, "", "")

            if error == "":
                rubric.insert(row, ["","", ""])
                rubric.insert(row, ["Q"+q+")", pts, descr])

    if error != "":
        q = ""

    return error, rubric, q, row

def editAssRubricRemQ(stdscr, rubric, q):
    """
    Remove a question from the rubric, and all of its associated comments.

    @param stdscr: curses root object
    @param rubric: complete grading scheme
    @param q: question in 'Q#)' format

    @return: error, rubric
    """
 
    error = ""
    qn = q[1:].split(')')[0]
    if qn == '99':
        error = "Cannot Remove Notes"
    else:

        qdel = False
        newrub = [rubric[0]]
        for rownum in range(1,len(rubric)):
            # remove both question and matching comments. 
            if "Q"+qn+")" in rubric[rownum][0] or "Q"+qn+"." in rubric[rownum][0]:
                qdel = True
            elif rubric[rownum][0] == "" and qdel:  # also rem trailing blank line
                qdel = False
            else:
                qdel = False
                newrub += [rubric[rownum]]
        rubric = newrub
    return error, rubric

def editAssRubricMov(stdscr, rubric: list, s: int):
    """
    Move a rubric comment to another row, either up or down in the grading scheme.

    @param stdscr: curses root object
    @param rubric: complete grading scheme
    @param s: rubric selection
    """
 
    error = ""
    m = 0
    while True:
        stdscr.clear()
        if rubric[s][0][0] != '>': 
            rubric[s][0] = '>>' + rubric[s][0]
        arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, s, True)
        menuInputH(stdscr, ["Add Question", "Add Comment", "Move Comment", "Edit", "Delete", "Find", "Save/Done"], 2, 0, 10, 0, 2, True)
        m = menuInputH(stdscr, ["Move Up", "Move Down", "Done"], 3, 0, 10, 0, m, False)

        if m == -1:
            error = "cancel"
            break
        if m == 0:
            if s>0 and '.' in rubric[s-1][0]:
                tmp = rubric[s-1]
                del rubric[s-1]
                rubric.insert(s,tmp)
                s = s - 1
        elif m == 1:
            if s < len(rubric) + 1 and '.' in rubric[s+1][0]:
                tmp = rubric[s+1]
                del rubric[s+1]
                rubric.insert(s,tmp)
                s = s + 1
        else:
            rubric[s][0] = rubric[s][0][2:]
            break
     
    return error, rubric, s

def editAssRubricCopyQ(stdscr, ass, rubric):

    # build list of known question #s
    qs=[]  # string version of Q
    qn=[]  # numeric version of Q
    qr=[]  # row in rubric that Q is located at

    for s in range(0, len(rubric)):
        if ')' in rubric[s][0] and '.' not in rubric[s][0]:
            qstr=rubric[s][0]
            qs.append(qstr)
            qstr=qstr.strip("Q").strip(")")
            qn.append(int(qstr))
            qr.append(s)

    q1m = menuInputH(stdscr, qs, 3, 0, 0, 0, 0, False)
    if q1m == -1:
        return ""
    q1n = int(qs[q1m].strip("Q").strip(")"))
    q2 = input(stdscr, "New Q#","", 4, 0)
    if q2 == None or len(q2) < 1:
        return ""
    try: 
        q2n = int(q2)
    except:
        return "Expecting an Integer"

    if q2n < 2:
        return "Expecting an integer >= 2"
   
    if q2n in qn:
        return "Question # Already Exists"

    qCopy=[["","",""]]

    for r in range(qr[q1m],len(rubric)):
        newrow = rubric[r][:]
        if len(newrow[0]) == 0: # found the end, we are done
            break
        if ')' in newrow[0]:
            newrow[0] = "Q" + str(q2n) + ")"
        else:
            newrow[0] = "  Q" + str(q2n) + "." + newrow[0].split('.')[-1]
        qCopy.append(newrow)
    
    # find the spot to insert the copy
    i = 0    
    while i < len(qr):
        if q2n < qn[i]:
            break
        i = i + 1

    if i == len(qr):
        drow = len(rubric)
    else:
        drow = qr[i] - 1

    # insert the copy in reverse
    for r in range(len(qCopy) - 1, -1, -1):
        rubric.insert(drow, qCopy[r])

    return ""

def editAssRubricGetStats(stdscr, ass, rubric_in):
    """
    Compute the frequency that each comment is reported

    @param ass: assignment id
    @param rubric_in: rubric to generate statistics for

    @return a variation of the rubric that includes usage statistics
    """


    # copy the rubric because we are going to modify it in a way that breaks it
    rubric_disp = []

    for s in range(0, len(rubric_in)):
        key = rubric_in[s][0]
        rubric_disp += [[""] + rubric_in[s]] 
        if '.' in key:
            klist, kdict = genStudKeysScores(rubric_in, ass, key)
            stat = len(kdict)
            if stat > 0:
                rubric_disp[s][0] = "[" + str(len(kdict)) + "]"
            else:
                rubric_disp[s][0] = " 0 "
                
    return rubric_disp

def editAssRubricMenu234(stdscr, m, rubric, s, ass):
    """
    Handle rubric edit menu items 2, 3 and 4, move, edit, delete, each involves a selection

    @param m - last horizontal menu selection (2..5)
    @param rubric - list of rubric comments
    @param s - line selected from rubric, will be a comment
    @param ass - assignment id

    """

    error = ""

    if m == 2:  # move
        if '.' not in rubric[s][0]:
            error = "Can only move comments, not whole question"
        else:
            error, rubric, s = editAssRubricMov(stdscr, rubric, s)

    elif m == 3 and (')' in rubric[s][0] or '.' in rubric[s][0]): # edit
        if ')' in rubric[s][0]:
            if rubric[s][0] == 'Q0)':
                error, pts, descr = editAssRubricQ0(stdscr, rubric[s][1], rubric[s][2])
            else:
                error, pts, descr = editAssRubricQ(stdscr, rubric[s][1], rubric[s][2])
        elif '.' in rubric[s][0]:
            if 'Q0.' in rubric[s][0]:
                error, pts, descr = editAssRubricCommQ0(stdscr, rubric[s][2], True, ass, rubric)
            else:
                error, pts, descr = editAssRubricComm(stdscr, rubric[s][1], rubric[s][2], 
                        99 if 'Q99.' in rubric[s][0] or 'Q99)' in rubric[s][0] else 
                        98 if 'Q98.' in rubric[s][0] or 'Q98)' in rubric[s][0] else None, True, ass=='NN')

        if error == "":
            edItem = [rubric[s][0], pts, descr]
            rubric[s] = edItem

    elif m == 4: # delete
        key = rubric[s][0]
        if '.' in key or ')' in key:
            klist, kdict = genStudKeysScores(rubric, ass, key)
            if len(kdict) > 0:
                error = "Found " + str(len(kdict)) + " students referencing " + key + ", cannot delete"
            else:
                if ')' in rubric[s][0]:
                    error, rubric = editAssRubricRemQ(stdscr, rubric, key)
                elif '.' in key:
                    del rubric[s]
                if s > len(rubric) - 1:
                    s = len(rubric) - 1

    return error, rubric

