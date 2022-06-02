
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset
import math
import random
import job

session.journalOptions.setValues(replayGeometry=INDEX,recoverGeometry=INDEX)

# input parameters
stepTime = 0.05

# parts
## base
myModel = mdb.models["Model-1"]
mysketch_1 = myModel.ConstrainedSketch(name='mysketch_1', sheetSize=200.0)
mysketch_1.rectangle(point1=(0.0, 0.0), point2=(100.0, 100.0))
myPart = myModel.Part(name='Part-Base', dimensionality=THREE_D, type=DEFORMABLE_BODY)
myPart.BaseSolidExtrude(sketch=mysketch_1, depth=100.0)
del mysketch_1

# materials
## UHDC
mdb.models['Model-1'].Material(name='UHDC')
mdb.models['Model-1'].materials['UHDC'].ConcreteDamagedPlasticity(table=((30.0, 0.1, 1.16, 0.667, 0.0005), ))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionHardening(
    table=((1.35, 0.0), (50.35626102, 0.002434953), (52.82539683, 0.002843504), 
    (54.58906526, 0.003278183), (55.64726631, 0.00373899), (56.0, 0.004225926), 
    (54.50364964, 0.004781346), (53.00729927, 0.005336767), (38.04379562, 
    0.010890971), (29.06569343, 0.014223493), (15.0, 0.019444444), (15.0, 
    0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionStiffening(
    table=((3.3, 0.0), (5.05, 0.049812963), (4.888, 0.051818963), (4.726,
    0.053824963), (1.0, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteCompressionDamage(
    table=((0.0, 0.0), (0.34141683, 0.002434953), (0.361561772, 0.002843504), (
    0.382363416, 0.003278183), (0.403890507, 0.00373899), (0.426224689, 
    0.004225926), (0.455150629, 0.004781346), (0.481409536, 0.005336767), (
    0.661539897, 0.010890971), (0.734745508, 0.014223493), (0.833333333, 
    0.019444444), (0.863917237, 0.029444444)))
mdb.models['Model-1'].materials['UHDC'].concreteDamagedPlasticity.ConcreteTensionDamage(
    table=((0.0, 0.0), (0.938838405, 0.049812963), (0.94099592, 0.051818963),
    (0.943066472, 0.053824963), (0.980754991, 0.099962963)))
mdb.models['Model-1'].materials['UHDC'].Elastic(table=((27000.0, 0.2), ))
mdb.models['Model-1'].materials['UHDC'].Density(table=((2.5e-09, ), ))
mdb.models['Model-1'].HomogeneousSolidSection(name='UHDC', material='UHDC', thickness=None)
p = mdb.models['Model-1'].parts['Part-Base']
c = p.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='UHDC', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='',
thicknessAssignment=FROM_SECTION)

# assemble parts
## base
myAssembly = myModel.rootAssembly
myAssembly.Instance(name='Part-Base', part = myModel.parts["Part-Base"], dependent=ON)

# step
myAssembly.ReferencePoint(point=(50.0, 0.0, 50.0))
myAssembly.ReferencePoint(point=(50.0, 100.0, 50.0))
r1 = myAssembly.referencePoints
refPoints1=(r1[3], )
myAssembly.Set(referencePoints=refPoints1, name='rf1')
r2 = myAssembly.referencePoints
refPoints2=(r2[4], )
myAssembly.Set(referencePoints=refPoints2, name='rf2')
mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial', 
    timePeriod=stepTime, massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING, 5.0, 
    1e-05, BELOW_MIN, 0, 0, 0.0, 0.0, 0, None), ), improvedDtMethod=ON)
mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables= 
('S', 'U', 'PE','RF','DAMAGEC', 'DAMAGET', 'STATUS'), numIntervals=40)
del mdb.models['Model-1'].historyOutputRequests['H-Output-1']
regionDef=mdb.models['Model-1'].rootAssembly.sets['rf1']
mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-1', 
    createStepName='Step-1', variables=('RF2', ), region=regionDef, 
    sectionPoints=DEFAULT, rebar=EXCLUDE)
regionDef=mdb.models['Model-1'].rootAssembly.sets['rf2']
mdb.models['Model-1'].HistoryOutputRequest(name='H-Output-2', 
    createStepName='Step-1', variables=('U2', ), region=regionDef, 
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
s1 = myAssembly.instances['Part-Base'].faces
side1Faces1 = s1[3:4]
region2=regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Coupling(name='Constraint-1', controlPoint=region1, 
    surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=OFF, ur2=OFF, ur3=OFF)
region3=regionToolset.Region(referencePoints=refPoints2)
s2 = myAssembly.instances['Part-Base'].faces
side1Faces2 = s2[1:2]
region4=regionToolset.Region(side1Faces=side1Faces2)
mdb.models['Model-1'].Coupling(name='Constraint-2', controlPoint=region3, 
    surface=region4, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
    localCsys=None, u1=ON, u2=ON, u3=ON, ur1=OFF, ur2=OFF, ur3=OFF)
mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Initial', 
    region=region1, localCsys=None)


# load
mdb.models['Model-1'].SmoothStepAmplitude(name='Amp-1', timeSpan=STEP, data=((
    0.0, 0.0), (stepTime, 1.0)))
region = myAssembly.sets['rf2']
mdb.models['Model-1'].DisplacementBC(name='load', createStepName='Step-1', 
    region=region, u1=0.0, u2=-2.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0, 
    amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='', 
    localCsys=None)

# keyword
mdb.models['Model-1'].keywordBlock.synchVersions(storeNodesAndElements=False)
mdb.models['Model-1'].keywordBlock.insert(32, """
*CONCRETE FAILURE
0,0,0,0.8639""")

# mesh
p = mdb.models['Model-1'].parts['Part-Base']
p.seedPart(size=2.0, deviationFactor=0.1, minSizeFactor=0.1)
c = p.cells
pickedRegions = c[0:1]
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE, allowMapped=False)
elemType1 = mesh.ElemType(elemCode=UNKNOWN_HEX, elemLibrary=EXPLICIT)
elemType2 = mesh.ElemType(elemCode=UNKNOWN_WEDGE, elemLibrary=EXPLICIT)
elemType3 = mesh.ElemType(elemCode=C3D10M, elemLibrary=EXPLICIT)
cells = c[0:1]
pickedRegions =(cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
    elemType3))
p.generateMesh()

# job
mdb.Job(name='0c', model='Model-1', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, explicitPrecision=SINGLE, 
    nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
    contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
    resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=6, 
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=6)
