# rgen
## A Dynamic Rubric Generator

Rgen is a computer program that provides a comprehensive rubric generator for
tests and assignments, combined with a course grade management system. The
feature set is based on my needs as an instructor at Mohawk College. Rgen
integrates data generated by several Mohawk College student data systems,
allows the dynamic construction of rubrics used for evaluation, generates
student grade overview reports with consistent comments, tracks student course
progress, and computes final grades.

1. Rubric Construction:
 * A rubric can be built before evaluation, or modified after student work has been graded.
 * Allows update of rubric comments, or comment scores during grading.
 * Comments can be edited to clarify, generalize, or fix mistakes.
 * Edited comments and scores are re-applied to all evaluations automatically.

2. Homework and Assignment Grading:
 * The generated rubric can immediately be used to grade homework submissions.
 * Grading and rubric generation are tightly integrated.
 * Grading homework, and evaluation design are presented as a unified task. 

3. Student Record Management:
 * Builds student record templates from FastSuite data. Name, e-mail, IDs etc. 
 * Imports grades generated by MyCanvas, on a per assignment basis.
 * Imports attendance records from online Zoom sessions.
 * Generates assignment, test comments and grade summaries.
 * Track special student issues, though extra notes system.

4. Supports Student Views and Faculty Views:
 * Additional notes are incorporated that are hidden from student views.
 * Hidden notes can be kept for both assignments, and student records.

5. Rgen is written in Python, is simple, portable and extendable.
 * Tool supports data import and export via plain text .csv files.
 * Import functions are simple and easily adaptable to other systems.
 * Interface is text based and menu driven, based on the curses library.
 * Grade reports can be printed, e-mailed, or pasted into existing LMS.

## Introduction

Rubrics are tools for grading student papers that facilitate generating
consistent grades, and minimizing the amount of time spent writing notes on
individual papers.

Ideally the instructor writes a list of goals to be met by a student
submission, and when grading tests or homework submissions the goals can be
used as a checklist. The core assumption of a rubric is that most students will
make similar mistakes, and it is helpful to write a detailed description of
common errors that can be given to students as part of providing feedback. The
rubric, might be implemented with a spread sheet or might be a checklist
printed on a sheet of paper, which is marked up by the instructor. Mohawk
College's LMS provides a static rubric system modeled on the classical notion
of a 2 dimensional scoring table. There are many good books on this subject,
see for example __Introduction to Rubrics__ by Stevens and Levi, 2005.  The
following rubric is taken from this book:

![Example Rubric, Stevens 2005](https://github.com/Dave-Gilbert/rgen/blob/main/images/Stevens_Example_Rubric_p70.png)

When I started teaching at Mohawk College I tried to build rubrics with
spreadsheets by grading a few homework submissions to get a sense of what
students typically did, and then I would write out a checklist for each
question.  Problems arose when I tried to apply this early draft of my
checklist to the rest of the student submissions. I would notice patterns later
on that I hadn't imagined, or decide that a grade item that I believed would be
important, hardly ever came up. I would often rewrite the comment columns of my
rubric and then recopy them into the students answer sheets, or redo my initial
evaluations after having completely surveyed all the submissions. The process
was tedious and error prone.  

I also ran into some persistent bookkeeping problems. For each assignment I
needed to build a rather complicated multi-page spreadsheet that had each
student's name and id associated with each rubric. Individual students would
sometimes make special requests for extensions, or have other issues with their
submission that required some additional attention. Merging this data at the
end of a course was also time consuming. While a spreadsheet could nicely
handle addition, it didn't help much with file management, and I couldn't
figure out a good way to merge several multi-page spreadsheets automatically.

## RGEN Student-View, Final Report

Rgen's purpose to automatically generate a custom grade sheet for each student, and merge those sheets into a single end of year report. 

The following table shows grades collected for the first term test. Each row in the table summarizes the grades for a single student. This birds eye perspective with per question averages gives a detailed snapshot into the first term test for the course.

![Example Student Grade Sheet](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_10.png)

The following grade sheet shows average scores and typical comments supplied
for an example student for the same test. In this test, questions 2 through 7
were automatically graded by the Mohawk College LMS MyCanvas, and these scores
were copied in to RGEN. Unfortunately MyCanvas has no way to export partial
test answers, so some manual data entry is necessary. The real work is saved in
generating comments for the long answer questions which can be quite
complicated. 

![Example Student Grade Sheet](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_1.png)

Scores are tabulated in several ways, 2 are shown in the preceding example.  A
fixed value score can be entered, this strategy is used in questions 1 through
7 where a comment is attached to a score for the question. Questions 8, 9 and
10 deduct points from a total for various mistakes. Each deduction includes an
explanatory comment. The system includes obvious error checks that prevent
negative scores, or providing multiple contradictory fixed scores.  

While MyCanvas will not export grades on a per question basis it will export
full grade sheets. In the case of multiple choice quizzes which are
automatically graded within myCanvas, these scores can be downloaded and merged
with other data collected by Rgen. The following view shows a partial grade
calculation which includes several course assignments, although the second term
test, final assignment and final exam have not yet been added to the totals. 

![Example Student Final Grade](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_9.png)

This kind of partial grade calculation can be very helpful when communicating
with students about their progress in the course. 

## RGEN Adding Comments

When grading a question, the instructor may choose to grade a single question
or a small group of questions in sequence for each student. The following menu
is used to grade a question and provide notes for the student. The menu at the
top shows a list of comments and their associated scores which the instructor
may select from. Rgen computes the total score for the question as comments
are added. In this example the student has made 3 common mistakes, and scores
5/10 total. 

![Example Student Evaluating Q](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_2.png)

The menu presents a list of 14 different possible comments.  Some comments have
fixed point values assigned to them, i.e.  "0 no answer" and "10 Good". Some
comments have no point value associated with them, others show -2, or -4
points. 

## RGEN Modifying a Rubric

The Rubric editor is accessible from the question grading menu.

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_3.png)

New comments can be added to the rubric, or existing comments can be modified at any point.

If an existing comment's score is modified and several students have received
the comment, the system will recalculate all grades. This can lead to some
surprising results. Rgen includes a check for question scores that go over the
maximum or under the minimum and will generate a warning until scores fit
within the prescribed ranges.

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_4.png)

Comment codes are exposed when grading student work, they include a decimal
point, "Q8.1", "Q8.2" etc., but are hidden in the student view.  Comments are
numbered internally in the order that they are created, but the order of
presentation can be modified by editing the rubric. In the above example
comments are grouped by type and severity. This makes finding a comment in a
list easier. The same order is generated in the student's version which can
help with clarity, again by keeping related remarks grouped.

## RGEN Searching for Students with particular Comments

An interesting feature provided by rgen is the ability to search for students
who have received a particular comment. This gives the grader a simple way to
check consistency, or gain an understanding of who is struggling in the course
with a particular concept. The "Find" option can be run from either the grading
menu or the rubric editor menu. 

![Example Editing Rubric](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_5.png)

In the following search result, 4 students did not answer question #8. This
same group also did quite poorly on the test as this summary screen shows. The
first student "Be" asked to be excused from the test.  Question #99 is only
shown in the instructor's view and includes the '%' symbol hinting that this
student's grade will need special calculation at some point.  The others
struggled with the rest of the test, suggesting that question 8 was understood
by the majority of the group. Reviewing the detailed scores for student "Be"
will show the full remark under Q99.

![Example Search](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_6.png)

## RGEN Other Features

Rgen includes a collection of course management features. It computes a grade in
progress for each student as well as adding up the number of hours the student
has attended Zoom lectures for. Zoom has a feature where it can require that
students log in only with an e-mail address from a specific domain. When that
address is restricted to the mohawkcollege.ca domain, Zoom's report can be
downloaded and student's attendance records can be matched via their e-mail
addresses. While Mohawk College does not provide credit for attendance, when
discussing a student's progress it is helpful to know whether they have been making
an effort to participate in online Zoom lectures, or not.

![Top Level Info](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_7.png)

Special notes are tracked with symbols in the last column. These notes can be
added to tests or to the root student record. A few symbols are built in with
various suggested meanings including '!', '\*', '%', and '?'. Keeping track of
who has made unusual requests, has missed an evaluation, or has made a
complaint about a grade can be helpful as the course progresses.

For quizzes, or assessments that are completely evaluated in myCanvas it is
possible to import sets of grades. MyCanvas will export the entire grade sheet
for a course. Rgen can construct an "imported" rubric that simply shows final
score. Unfortunately myCanvas will not export individual question scores.

![Data Import](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_8.png)

Rgen will compute partial grades based on the work that has been done so far.
This same view will also show the details for any special notes that are
relevant to this student.

![Top Level Info](https://github.com/Dave-Gilbert/rgen/blob/main/images/RGEN_9.png)

## Anecdotal Conclusions

Prior to using this rubric generating tool I used a variety of different
grading strategies. 20 years ago when I was in graduate school the norm was to
sit down with a printed copy of a student's assignment and write on it with a
pen. I found this style of grading extremely difficult. I've only worked at the
college for a few years. During my first year at the college I relearned how to
use a spreadsheet, following the lead of senior staff who would often
communicate grading template in this format. MyCanvas, the learning management
system used by the college includes a static Rubric system, although these must
be set up in advance of student submissions, and don't seem very flexible to
me.

Rgen is fairly reliable. Each time a modification to either a rubric or a
student's grade is made Rgen will save the update to a .csv file on the disk.
It always makes a backup of any existing file prior to performing a write and
will generate an exception if anything goes wrong with the write leaving the
backup file in place. My personal file system is backed up regularly, backups
are essential when working with sensitive data.

I wrote the initial version of Rgen in a few weeks at the start of the summer
semester and have been using it to evaluate student homework and test
submissions since then. With each homework assignment that I grade I find a few
bugs or limitations. Generally I find that I grade and return things much
faster than I did in the past, and that the supplied comments are far more
detailed than I would normally be able to provide. Students have not complained
to me about their grades this term as much as in other courses. I'd like to
think that the consistency of the remarks and the detailed explanations
contribute to better and clearer learning outcomes, and generally happier
students.

I occasionally suffer from wrist strain. It is an occupational hazard in
computing. I've spent time to optimize the menus in rgen to minimize key
strokes. While its still necessary to type in comments the first time, I find
its much easier to navigate simple menus with cursor keys than it is to scroll
through spreadsheet cells, and switch back and forth between a mouse and keyboard.

## Bugs and Rough Edges

Some obvious features are missing. Initial setup requires the creation of a
special data directory. The .csv file downloaded from FastSuite must be copied
to a particular location, and the list of course assignments, and their
associated weights is assumed to be present. These details require
documentation and automation. There are a few ways that the code can generate
exceptions. Work is ongoing. If you have any questions you can reach me via
gmail at:

dave.wm.gilbert@gmail.com

