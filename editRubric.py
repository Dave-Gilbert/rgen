#!/usr/bin/python3
#
from cwidgets import *
from dataIO import *
from pathlib import Path
import os
    

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
    if descr != '' and descr[0] == ':' and descr[1] not in 'Hh':
        error = "Unsupported description prefix"
    else:
        pts = input(stdscr, "Total Points", pts, 6, 0)
        if not pts.strip().isdecimal():
            error = "Expected Integer Point Total"
        else:
            if len(pts) == 1:
                pts = " " + pts

    return error, pts, descr

def editAssRubricComm(stdscr, pts: str, descr: str, q99: bool):
    """
    Edits a rubric comment, does basic input validation.

    @param stdscr: curses root object
    @param pts: default point value, or "" for empty
    @param descr: default description, or "" for empty
    @param q99: whether this is special question 99

    @return: error, pts(updated point value), descr(update description)
    """

    error = ""
    if q99:
        stdscr.addstr(4,0, "q99 always hidden, ':?' or ':%' notes")
        okprefix='?%'
    else:
        stdscr.addstr(4,0, "Description prefixes = ':H' Hide Comment, ':n' custom value")
        okprefix='Hn'
    descr = input(stdscr, "Item Description", descr, 5, 0)
    
    if descr != '' and descr[0] == ':' and descr[1] not in okprefix:
        error = "Unsupported description prefix"
    else:
        if descr[0:2] == ':n':
            pts = '#.#'
        else:
            pts = input(stdscr, "item points [+-]#", pts, 6, 0).strip()
            if not (pts == "" or
                   (pts[0] in "+-" and pts[1:].isdecimal()) or 
                    pts.isdecimal()):
                error = "Incorrect score format, use [+-]#, or empty for no score" 
            else:
                if len(pts) == 1:
                    pts = " " + pts

    return error, pts, descr


def editAssRubricAddComm(stdscr, rubric: list, q: str):
    """
    Add a new comment to the rubruc.

    @param stdscr: curses root object
    @param rubric: complete grading scheme
    @param q: default question, can be ""

    @return: error, rubric, q
    """
 
    error = ""
    q = input(stdscr, "Question#", q, 3, 0).strip()
    if not q.isdecimal():
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
            lrow = irow + 1 # XXX double check +1
            maxit = 1;
            for row in range(irow+1, len(rubric)):
                if ")" in rubric[row][0] or rubric[row][0] == "":
                    break
                lrow = row
                maxit = max(int(rubric[row][0].split('.')[1]) + 1, maxit)
            # reposition highlight
            arrayRowSelect(stdscr, rubric, 8, 0, 0, 8, 0, lrow, True)

            error, pts, descr = editAssRubricComm(stdscr, "", "", int(q) == 99)
            if error == "":
               rubric.insert(row, ["  Q"+q+"."+str(maxit), pts, descr])

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
    if not q.isdecimal():
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



