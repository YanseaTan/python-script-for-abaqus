
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import math
import random
import job

# input parameters
diameter = 10
dopingRate = 0.2
stepTime = 0.05

# parts
## base
myModel = mdb.models["Model-1"]
mysketch_1 = myModel.ConstrainedSketch(name='mysketch_1', sheetSize=200.0)
mysketch_1.rectangle(point1=(0.0, 0.0), point2=(50.0, 50.0))
myPart = myModel.Part(name='Part-Base', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mysketch_1, depth=100.0)
del mysketch_1

## aggregate
partName = "Part-Ball-{}".format(diameter)
mysketch_2 = myModel.ConstrainedSketch(name='mysketch_2', sheetSize=200.0)
mysketch_2.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
mysketch_2.ArcByCenterEnds(center=(0.0, 0.0), point1=(0.0, 5.0), point2=(5.0, 0.0), 
    direction=CLOCKWISE)
mysketch_2.Line(point1=(0.0, diameter/2.0), point2=(0.0, 0.0))
mysketch_2.Line(point1=(0.0, 0.0), point2=(diameter/2.0, 0.0))
myPart2 = myModel.Part(name=partName, dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart2.BaseSolidRevolve(sketch=mysketch_2, angle=90.0, flipRevolveDirection=OFF)
del mysketch_2
p = mdb.models['Model-1'].parts["Part-Ball-{}".format(diameter)]
f = p.faces
p.Mirror(mirrorPlane=f[3], keepOriginal=ON, keepInternalBoundaries=ON)
f1 = p.faces
p.Mirror(mirrorPlane=f1[2], keepOriginal=ON, keepInternalBoundaries=ON)
f = p.faces
p.Mirror(mirrorPlane=f[9], keepOriginal=ON, keepInternalBoundaries=ON)

# interCheck function
def interCheck(point,center,radius1,radius2):
    sign = True
    for p in center:
        if sqrt((point[0]-p[0])**2+(point[1]-p[1])**2+(point[2]-p[2])**2) <= (radius1+radius2+1):
            sign = False
            break
    return sign

# calculate aggregate coordinates
count = 0
center10 = []
radius = 5
while True:
    disX = random.uniform(radius+1, 50-radius-1)
    disY = random.uniform(radius+1, 50-radius-1)
    disZ = random.uniform(radius+1, 100-radius-1)
    if len(center10)==0:
        center10.append([disX,disY,disZ])
    else:
        if interCheck([disX,disY,disZ],center10,5,5):
            center10.append([disX,disY,disZ])
            count += 1
    if count >= 50*50*100*dopingRate/4*3/math.pi/radius/radius/radius:
        break

# assemble parts
## base
myAssembly = myModel.rootAssembly
myAssembly.Instance(name='Part-Base', part = myModel.parts["Part-Base"], dependent=ON)

## aggregate
instances1 = []
for index in range(len(center10)):
    myAssembly.Instance(name='Part-Ball-10-{}'.format(index), part=myModel.parts["Part-Ball-10"], dependent=ON)
    myAssembly.translate(instanceList=('Part-Ball-10-{}'.format(index),), vector=tuple(center10[index]))
    instances1.append(myAssembly.instances['Part-Ball-10-{}'.format(index)])

session.viewports['Viewport: 1'].assemblyDisplay.geometryOptions.setValues(datumAxes=OFF)

a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanCut(name='Part-CutBase', 
    instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-Base'], 
    cuttingInstances=instances1, originalInstances=DELETE)

cells1, instances2 = [], [myAssembly.instances['Part-CutBase-1'], ]
for index in range(len(center10)):
    myAssembly.Instance(name='Part-Ball-10-{}'.format(index), part=myModel.parts["Part-Ball-10"], dependent=ON)
    myAssembly.translate(instanceList=('Part-Ball-10-{}'.format(index),), vector=tuple(center10[index]))
    cells1.append(myAssembly.instances['Part-Ball-10-{}'.format(index)].cells[0:8])
    instances2.append(myAssembly.instances['Part-Ball-10-{}'.format(index)])

myAssembly.Set(cells=cells1, name='aggregate')
myAssembly.Set(cells=myAssembly.instances['Part-CutBase-1'].cells[0:1], name='base')

# materials
## UHDC
mdb.models['Model-1'].Material(name='UHDC')
mdb.models['Model-1'].materials['UHDC'].ConcreteDamagedPlasticity(table=((30.0, 0.1, 1.16, 0.667, 0.0005), ))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=((1.35, 0.0), (45.12280675, 0.002628785), (47.3353288, 0.00304684), (
    48.91570169, 0.003488307), (49.86392542, 0.003953188), (50.18, 
    0.004441481), (48.89605839, 0.004989035), (47.61211679, 0.005536588), (
    34.77270073, 0.011012122), (27.06905109, 0.014297443), (15.0, 0.019444444), 
    (15.0, 0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=((3.3, 0.0), (5.05, 0.049812963), (4.888, 0.051818963), (4.726,
    0.053824963), (1.0, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=((0.0, 0.0), (0.37657826, 0.002628785), (0.395647673, 0.00304684), (
    0.415338728, 0.003488307), (0.435716498, 0.003953188), (0.456858269, 
    0.004441481), (0.483939538, 0.004989035), (0.508509155, 0.005536588), (
    0.676417688, 0.011012122), (0.7440183, 0.014297443), (0.833333333, 
    0.019444444), (0.863917237, 0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=((0.0, 0.0), (0.938838405, 0.049812963), (0.94099592, 0.051818963),
    (0.943066472, 0.053824963), (0.980754991, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].Elastic(table=((27000.0, 0.2), ))
mdb.models['Model-1'].materials['UHDC'].Density(table=((2.5e-09, ), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='UHDC', material='UHDC', thickness=None)
p = mdb.models['Model-1'].parts['Part-CutBase']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='UHDC', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)

## aggregate
mdb.models['Model-1'].Material(name='aggregate')
mdb.models['Model-1'].materials['aggregate'].Elastic(table=((1500.0, 0.4), ))
mdb.models['Model-1'].materials['aggregate'].Density(table=((9e-10, ), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='aggregate', material='aggregate', thickness=None)
p = mdb.models['Model-1'].parts['Part-Ball-10']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#ff ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='aggregate', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)

# step
myAssembly.ReferencePoint(point=(25.0, 25.0, 100.0))
myAssembly.ReferencePoint(point=(25.0, 25.0, 0.0))
r1 = myAssembly.referencePoints
refPoints1=(r1[395], )
myAssembly.Set(referencePoints=refPoints1, name='rf1')
r2 = myAssembly.referencePoints
refPoints2=(r2[396], )
myAssembly.Set(referencePoints=refPoints2, name='rf2')
mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial', 
    timePeriod=stepTime, massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 5.0, 
    1e-05, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None), ), improvedDtMethod=ON)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'PE','RF','DAMAGEC', 'DAMAGET', 'STATUS'))
del mdb.models['Model-1'].historyOutputRequests['H-Output-1']
regionDef=mdb.models['Model-1'].rootAssembly.sets['rf1']
mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-1', 
    createStepName='Step-1', variables=('RF3', ), region=regionDef, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)
regionDef=mdb.models['Model-1'].rootAssembly.sets['rf2']
mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2', 
    createStepName='Step-1', variables=('U3', ), region=regionDef, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)

# contact
mdb.models['Model-1'].ContactProperty('IntProp-1')
mdb.models['Model-1'].interactionProperties['IntProp-1'].TangentialBehavior(
    formulation=FRICTIONLESS)
mdb.models['Model-1'].interactionProperties['IntProp-1'].NormalBehavior(
    pressureOverclosure=HARD, allowSeparation=ON, 
    constraintEnforcementMethod=DEFAULT)
mdb.models['Model-1'].ContactExp(name='Int-1', createStepName='Initial')
mdb.models['Model-1'].interactions['Int-1'].includedPairs.setValuesInStep(
    stepName='Initial', useAllstar=ON)
mdb.models['Model-1'].interactions['Int-1'].contactPropertyAssignments.appendInStep(
    stepName='Initial', assignments=((GLOBAL, SELF, 'IntProp-1'), ))

# boundary conditions
region1=regionToolset.Region(referencePoints=refPoints1)
s1 = myAssembly.instances['Part-CutBase-1'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#10 ]', ), )
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Coupling(name='Constraint-1', controlPoint=region1, 
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=OFF, u2=OFF, u3=ON, ur1=ON, ur2=ON, ur3=ON)
region3=regionToolset.Region(referencePoints=refPoints2)
s2 = myAssembly.instances['Part-CutBase-1'].faces
side1Faces2 = s2.getSequenceFromMask(mask=('[#20 ]', ), )
region4=regionToolset.Region(side1Faces=side1Faces2)
mdb.models['Model-1'].Coupling(name='Constraint-2', controlPoint=region3, 
    surface=region4, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=OFF, u2=OFF, u3=ON, ur1=ON, ur2=ON, ur3=ON)
mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Initial', 
    region=region1, localCsys=None)


# load
mdb.models['Model-1'].SmoothStepAmplitude(name='Amp-1', timeSpan=STEP, data=((
    0.0, 0.0), (stepTime, 1.0)))
region = myAssembly.sets['rf2']
mdb.models['Model-1'].DisplacementBC(name='load', createStepName='Step-1', 
    region=region, u1=0.0, u2=0.0, u3=-10.0, ur1=0.0, ur2=0.0, ur3=0.0, 
    amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

# merge parts
myAssembly.InstanceFromBooleanMerge(name='Part-CAUHDC', instances=instances2, 
    keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)

# mesh
p = mdb.models['Model-1'].parts['Part-CAUHDC']
p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
c = p.cells
pickedRegions = c[776:777]
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE, allowMapped=False)
elemType1 = mesh.ElemType(elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT)
elemType2 = mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT)
elemType3 = mesh.ElemType(elemCode=C3D10M, elemLibrary=EXPLICIT)
cells = c[776:777]
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
p.generateMesh()

# job
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, 
    nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
    contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
    resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=6, 
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=6)

# keyword
# *CONCRETE FAILURE
# 0,0,0,0.86