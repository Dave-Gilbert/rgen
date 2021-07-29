import csv 
import os
import errno
from cwidgets import *

def getStudList():
    """
    Generate a list of basic student information pulled from the FastSuite file.

    @return: studList = [studkey, ID, name, e-mail addr], studDict (same, indexed by studkey)
    """

    # verify that a class list file is present in the current directory
    # open will throw an exception otherwise
    pathSl=os.getcwd()+'/course_data/'+'fs_student_list.csv'
    open(pathSl)

    studList1 = importFastSuiteCSV(pathSl)
    ostudList = []

    studDict = {}
    for stud in studList1:
        lname = (stud[1].split(',')[0]).split(' ')[0]
        lname = lname[:12]  # trim last names to 12 characters
        studkey = lname + '_' + stud[0]
        studDict[studkey] = [stud[0], stud[1], stud[2]]
        ostudList += [[studkey] + stud]
    

    return ostudList, studDict

def importFastSuiteCSV(path: str):
    """
    Import the fast suite data file, ignore the first row

    @param path: refers to .csv file downloaded from Fast Suite

    @return: an array version of three essential columns, id, name, e-mail addr
    """
    
    retval = []
    with open(path, newline='') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        firstRow = True
        for row in filereader:
            if firstRow:
                pass
                firstRow = False
            else:
                retval += [[row[0], row[1], row[8]]]
    assert(len(retval) > 0)
    return retval


def importCSV(path: str):
    """
    Import a generic CSV file. Ignore empty rows, warn if the input fails for some reason.

    @param path: refers to generic .csv file, ignore blank lines

    @return: an array version of csv
    """
    
    retval = []
    if not os.path.isfile(path):
        return None

    with open(path, newline='') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',', quotechar='"')
        
        try:
            for row in filereader:
                if len(row) > 0:
                    retval += [row]
        except:
            # some problem with the data
            debug(None, "Incomplete read for " + path)
            pass

    return retval

total_exports = 0

def exportCSV(path: str, outdata: list):
    """
    Carefully export data, backup files before export, count total export operations.

    @para path: full path and file name
    @param outdata: list of lists to export
    """

    global total_exports

    total_exports += 1

    if total_exports % 100 == 0:
        debug(None, "Exporting a lot of files, count = " + str(total_exports))

    # if backup exists, rais an exception, we were likely interrupted
    # while exporting data, which isn't okay.
    assert not os.path.isfile(path + '.bak'), "Error during exportCSV. Found: " + path + '.bak'

    if os.path.isfile(path):
        os.rename(path, path + '.bak')
    
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(outdata)

    if os.path.isfile(path + ".bak"):
        os.remove(path + ".bak")

def buildAssDir(cAss: list):
    """
    Build the assignment directory structure, populate with default rubric files.

    @param cAss: course assignment list

    """
        
    pathA=os.getcwd()+'/course_data/assignments/'
    try:
        os.mkdir(pathA, mode=0o755)
    except OSError as e:
        # ignore file exists errors
        if e.errno != errno.EEXIST:
            raise

    for row in cAss:
        pathA=os.getcwd()+'/course_data/assignments/'+row[0]+'/'
        try:
            os.mkdir(pathA, mode=0o755)
        except OSError as e:
            # ignore file exists errors
            if e.errno != errno.EEXIST:
                raise

        try:
            f = open(pathA + '0_rubric.csv')
        except:
            # assume file not present, try to create
            pts = row[1]
            if len(pts) == 1:
                pts = " " + pts

            rubric=[["Total", pts, ""], ["","",""], ["Q99)", "0", ":H Notes"], ["","",""]]
            exportCSV(pathA + '0_rubric.csv', rubric)

def importZoomAttendData(stdList, stdDict):
    """
    Import Zoom attendance files. 

    @param stdList: list of all student data from fast suite
    @param stdDict: dictionary of student keys vs. basic infor

    @return: studKeyVsZTimeDict - a dictionary returning zoom view hours vs student keys
    """

    emailDict = {}
    studKeyVsZTimeDict = {}
    # Zoom stores @mohawkcollege.ca e-mails in two formats, 
    # <name>@mohawkcollege.ca and <studid>@mohawkcollege.ca
    for row in stdList:
        email=row[3]
        email_alt=row[1]+'@mohawkcollege.ca'
        if email != '':
            emailDict[email] = row[0]
        emailDict[email_alt] = row[0]
        studKeyVsZTimeDict[row[0]] = 0
    
    pathZoom = os.getcwd()+'/course_data/Zoom_Attendance' 
    zoom_files = os.listdir(pathZoom)

    for zfile in zoom_files:
        zatt = importCSV(pathZoom +'/' + zfile)
        for row in zatt:
            if len(row) > 1 and row[1] in emailDict:
                studkey = emailDict[row[1]]
                studKeyVsZTimeDict[studkey] += int(row[2]) / 60

    return studKeyVsZTimeDict


def importMyCanvasData(stdscr, ass: str):
    """
    Select data to import an assignment from. Data files are assumed to be from myCanvas

    @param stdscr: curses window
    @param ass: student assignment

    @note
    This function builds a template rubric which stores the name of the source
    file that the grade came from. Source data is hidden in the student view.
    """

    stdscr.clear()

    pathGrades=os.getcwd()+'/course_data/assignments/'+ass
    
    # expect there to always be at least an empty template rubric
    rubric = importCSV(pathGrades + '/' + '0_rubric.csv')
    if len(rubric) != 4 or rubric[2] != ['Q99)','0',':H Notes']:
        debug(stdscr, rubric)
        stdscr.addstr(3, 0, "Rubric not empty, check directory contents and manually delete to overwrite")
        s = arrayRowSelect(stdscr, rubric, 5, 0, 0, 8, 0, 0, False)
        return
     
    stud_files = os.listdir(pathGrades)
    stud_files.sort()

    files2d = []
    if len(stud_files) > 2:
        for item in stud_files[1:]:
            sgrade = importCSV(pathGrades+'/'+item)
            if len(sgrade) !=1 or sgrade[0] != ['Q99)','0','']:
                stdscr.addstr(3, 0, "Student Grade already populated, check directory contents and manually delete to overwrite.")
                s = arrayRowSelect(stdscr, [['filename: ' + item, '','']] + sgrade, 5, 0, 0, 8, 0, 0, False)
                return

    pathCanvas=os.getcwd()+'/course_data/myCanvas_Grade_Export'
    all_files = os.listdir(pathCanvas)
    all_files.sort()
    stdscr.addstr(3, 0,"Select File To Import Data for " + ass)

    # reformat input list as 2D array
    files2d = []
    for item in all_files:
        files2d += [[item]]
    s = arrayRowSelect(stdscr, files2d, 5, 0, 12, 8, 0, 0, False)

    stdscr.addstr(13, 0,"Select Grade Item to import for " + ass)

    fileCanvas = os.getcwd()+'/course_data/myCanvas_Grade_Export/'+files2d[s][0]

    allData = importCSV(fileCanvas)
    selectRow = []
    for col in range(6, len(allData[0])):
        if not 'read only' in allData[2][col]:
            selectRow += [[allData[0][col], '/ '+ allData[2][col]]]

    assCol = arrayRowSelect(stdscr, selectRow, 14, 0, 0, 8, 0, 0, False) + 6

    total =  ((selectRow[assCol][1].split('/')[1]).split('.')[0])

    newRubric = [['Total',total, ''],
                 ['','',''],
                 ['Q1)',total,':H Imported from '+files2d[s][0]],
                 ['Q1.1','', ':i Imported grade'],
                 ['','',''],
                 ['Q99)',0,':H Notes'],
                 ['','','']]
    
    exportCSV(pathGrades + '/' + '0_rubric.csv', newRubric)

    stdList, stdDict = getStudList()

    for student in stdList:
        for row in allData:
            if row[2] == student[1]:
                # found student ID match, build grade record
                sdata=[['Q1)',total,'Q1.1{'+row[assCol] + '}'],
                       ['Q99)',0,'']]
                exportCSV(pathGrades + '/' + student[0] + '.csv', sdata)


