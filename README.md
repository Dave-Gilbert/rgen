# rgen
## A Dynamic Rubric Generator

Rgen is a computer program that provides a comprehensive and dynamic rubric
generator for tests and assignments, combined with a course grade management
system. Rgen tightly integrates rubric design with assignment grading, allowing
the two tasks to procede iteratively. Rgen also integrates data generated by
several Mohawk College student data systems, generates student grade overview
reports with consistent comments, tracks student course progress, and computes
final grades.

**1. Rubric Construction**
  * Constructs a menu of comments with point values for each assignment question.
  * Point values can be fixed, partial additive, subractive or empty.
  * Rubric design and homework evaluation are presented as a unified task. 

**2. Homework and Assignment Grading**
  * Homework scores and class averages are calculated as comments are applied.
  * Grading and rubric generation are tightly integrated, the workflow is bidirectional.
  * Edited comments and updated scores are re-applied to all evaluations automatically.

**3. Student Record Management, Tool Integration**
  * Builds student record templates from FastSuite data, including name, e-mail, student IDs etc. 
  * Imports grades generated by MyCanvas, on a per assignment basis.
  * Imports attendance records from online Zoom sessions.

**4. Supports Student Views and Faculty Views**
  * Additional notes are incorporated that are hidden from student views.
  * Hidden notes can be kept for both assignments, and student records.

**5. Rgen is written in Python, is simple, portable and extendable**
  * Tool supports data import and export via plain text .csv files.
  * User interface is portable, text based and menu driven.
  * Grade reports can be printed, e-mailed, or pasted into existing LMS.

## Introduction

Rubrics are tools for grading student papers that facilitate generating
consistent grades, and minimizing the amount of time spent writing 
descriptive notes on individual papers.

Ideally the instructor writes a list of goals to be met by a student
submission, and when grading tests or homework submissions the goals can be
used as a checklist. The core assumption of a rubric is that most students will
make similar mistakes, and it is helpful to write a detailed description of
common errors that can be given to students as part of providing feedback. The
rubric might be implemented with a spread sheet or might be a checklist printed
on a sheet of paper, which is marked up by the instructor. Mohawk College's
Learning Management System (LMS) MyCanvas provides a static rubric tool
modeled on the classical notion of a 2 dimensional scoring table. There are
many good books on this subject, see for example __Introduction to Rubrics__ by
Stevens and Levi, 2005.  The following rubric is taken from this book:

![Example Rubric, Stevens 2005](https://github.com/Dave-Gilbert/rgen/blob/main/images/Stevens_Example_Rubric_p70.png)

When I started teaching at Mohawk College I tried to build rubrics with
spreadsheets by grading a few homework submissions to get a sense of what
students typically did, and then I would write out a checklist for each
question.  Problems arose when I tried to apply this early draft of my
checklist to the rest of the student submissions. I would notice patterns later
on that I hadn't imagined, or decide that a grade item that I originally
believed would be important hardly ever came up. I would often rewrite the
comment columns of my spreadsheet based rubric when I was half done grading an
assignment and then recopy these columns into partially graded answer sheets. I
regularly regraded many of the submissions I looked at initially after having
completely surveyed all the submissions in an attempt to ensure that specific
comments were consistent. Sometimes one student would do something odd, I'd
make a comment on it, but then forget which student had written the unusual
answer and spend a lot of time looking for it. The process was tedious and
error prone.

I also ran into some persistent bookkeeping problems. For each assignment I
needed to build a rather complicated multi-page spreadsheet that had each
student's name and id associated with each rubric. Individual students would
sometimes make special requests for extensions, or have other issues with their
assignment that required some additional attention. Merging this data at the
end of a course was time consuming. While a spreadsheet could nicely handle
addition, it didn't help much with file management, and I couldn't figure out a
good way to merge several multi-page spreadsheets automatically.

After a while I realized that my primary frustration with grading student
papers was not about really reading through all their solutions, or considering
how to evaluate the sometimes strange answers my students wrote, but it boiled
down to too much fiddly note keeping. Efficiently keeping track of all the
small details, correctly handling endless columns of numbers, finding all the
relevant notes, and providing consistent commentary ate up huge amounts of
time. This was my motivation for developing Rgen, to automate bookkeeping and
consistency tasks, so I could focus on thinking about what my students had
learned in the recent weeks of the course.

## Rgen Student-View, Final Report

Rgen's purpose is to build rubrics that can be easily used to grade homework,
automatically generate a custom grade sheet for each student, and merge
those grade reports into a single end of term summary for the course.

The following table shows grades collected for the first term test for an
introductory course in computer programming. Each row in the table summarizes
the test results for a single student. Actual student names have been removed
from the screen-capture. This bird's eye perspective shows per question
averages giving a detailed snapshot of the first term test for the course.

![Example Student Grade Sheet](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_10.png)

The table is also a menu. By highlighting a specific student and pressing
enter, the detailed comments given for each question can be viewed.

The following grade sheet shows question scores and typical comments supplied
for an example student. In this test, questions 2 through 7 were automatically
graded by the Mohawk College LMS MyCanvas, and these scores were manually
entered in to Rgen. MyCanvas has no way to export partial test answers, so some
manual data entry is necessary.

![Example Student Grade Sheet](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_1.png)

Scores are calculated in several ways, 2 are shown in the preceding example.  A
fixed value score can be entered, this strategy is used in questions 1 - 7.
Questions 8, 9 and 10 were scored subtractively by deducting points from a
total. Each deduction includes an explanatory comment. Rgen includes error
checks that prevent negative scores and prevent multiple contradictory fixed
scores.  Rgen also supports additive comments, where scoring starts at zero and
each comment increases total for the question.

In the case of multiple choice
quizzes or other evaluations that are completed within within MyCanvas,
MyCanvas scores can be downloaded and merged with other data collected by Rgen.
The following view shows a partial grade calculation for a student listing
scores for the first few assignments and the first test. The second term test,
final assignment and final exam have not yet been added to the totals. 

![Example Student Final Grade](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_9.png)

The student's grade is recorded as a fraction of the course work completed in
this view. Total Zoom attendance in hours is recorded as 0 for the example
student. Any special notes made on the student's work will also be displayed in
this view.

## Rgen Adding Comments

Starting from the top level student information view an instructor selects
"Enter Grades" from the horizontal menu and is presented with a table of tests
and assignments for the course and their associated weights. "T1" is the first
term test in the course. 

![Selecting a Term Test](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_12.png)

When grading a question, the instructor may choose to grade a single question
or a small group of questions for each student. Question #8 is worth 10
points. It asked students to write a short Python if ... elif ... else
structure that converted a 3 letter month to a yearly quarter, i.e. "Jan" ->
"Q1", "Feb" -> "Q1", "Dec" -> "Q4".

![Selecting a Question to Grade](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_11.png)

The following menu is used to provide comments and grades for a single
question. The menu at the top shows a list of comments and their associated
scores which the instructor may select from, these are selected and added to
the students comment list, shown at the bottom of the screen. Rgen computes the
total score for the question as comments are appended. In this example the
student has made 3 common mistakes, and scores 5/10 total. 

![Example Student Evaluating Q](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_2.png)

Some comments have fixed point values assigned to them, i.e.  "0   no answer"
and "10    Good". Some comments have no point value associated with them,
others show -1, -2, or -4 and are meant to be selected in combination. 

By selecting the "Next" menu option at the bottom of the comment list Rgen will
load the next student's comment list for the same question, and so on, until
the selected question group has been graded for the entire class.

## Rgen Modifying a Rubric

The Rubric editor is accessible from the question grading menu.

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_3.png)

Very experienced instructors may be quite good at anticipating common student
errors and able to write a complete rubric in advance of grading an assignment.
While Rgen supports this, its strength is that it allows quick access to the
rubric edit menu from the grading menu, and allows fluid development of the rubric.

The idea is that it should be easy to switch back and forth between adding
comments to student evaluations, and creating new comments for the rubric.  It
is often the case that patterns in student understanding are revealed only
during grading. 

If an existing comment's score is modified and several students have received
the comment, the system will recalculate all grades. Rgen includes a check for
question scores that go over the maximum or under the minimum and will generate
a warning until all scores fit within the prescribed ranges.

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_4.png)

Comment codes are exposed when grading student work, they include the question
number and a decimal point followed by a comment number i.e.  "Q8.1", "Q8.2"
through "Q8.14" are visible in this example, but are hidden in the student
view. Internally, Rgen associates comment codes with student grade records, and
must merge the rubric with the student record each time it generates a student
grade report. This ensures that each student grade report will always use the
most recent version of the rubric when it is generated.

The order that comments are presented in can be modified by editing the rubric
and moving comments either up or down in the selection menus. In the above
example comments are grouped by first by severity, then by type. This makes
finding a comment in a list easier.  The same order is generated in the
student's version which can help with clarity, again by keeping related remarks
grouped.

Comments can be removed from the rubric only if they have not been applied to
any student's work. The following screencap shows a warning displayed by Rgen
when trying to delete a comment which has already been applied to several grade
reports. 

![Preventing Deletion](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_13.png)

## Rgen Searching for Students with particular Comments

An interesting feature provided by Rgen is the ability to search for students
who have received a particular comment. This gives the grader a simple way to
check consistency, or gain an understanding of who is struggling in the course
with a particular concept. The "Find" option can be run from either the grading
menu or the rubric editor menu. 

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_5.png)

In the following search result, 4 students did not answer question #8. Full
names have been obfuscated with a grey box, leaving first two letters for
reference. This same group also did quite poorly on the test as this summary
screen shows. The first student "Be" asked to be excused from the test.
Question #99 is only shown in the instructor's view and includes the '%' symbol
hinting that this student's grade will need special calculation at some point.
Reviewing the detailed scores for student "Be" will show the full comment under
Q99, the symbol is a reminder of this student's special circumstances on this
test.

![Example Search](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_6.png)

## Rgen Other Features

Rgen includes a collection of course management features. 

MyCanvas will export summary grade spreadsheet for a course in .csv format
which record results for each assignment and student recorded so far.  Rgen can
construct an "imported" rubric and merge in data from MyCanvas, identifying the
source file from which grades were derived as part of constructing a complete
report.

![Data Import](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_8.png)

Rgen computes a grade in progress for each student as well as adding up the
number of hours the student has attended Zoom lectures. Zoom has a feature
where it can require that students log in only with an e-mail address from a
specific domain. When that address is restricted to the mohawkcollege.ca
domain, Zoom's report can be downloaded and student's attendance records can be
matched via their e-mail addresses. While Mohawk College does not provide
credit for attendance, having a sense of who participates in live discussions
can be helpful.

![Top Level Info](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_7.png)

Special notes are tracked with symbols in the last column. These notes can be
added to tests or to the root student record. A few symbols are built in with
various suggested meanings including '!', '\*', '%', and '?'. These can be used
to track who has made unusual requests, has missed an evaluation, or has a
special accommodation.

From the top level student information view the individual student's detailed
records can be viewed. This same view will also show the details for any
special notes that are relevant to this student. This view can also be used to
drill down into the individual assignments and review or edit details.

![Example Student Record](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_9.png)

## Anecdotal Conclusions

Prior to using this rubric generating tool I used a variety of different
grading strategies. 20 years ago when I was in graduate school the norm was to
sit down with a stack of homework assignments and write on each with a red pen.
I found this style of grading extremely difficult. I've only worked at the
college for a few years. During my first year I relearned how to use a
spreadsheet, following the lead of senior staff who would often communicate
grading templates via spreadsheets. MyCanvas, the learning management system
used by the college includes a static rubric system. These must be set up in
advance of student submissions, and don't seem very flexible to me.

I wrote the initial version of Rgen in a few weeks at the start of the summer
semester and have been using it to evaluate student homework and test
submissions since then. With each homework assignment that I grade I find a few
bugs or limitations in Rgen that I fix. Generally I find that I grade and
return things much faster than I did in the past, and that the supplied
comments are far more detailed than I would normally be able to provide.  I
believe that the consistency of the remarks and the shorter grading times
contribute to better learning outcomes, and generally happier students.

I occasionally suffer from wrist strain. It is an occupational hazard in
computing. I've spent time optimizing the menus in Rgen to minimize key
strokes. While its still necessary to type in comments the first time, I find
its much easier to navigate simple menus with cursor keys than it is to scroll
through spreadsheet cells, and switch back and forth between a mouse and keyboard, 
or constantly retype remarks into spreadsheet cells.

## Bugs and Rough Edges

The current draft should be considered working and feature complete for common
tasks, but still beta software.

Some obvious features are missing. Initial setup requires the creation of a
special data directory. The .csv file downloaded from FastSuite must be copied
to a particular location and given a specific name, and the list of course
assignments, and their associated weights is assumed to be present. These
details require documentation and automation. The current version includes
some sample files. See:

course\_data/fs\_student\_list.csv             # CSV student data file downloaded from Fast Suite
course\_data/course\_assignments.csv           # Static course description, modify with text editor
course\_data/Zoom\_Attendance/empty\_data.csv  # zoom data files may use any name

Rgen will build out the rest of the file structure based on these initial
files.  You can extend the student list or the assignments list at any time,
although currently this functionality is not menu driven, but can be done with
a text editor.

Rgen is generally reliable, although there are no guarantees. 

There are a few corner cases that cause the code to generate exceptions. Rgen
can be restarted in cases like this without any data loss. 

Each time a modification to either a rubric or a student's grade is made Rgen
will save the update to a .csv file on the disk. Very little state information
is kept in memory without saving it to disk. Performance concerns were ignored
for the sake of reliability.

Rgen may destroy all of your student grades and notes for a course. My personal
file system is backed up regularly, backups are essential when working with
sensitive data.

Rgen uses the curses library for character based screen management and has been
developed within a Linux bash environment. The curses library will normally be
pre-installed on any Unix installation but must be installed separately in
Windows. See:

[https://pypi.org/project/windows-curses/](https://pypi.org/project/windows-curses/)

Rgen works in Windows, although I've only done minimal testing.

Work is ongoing. If you have any questions you can reach me via gmail at:

dave.wm.gilbert@gmail.com

