""" circalc.py -- simplistic LCR calculator for TPRG 2131 Week 2 Asmt 1

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

def getLemon(name):
    x = float(input("What is the inductance in "+name+"? "))
    while x <= 0.0:
        x = float(input("The value must be greater than zero\n"
                        "What is the inductance "+name+"? "))
    return x

def calcRF(l,c):
    rf = 1 / (2 * math.pi * math.sqrt(l * c))
    return rf

def calcQ(l,r,c):
    q = (1 / r) * math.sqrt(l / c)    
    return q

def calcBW(rf,q):
    bw = rf/q
    return bw

def convertMag(x,mod):
    y = x*10**(mod)
    return y
    

print("Series resonant circuit calculator\n(CTRL-C to quit)")

while True:
    
    lA = getLemon("mH")
    cA = getLemon("uF")
    rA = getLemon("ohms")
    
    lB = convertMag(lA,-3)
    cB = convertMag(cA,-6)
    
    rf = calcRF(lB,cB)
    q = calcQ(lB,rA,cB)
    bw = calcBW(rf,q)
    
    rf = Decimal(rf).quantize(Decimal('0.00'), rounding=ROUND_DOWN) 
    q = Decimal(q).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
    bw = Decimal(bw).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

    # Calculate the resonant frequency and the Q factor of this circuit
    # Formulas TBD
    print("lcr: ", lA, cA, rA, "\n")
    
    print("resonant frequency: "+str(rf)+" Hz\n")
    print("Q factor: "+str(q)+"\n")
    print("bandwidth: "+str(bw)+" Hz\n")
    
