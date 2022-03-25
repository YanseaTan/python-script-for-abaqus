
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import math
import random

# input attribute
diameter = 10
dopingRate = 0.2

# create base
myModel = mdb.models["Model-1"]
mysketch_1 = myModel.ConstrainedSketch(name='mysketch_1', sheetSize=200.0)
mysketch_1.rectangle(point1=(0.0, 0.0), point2=(100.0, 100.0))
myPart = myModel.Part(name='Part-Base', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mysketch_1, depth=300.0)
del mysketch_1

# assembly base
myAssembly = myModel.rootAssembly
myAssembly.Instance(name='Part-Base', part = myModel.parts["Part-Base"], dependent=ON)

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

# step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', maxNumInc=10000, initialInc=0.01, maxInc=0.01)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'PE', 'PEEQ', 'PEMAG', 'LE', 'U',
'RF', 'CF', 'CSTRESS', 'CDISP', 'DAMAGEC', 'DAMAGET'))

# boundary conditions
myAssembly.ReferencePoint(point=(50.0, 50.0, 325.0))
r1 = myAssembly.referencePoints
refPoints1=(r1[3], )
region1=regionToolset.Region(referencePoints=refPoints1)
s1 = myAssembly.instances['Part-Base'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#10 ]', ), )
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Coupling(name='Constraint-1', controlPoint=region1, surface=region2, influenceRadius=WHOLE_SURFACE,
couplingType=KINEMATIC, localCsys=None, u1=OFF, u2=OFF, u3=ON, ur1=ON, ur2=ON, ur3=ON)
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET,
ur1=SET, ur2=SET, ur3=SET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# load
mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP, smooth=SOLVER_DEFAULT,
data=((0.0, 0.0), (0.1, 0.5), (0.2, 6.0), (0.3, 12.0), (0.4, 18.0), (0.5, 18.0), (0.6, 12.0), (0.7, 6.0),
(0.8, 0.5), (0.9, 0.5), (1.0, 0.0)))
s1 = myAssembly.instances['Part-Base'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#20 ]', ), )
region = regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Pressure(name='Load-1', createStepName='Step-1', region=region, distributionType=UNIFORM,
field='', magnitude=1.0, amplitude='Amp-1')

# mesh
## base
p = mdb.models['Model-1'].parts['Part-Base']
p.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()

# job
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=4,
numDomains=4, numGPUs=1)

