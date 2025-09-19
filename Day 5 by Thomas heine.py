""" day 5 by Thomas Heine.py -- simplistic LCR calculator for TPRG 2131 Week 2 Asmt 1

Assignment 1 for Tprg 2131 intro week 1-2


ADD YOUR NAME, STUDENT ID and SECTION CRN here.

name: Thomas Heing
sdutent ID: 100777741
section CRN: TPRG 2131

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

import math
from decimal import Decimal, ROUND_DOWN

""" "quit" changed to "q" on day 4"""

def menuHint():
    print("(type 'menu' to return or 'q' to quit)")   


def getComp(unitNam):
    """prompt user for a component value and ensure it is greater than zero."""
    menuHint()
    val = input(f"what is the {unitNam}? ")
    if val.strip().lower() in ["menu", "q"]:
        return val.strip().lower()
    val = float(val)
    while val <= 0.0:
        menuHint()
        val = input(f"the value must be greater than zero\n"
                    f"what is the {unitNam}? ")
        if val.strip().lower() in ["menu", "q"]:
            return val.strip().lower()
        val = float(val)
    return val


"""--- calculating methods ---"""

def resFrq(indH, capF):
    return 1 / (2 * math.pi * math.sqrt(indH * capF))


def qFact(indH, resOhm, capF):
    return (1 / resOhm) * math.sqrt(indH / capF)


def band(resHz, qFac):
    return resHz / qFac


def cnvUnt(val, expn):
    """convert metric-prefixed units to base units using powers of 10."""
    return val * 10 ** expn


def resSeries(r1, r2):
    """calculate total resistance of two resistors in series."""
    return r1 + r2


def resParallel(r1, r2):
    """calculate total resistance of two resistors in parallel."""
    return (r1 * r2) / (r1 + r2)


def rcTimeConst(r, c):
    """calculate RC time constant tau = R * C."""
    return r * c

"""-------"""


def menu():
    print("\nMain Menu (q to quit)")
    print("1: series resonant circuit calculator")
    print("2: two resistors in series")
    print("3: two resistors in parallel")
    print("4: RC time constant")
    print("5: resonant frequency of series RLC\n")


# one time start up message
print("Multi-mode circuit calculator\n(q to quit)\n")

# tells the user which version they have
def versionYell(times, day):
    count = 0
    while count < times:
        print("This is the day "+str(day)+" version!")
        count += 1

versionYell(3, 5)


"""--- main loop ---"""

while True:
    menu()
    menuHint()
    choice = input("Select a mode: ").strip().lower()
    if choice == "q":
        break
    
    if choice == "1":
        while True:
            indMh = getComp("inductance in mH")
            if indMh in ["menu", "q"]:
                if indMh == "q": quit()
                break
            capUf = getComp("capacitance in uF")
            if capUf in ["menu", "q"]:
                if capUf == "q": quit()
                break
            resOhm = getComp("resistance in ohms")
            if resOhm in ["menu", "q"]:
                if resOhm == "q": quit()
                break

            indH = cnvUnt(indMh, -3)
            capF = cnvUnt(capUf, -6)

            resHz = resFrq(indH, capF)
            qFac = qFact(indH, resOhm, capF)
            bandHz = band(resHz, qFac)

            resHz = Decimal(resHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            qFac = Decimal(qFac).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            bandHz = Decimal(bandHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            menuHint()
            print(f"LCR component values: L = {indMh} mH, C = {capUf} uF, R = {resOhm} Ω\n")
            menuHint()
            print(f"resonant freq: {resHz} Hz\n")
            menuHint()
            print(f"Q factor: {qFac}\n")
            menuHint()
            print(f"bandwidth: {bandHz} Hz\n")

    elif choice == "2":
        while True:
            r1 = getComp("first resistor in ohms")
            if r1 in ["menu", "q"]:
                if r1 == "q": quit()
                break
            r2 = getComp("second resistor in ohms")
            if r2 in ["menu", "q"]:
                if r2 == "q": quit()
                break

            total = resSeries(r1, r2)
            total = Decimal(total).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            menuHint()
            print(f"series resistance: {total} Ω\n")

    elif choice == "3":
        while True:
            r1 = getComp("first resistor in ohms")
            if r1 in ["menu", "q"]:
                if r1 == "q": quit()
                break
            r2 = getComp("second resistor in ohms")
            if r2 in ["menu", "q"]:
                if r2 == "q": quit()
                break

            total = resParallel(r1, r2)
            total = Decimal(total).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            menuHint()
            print(f"parallel resistance: {total} Ω\n")

    elif choice == "4":
        while True:
            r = getComp("resistor in ohms")
            if r in ["menu", "q"]:
                if r == "q": quit()
                break
            cUf = getComp("capacitance in uF")
            if cUf in ["menu", "q"]:
                if cUf == "q": quit()
                break

            cF = cnvUnt(cUf, -6)
            tau = rcTimeConst(r, cF)
            tau = Decimal(tau).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            menuHint()
            print(f"RC time constant: {tau} seconds\n")

    elif choice == "5":
        while True:
            indMh = getComp("inductance in mH")
            if indMh in ["menu", "q"]:
                if indMh == "q": quit()
                break
            capUf = getComp("capacitance in uF")
            if capUf in ["menu", "q"]:
                if capUf == "q": quit()
                break
            resOhm = getComp("resistance in ohms")
            if resOhm in ["menu", "q"]:
                if resOhm == "q": quit()
                break

            indH = cnvUnt(indMh, -3)
            capF = cnvUnt(capUf, -6)

            resHz = resFrq(indH, capF)
            qFac = qFact(indH, resOhm, capF)
            bandHz = band(resHz, qFac)

            resHz = Decimal(resHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            qFac = Decimal(qFac).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            bandHz = Decimal(bandHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            
            print(f"\nRLC component values: L = {indMh} mH, C = {capUf} uF, R = {resOhm} Ω\n")
            
            print(f"resonant freq: {resHz} Hz\n")
            
            print(f"Q factor: {qFac}\n")
            
            print(f"bandwidth: {bandHz} Hz\n")

    else:
        menuHint()
        print("invalid choice, please select 1, 2, 3, 4, 5.\n")

"""-------"""
