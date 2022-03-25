
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import math
import random

# material
## UHDC
mdb.models['Model-1'].Material(name='UHDC')
mdb.models['Model-1'].materials['UHDC'].ConcreteDamagedPlasticity(table=((30.0, 0.1, 1.16, 0.667, 0.0005), ))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=((1.35, 0.0), (59.79805996, 0.002085257), (62.73015873, 0.002476661),
    (64.82451499, 0.002899092), (66.08112875, 0.003352551), (66.5,
    0.003837037), (64.80291971, 0.004399892), (63.10583942, 0.004962747), (
    46.1350365, 0.010591295), (35.95255474, 0.013968424), (20.0, 0.019259259),
    (20.0, 0.029259259)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=((2.5, 0.0), (5.05, 0.039812963), (4.915, 0.041817963), (4.78,
    0.043822963), (1.0, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=((0.0, 0.0), (0.282325629, 0.002085257), (0.304278071, 0.002476661),
    (0.326946137, 0.002899092), (0.35040474, 0.003352551), (0.374742851,
    0.003837037), (0.40589809, 0.004399892), (0.434162845, 0.004962747), (
    0.62728146, 0.010591295), (0.704989631, 0.013968424), (0.80754991,
    0.019259259), (0.84286516, 0.029259259)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=((0.0, 0.0), (0.931619258, 0.039812963), (0.934165243, 0.041817963),
    (0.936568391, 0.043822963), (0.980754991, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].Elastic(table=((27000.0, 0.2), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='UHDC', material='UHDC', thickness=None)
p = mdb.models['Model-1'].parts['Part-Base']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='UHDC', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)
