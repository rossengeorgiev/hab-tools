#!/usr/bin/env python
import math
import sys

# tiny burst model constants
a = 1.0132499806563689E+05
b = 1.2214130725079315E+00
c = 5.5141399703583615E+04
d = 3.4175843531167951E+00
f = 1.1471070689705153E+01

# tiny simple costants 
m = 3050.52626368589
n = 6385.42876800664

gndLevel = 80 # meters

def sphereVolumeFromDiameter(d):
	return (4.0/3)*math.pi*math.pow(d/2.0,3)

def heightFromPressure(p):
	try:
		return c*((a/p)**(1.0/f) - 1)**(1.0/b)
	except ValueError:
		return -c*math.fabs((a/p)**(1.0/f) - 1)**(1.0/b)

def pressureAtGnd():
	return d + (a - d) / (1 + (gndLevel / c)**b)**f

def calcBurstPoint(i,v):
	return heightFromPressure((pressureAtGnd() * i) / v)

def calcBurstPointIdeal(i,v):
	pressure = ((pressureAtGnd()*i)/288.15) / (v/233.0)
	return heightFromPressure(pressure)

def calcBurstSimple(i,v):
	return m+n*math.log(v/i);

if(len(sys.argv) < 3):
	print "To run: python %s <diameter> <fill volume> [ground level]" % sys.argv[0]
	sys.exit();

if(len(sys.argv) >= 4):
	gndLevel = float(sys.argv[3])
	print "Pressure: %.2f (%.0f)" % (pressureAtGnd(), gndLevel)

dia = float(sys.argv[1])
v = sphereVolumeFromDiameter(dia)
x = float(sys.argv[2]);

print "Diameter: %.2f (%.2f m^3)"						% (dia, v)
print "Fill: %.2fm^3 @ %.0fm (Vd/f %.2f)"		% (x, gndLevel, v/x)
print "Gross lift (H): %.0fg"								% ((1.205-0.0899) * x * 1000)
print "Gross lift (He): %.0fg"							% ((1.205-0.1786) * x * 1000)
print "Burst altitude (Tconst): %.0fm"			% calcBurstPoint(x,v)
print "Burst altitude (US std): %.0fm"			% calcBurstPointIdeal(x,v)
print "Burst altitude (simplified): %.0fm" 	% calcBurstSimple(x,v)

if(len(sys.argv) == 5):
	print "Alt: %.0fm(%.2fpa)" % (heightFromPressure(float(sys.argv[4])), float(sys.argv[4]))

