""" circalc v2 by Thomas Heine.py -- simplistic LCR calculator for TPRG 2131 Week 2 Asmt 1

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


def getComp(unitNam):
    """prompt user for a component value and ensure it is greater than zero."""
    val = float(input(f"What is the {unitNam}? "))
    while val <= 0.0:
        val = float(input(f"The value must be greater than zero\n"
                          f"What is the {unitNam}? "))
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

"""-------"""


print("Series resonant circuit calculator\n(CTRL-C to quit)")


"""--- main control loop---"""

while True:
    
    indMh = getComp("inductance in mH")
    capUf = getComp("capacitance in uF")
    resOhm = getComp("resistance in ohms")

    # Convert to base SI units (Henry, Farad)
    indH = cnvUnt(indMh, -3)
    capF = cnvUnt(capUf, -6)

    resHz = resFrq(indH, capF)
    qFac = qFact(indH, resOhm, capF)
    bandHz = band(resHz, qFac)

    # Round results to two decimal places
    resHz = Decimal(resHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    qFac = Decimal(qFac).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    bandHz = Decimal(bandHz).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

    # Calculate the resonant frequency and the Q factor of this circuit
    # Formulas TBD
    
    print(f"Comp vals: L = {indMh} mH, C = {capUf} uF, R = {resOhm} Ω\n")

    print(f"Resonant freq: {resHz} Hz\n")
    print(f"Q factor: {qFac}\n")
    print(f"Bandwidth: {bandHz} Hz\n")
    
"""-------"""
