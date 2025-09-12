""" circalc.py -- simplistic LCR calculator for TPRG 2131 Week 2 Asmt 1

Assignment 1 for Tprg 2131 intro week 1-2


ADD YOUR NAME, STUDENT ID and SECTION CRN here.

This LCR calculator is ugly and incomplete. The code runs but doesn't actually
calculate anything. For full marks, you must complete the computation. You must
also "clean up" the code according to the course style guide and coding
standard. Specifically, you must:
  1) Take code that is duplicated and encapsulate it into a function that is
     called from the main program; the function must not "reach into" the
     main program for its working values;
  2) Rename variables so that they are not single letters, using descriptive
     names;
  3) Actually calculate the resonant frequency, bandwidth and Q factor for the
     SERIES resonant circuit (look up the formulas from ELEC II).

Keep working on the program. As you fix each problem, commit with an
informative commit message.
When done, commit with a message like "Ready for marking" and push the changes
to your assignment1 repository on the server hg.set.durhamcollege.org.
"""

print("Series resonant circuit calculator\n(CTRL-C to quit)")

while True:
    l = float(input("What is the inductance in mH? "))
    while l <= 0.0:
        l = float(input("The value must be greater than zero\n"
                        "What is the inductance in mH? "))

    c = float(input("What is the capacitance in uF? "))
    while c <= 0.0:
        c = float(input("The value must be greater than zero\n"
                        "What is the capacitance in uF? "))

    r = float(input("What is the resistance in ohms? "))
    while r <= 0.0:
        r = float(input("The value must be greater than zero\n"
                        "What is the resistance in ohms? "))

    # Calculate the resonant frequency and the Q factor of this circuit
    # Formulas TBD
    print("lcr:", l, c, r, "\n")
