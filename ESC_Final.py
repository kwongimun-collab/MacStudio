#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
# It is coded For Raza's request (Without Shortest Path)
#----------------------------------------------------------------------------
#   Objective: Minimizing the energy gap for 50 years in Pakistan.
#----------------------------------------------------------------------------
#    UNITS:
#    money: $ thousnad
#    coal: ton
#    time: hour
#    power: MWh
#    distance: 100 miles
#----------------------------------------------------------------------------

# Call Library
#import sys
import os
import xlrd

#sys.path.append('C:/gurobi550/win64/python27/lib/gurobipy')

from gurobipy import *

#   Modeling start
try:

    #   Create a model
    model = Model("Coal_Based Energy Supply Chain")


######################################
#   open InputData
######################################
    from xlrd import open_workbook

    inputdata = open_workbook(
        os.path.join(os.path.dirname(__file__), 'InputData_Thousand.xls'))
    player = inputdata.sheet_by_name("Index")
    reserve = inputdata.sheet_by_name("CR_j")
    RoundTrip = inputdata.sheet_by_name("RT_jk")
    capacity = inputdata.sheet_by_name("F_jk")
    SC_railway = inputdata.sheet_by_name("SC_RW_jk")
    shortage = inputdata.sheet_by_name("G_nt")
    impact = inputdata.sheet_by_name("Beta_t")
    DIST1 = inputdata.sheet_by_name("D_jk")
    DIST2 = inputdata.sheet_by_name("D_kn")
    RATION = inputdata.sheet_by_name("RA_t")
    SC_tl = inputdata.sheet_by_name("SC_TL_k")

#######################################
#   Definition of Index
#######################################
    SOURCE = int(player.cell_value(rowx=1, colx=1))
    PP = int(player.cell_value(rowx=1, colx=2))
    DEMANDZONE = int(player.cell_value(rowx=1, colx=3))
    YEARS = int(player.cell_value(rowx=1, colx=4))
    percentage = int(player.cell_value(rowx=1, colx=5))
    GDP_Indicator = int(player.cell_value(rowx=1, colx=6))
#    print SOURCE
#    print PP
#    print DEMANDZONE
#    print YEARS
#######################################
#   Definition of Variables
#######################################
#type of variables: GRB.CONTINUOUS, GRB.BINARY, GRB.INTEGER
#addVar ( lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name='''', column=None ) 
################ Decision Variables ######################
#w[j][t]: If A Mine Of Location j Is Entering Service (Setup) In Year t, Then 1. Otherwise 0.
#A Decision Variable to setup a mine
#A Binary Variable
    w = []
    for j in range(SOURCE):
        w.append([])
        for t in range(YEARS):
            w[j].append(model.addVar(vtype=GRB.BINARY, name="w_%s,%s" % (j,t)))
      
#q[j][k][t]: The Quantity Of Coal Shipped From A Source j To A PP Location k In Year t.
#A Continuous Variable.
    q = []
    for j in range(SOURCE):
        q.append([])
        for k in range(PP):
            q[j].append([])
            for t in range(YEARS):
                q[j][k].append(model.addVar(vtype=GRB.CONTINUOUS, name="q_%s,%s,%s" % (j,k,t)))
    
#y[k][t]: The # Of Power Plants Newly Entering Service At A PP Location In Year t.
#An Integer Variable.
    y = []
    for k in range(PP):
        y.append([])
        for t in range(YEARS):
            y[k].append(model.addVar(vtype=GRB.INTEGER, name="y_%s,%s" % (k,t)))

#p[k][n][t]: The Total Amount Of Electricity Supplied From A PP Location k
#To A Demand Zone n In Year t.
#A Continuous Variable.
    p = []
    for k in range(PP):
        p.append([])
        for n in range(DEMANDZONE):
            p[k].append([])
            for t in range(YEARS):
                p[k][n].append(model.addVar(vtype=GRB.CONTINUOUS, name="p_%s,%s,%s" % (k,n,t)))

################ Other Variables ######################            
#b_CM[t]: The Budget For Setup Sources In Year t.
#A Continuous Variable
    b_CM1 = {}
    for t in range(YEARS):
        b_CM1[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_CM1_%s' % (t))
    b_CM2 = {}
    for t in range(YEARS):
        b_CM2[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_CM2_%s' % (t))
    b_CM3 = {}
    for t in range(YEARS):
        b_CM3[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_CM3_%s' % (t))
    b_CM4 = {}
    for t in range(YEARS):
        b_CM4[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_CM4_%s' % (t))

#x[j][k][t]: If A Railway Between A Source j And A PP Location k Is Entering Service In Year t,
#Then 1. Otherwise 0.
#A Decision Variable.
#A Binary Variable.
    x = []
    for j in range(SOURCE):
        x.append([])
        for k in range(PP):
            x[j].append([])
            for t in range(YEARS):
                x[j][k].append(model.addVar(vtype=GRB.BINARY, name="x_%s,%s,%s" % (j,k,t)))
#b_RW[t]: The Budget For Railway System In Year t.
#A Continuous Variable
    b_RW1 = {}
    for t in range(YEARS):
        b_RW1[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_RW1_%s' % (t))
    b_RW2 = {}
    for t in range(YEARS):
        b_RW2[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_RW2_%s' % (t))       
#b_TR[t]: The Budget For Purchasing Trains In Year t.
#A Continuous Variable   
    b_TR = {}
    for t in range(YEARS):
        b_TR[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_TR_%s' % (t))
#nt[j][k][t]: The # Of Trains Newly Purchased In Year t.
#An Integer Variable
    nt = []
    for j in range(SOURCE):
        nt.append([])
        for k in range(PP):
            nt[j].append([])
            for t in range(YEARS):
                nt[j][k].append(model.addVar(lb=0.0, vtype=GRB.INTEGER, name="nt_%s,%s,%s" % (j,k,t)))   
#e[k][t]: The Total Amount Of Electricity Generated At A PP Location In Year t.
#A Continuous Variable
    e = []
    for k in range(PP):
        e.append([])
        for t in range(YEARS):
            e[k].append(model.addVar(vtype=GRB.CONTINUOUS, name="e_%s%s" % (k,t)))
#b_PP[t]: The Budget For PPs In Year t.
#A Continuous Variable     
    b_PP1 = {}
    for t in range(YEARS):
        b_PP1[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_PP1_%s' % (t))
    b_PP2 = {}
    for t in range(YEARS):
        b_PP2[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_PP2_%s' % (t))    
#g[t]: GDP In Year t
    g = {}
    for t in range(YEARS):
        g[t] = model.addVar(vtype=GRB.CONTINUOUS, name='g_%s' % (t))
###############FOR TEST: START ######################
#total_cost[t]: Yearly investment
    total_cost = {}
    for t in range(YEARS):
        total_cost[t] = model.addVar(vtype=GRB.CONTINUOUS, name='total_cost_%s' % (t))
#yearly_gap[t]
    yearly_gap = {}
    for t in range(YEARS):
        yearly_gap[t] = model.addVar(vtype=GRB.CONTINUOUS, name='yearly_gap_%s' % (t)) 
###############FOR TEST: END ######################

###############FOR TEST: END ######################
    #   Update model to integrate new variables
    model.update()

    #   Minimizing Objective Value
    model.modelSense = GRB.MINIMIZE


#######################################
#   Parameter Setting
#######################################
#   1. CR[j]: Coal Reserves at source 'j'
#######################################
#   Parameter Setting
#######################################
#CR[j]: Coal Reserves at source 'j'
    CR = reserve.row_values(1)
#    for j in range(SOURCE):
#        print "CR_[",j,"]=", CR[j]
#RT[j][k]: Roundtrip Time between 'j' and 'k'
    RT = []
    for j in range(SOURCE):
        RT.append([])
        for k in range(PP):
            RT[j].append(RoundTrip.cell_value(rowx=j+1,colx=k+1))
#            print "RT_[",j,",",k,"]=", RT[j][k]
#F[j][k]: The Capacity of a train operated between 'j' and 'k'
    F = []
    for j in range(SOURCE):
        F.append([])
        for k in range(PP):
            F[j].append(capacity.cell_value(rowx=j+1,colx=k+1))
#            print "F[",j,",",k,"]=", F[j][k]
#SC_RW[j][k]: The Setup Cost to setup railway between 'j' and 'k'
    SC_RW = []
    for j in range(SOURCE):
        SC_RW.append([])
        for k in range(PP):
            SC_RW[j].append(SC_railway.cell_value(rowx=j+1,colx=k+1))
#            print "SC_RW[",j,",",k,"]=", SC_RW[j][k]
#G[n][t]: The Energy Gap betweeb power supplied from 'k' and power demanded to 'n'
    GAP = []
    for n in range(DEMANDZONE):
        GAP.append([])
        for t in range(YEARS):
            GAP[n].append(shortage.cell_value(rowx=n+1,colx=t+1))
#            print "GAP[",n,",",t,"]=", GAP[n][t]
#RA[t]: Ration in year t
    RA = RATION.row_values(1)
#    for t in range(YEARS):
#        print "RA[",t,"]=", RA[t]
#BETA[t]: Beta_t
    BETA = impact.row_values(1)
#    for t in range(YEARS):
#        print "BETA[",t,"]=", BETA[t]
#DISTANCE1[j][k]: Distance between 'j' and 'k'
    DISTANCE1 = []
    for j in range(SOURCE):
        DISTANCE1.append([])
        for k in range(PP):
            DISTANCE1[j].append(DIST1.cell_value(rowx=j+1,colx=k+1))
#            print "DISTANCE1[",j,",",k,"]=", DISTANCE1[j][k]
#DISTANCE2[k][n]: Distance between 'j' and 'k'
    DISTANCE2 = []
    for k in range(PP):
        DISTANCE2.append([])
        for n in range(DEMANDZONE):
            DISTANCE2[k].append(DIST2.cell_value(rowx=k+1,colx=n+1))
#            print "DISTANCE2[",k,",",n,"]=", DISTANCE2[k][n]
#SC_TL[K]: Setup cost for transmission line and grid station at k
    SC_TL = SC_tl.row_values(1)
#    for k in range(PP):
#        print "SC_TL[",k,"]=", SC_TL[k]
#Other Parameters: a bigM, E_s, and LT&UT
    bigM = 200000000000.0
    

############################################################################
#### Adding Constraints
#NOTE:
############################################################################
#Initial Condition 1
    for j in range(0,1):
        for t in range(0,5):
            model.addConstr(w[j][t] == 0.0)
    for j in range(1,2):
        for t in range(0,3):
            model.addConstr(w[j][t] == 0.0)
    for j in range(2,SOURCE):
        for t in range(0,3):
            model.addConstr(w[j][t] == 0.0)
#Source Balance Constraint
    for j in range(0,SOURCE):
        for t in range(0,YEARS):
            model.addConstr(quicksum(quicksum(q[j][k][tau] for tau in range(0,t+1)) for k in range(0,PP)) <= CR[j]*quicksum(w[j][tau] for tau in range(0,t+1)))
#Souce (Mine) Availability Constraints
#quicksum(w[j][t] for t in range(0,YEARS)) <= 1    for all j
    for j in range(0,SOURCE):
        model.addConstr(quicksum(w[j][t] for t in range(0,YEARS)) <= 1.0)
#   Source Budget and Operating Cost
    for t in range(0,YEARS-5):
        model.addConstr(b_CM1[t] == (1200000.0*(w[0][t+1] + w[0][t+2] + w[0][t+3] + w[0][t+4] + w[0][t+5])))
    for t in range(YEARS-5,YEARS-4):
        model.addConstr(b_CM1[t] == (1200000.0*(w[0][t+1] + w[0][t+2] + w[0][t+3] + w[0][t+4])))
    for t in range(YEARS-4,YEARS-3):
        model.addConstr(b_CM1[t] == (1200000.0*(w[0][t+1] + w[0][t+2] + w[0][t+3])))
    for t in range(YEARS-3,YEARS-2):
        model.addConstr(b_CM1[t] == (1200000.0*(w[0][t+1] + w[0][t+2])))
    for t in range(YEARS-2,YEARS-1):
        model.addConstr(b_CM1[t] == (1200000.0*w[0][t+1]))
    for t in range(YEARS-1,YEARS):
        model.addConstr(b_CM1[t] == 0.0)
    for t in range(0,YEARS-3):
        model.addConstr(b_CM2[t] == ((2000000.0/3.0)*(w[1][t+1] + w[1][t+2] + w[1][t+3])))
    for t in range(YEARS-3,YEARS-2):
        model.addConstr(b_CM2[t] == ((2000000.0/3.0)*(w[1][t+1] + w[1][t+2])))
    for t in range(YEARS-2,YEARS-1):
        model.addConstr(b_CM2[t] == ((2000000.0/3.0)*w[1][t+1]))
    for t in range(YEARS-1,YEARS):
        model.addConstr(b_CM2[t] == 0.0)
    for t in range(0,YEARS-3):
        model.addConstr(b_CM3[t] == ((500000.0/3.0)*(w[2][t+1] + w[2][t+2] + w[2][t+3])))
    for t in range(YEARS-3,YEARS-2):
        model.addConstr(b_CM3[t] == ((500000.0/3.0)*(w[2][t+1] + w[2][t+2])))
    for t in range(YEARS-2,YEARS-1):
        model.addConstr(b_CM3[t] == (500000.0/3.0)*w[2][t+1])
    for t in range(YEARS-1,YEARS):
        model.addConstr(b_CM3[t] == 0.0)       
    for t in range(0,YEARS):
        model.addConstr(b_CM4[t] == (0.00533*quicksum(quicksum(q[j][k][t] for j in range(0,SOURCE)) for k in range(0,PP))))
#   Initial Condition 2
    for j in range(0,SOURCE):
        for k in range(0,PP):
            for t in range(0,3):
                model.addConstr(x[j][k][t] == 0.0)
#   Railway Availability Constraints
    for j in range(0,SOURCE):
        for k in range(0,PP):
            if j == k:
                model.addConstr(quicksum(x[j][k][t] for t in range(0,YEARS)) == 0.0)
            elif j != k:
                model.addConstr(quicksum(x[j][k][t] for t in range(0,YEARS)) <= 1.0)                        
######################  Modified Nov 26 START ###################################################
    for j in range(0,SOURCE):
        for k in range(0,PP):
            for t in range(0,YEARS):
                if j == k:
                    model.addConstr(q[j][k][t] <= bigM)
                elif j != k:
                    model.addConstr(q[j][k][t] <= bigM*quicksum(x[j][k][tau] for tau in range(0,t+1)))
######################  Modified Nov 26 END ###################################################
#   Train Availability Constraint
    for j in range(0,SOURCE):
        for k in range(0,PP):
            for t in range(0,YEARS):
                if j == k:
                    model.addConstr(nt[j][k][t] == 0.0)
                elif j != k:
                    model.addConstr(nt[j][k][t] <= bigM*quicksum(x[j][k][tau] for tau in range(0,t+1)))
#   Railway Capacity Constraint
    for j in range(0,SOURCE):
        for k in range(0,PP):
            for t in range(0,YEARS):
                model.addConstr(quicksum(nt[j][k][tau] for tau in range(0,t+1)) <= 6.0*RT[j][k])
######################  Modified Nov 26 START ###################################################
#sum_{tau} F[j][k]*nt[j][k][tau] >= q[j][k][t] for all j, for all k and for all t
    for j in range(0,SOURCE):
        for k in range(0,PP):
            for t in range(0,YEARS):
                if j == k:
                    model.addConstr(F[j][k] >= q[j][k][t])
                elif j != k:
                    model.addConstr(F[j][k]*quicksum(nt[j][k][tau] for tau in range(0,t+1)) >= q[j][k][t])
######################  Modified Nov 26 END ###################################################
#   Railway Budget Constraint                    
#   Railway Setup Budget & Operating Cost
    for t in range(0,YEARS-3):
        model.addConstr(b_RW1[t] == quicksum(quicksum((SC_RW[j][k]/3.0)*(x[j][k][t+1] + x[j][k][t+2] + x[j][k][t+3]) for j in range(0,SOURCE)) for k in range(0,PP)))
    for t in range(YEARS-3,YEARS-2):
        model.addConstr(b_RW1[t] == quicksum(quicksum((SC_RW[j][k]/3.0)*(x[j][k][t+1] + x[j][k][t+2]) for j in range(0,SOURCE)) for k in range(0,PP)))
    for t in range(YEARS-2,YEARS-1):
        model.addConstr(b_RW1[t] == quicksum(quicksum((SC_RW[j][k]/3.0)*(x[j][k][t+1]) for j in range(0,SOURCE)) for k in range(0,PP)))
    for t in range(YEARS-1,YEARS):
        model.addConstr(b_RW1[t] == 0.0)
    for t in range(0,YEARS):
        model.addConstr(b_RW2[t] == quicksum(quicksum(0.00004*DISTANCE1[j][k]*q[j][k][t] for k in range(0,PP)) for j in range(0,SOURCE))) 
#   Trains Budget Constraint
    for t in range(0,YEARS):
        model.addConstr(b_TR[t] == 50000.0*quicksum(quicksum(nt[j][k][t] for j in range(0,SOURCE)) for k in range(0,PP)))
#   Network Constraint 1
    for k in range(0,PP):
        for t in range(0,YEARS):
            model.addConstr(quicksum(q[j][k][t] for j in range(0,SOURCE)) >= (7300.0/3.0)*e[k][t])
#   Network Constraint 2
    for k in range(0,PP):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] == 300.0*quicksum(y[k][tau] for tau in range(0,t+1)))

    for k in range(0,PP):
        for t in range(0,YEARS):
            model.addConstr(quicksum(p[k][n][t] for n in range(0,DEMANDZONE)) <= e[k][t])
#   Network Constraint 3
#   Power Plant Location Constraint
    for k in range(0,3):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 750000.0)
    for k in range(3,4):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 3000.0)
    for k in range(4,10):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 1500.0)
    for k in range(10,12):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 3000.0)        
    for k in range(12,13):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 1500.0)
    for k in range(13,14):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 3000.0)
    for k in range(14,18):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 1500.0)            
    for k in range(18,19):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 3000.0)  
    for k in range(19,PP):
        for t in range(0,YEARS):
            model.addConstr(e[k][t] <= 1500.0)                          
#   Power Plant Budget Constraint
#   Initial Condition 3
    for k in range(0,PP):
        for t in range(0,3):
            model.addConstr(y[k][t] == 0.0)
#   PP Setup Budget & Grid Station Setup Cost & Operating Cost
    for t in range(0,YEARS-3):
        model.addConstr(b_PP1[t] == quicksum(((1000000.0/3.0)*(y[k][t+1] + y[k][t+2] + y[k][t+3])) for k in range(0,PP)))
    for t in range(YEARS-3,YEARS-2):
        model.addConstr(b_PP1[t] == quicksum(((1000000.0/3.0)*(y[k][t+1] + y[k][t+2])) for k in range(0,PP)))
    for t in range(YEARS-2,YEARS-1):
        model.addConstr(b_PP1[t] == quicksum(((1000000.0/3.0)*(y[k][t+1])) for k in range(0,PP)))
    for t in range(YEARS-1,YEARS):
        model.addConstr(b_PP1[t] == 0.0)
    for t in range(0,YEARS):
        model.addConstr(b_PP2[t] == quicksum((SC_TL[k]*y[k][t]) + ((20000.0/300.0)*e[k][t]) for k in range(0,PP)))
#   Demand Constraint
#quicksum((0.92**DISTANCE2[k][n])*p[k][n][t] for k in range(PP)) <= GAP[n][t]    for all n and for all t
    for n in range(0,DEMANDZONE):
        for t in range(0,YEARS):
            model.addConstr(quicksum((0.92**DISTANCE2[k][n])*p[k][n][t] for k in range(0,PP)) <= GAP[n][t])
#   Impact of Energy on GDP

    for t in range(0,1):
        model.addConstr(g[t] == 210741069.91037 + (16567.9049*quicksum(quicksum((0.92**DISTANCE2[k][n])*(p[k][n][t]) for k in range(0,PP)) for n in range(DEMANDZONE))))
    for t in range(1,YEARS):
        model.addConstr(g[t] == g[t-1] + (16567.9049*quicksum(quicksum((0.92**DISTANCE2[k][n])*(p[k][n][t]-p[k][n][t-1]) for k in range(0,PP)) for n in range(DEMANDZONE))))

#NOTE: 2011 GDP_Nominal $210741069.91037 K (year 1)
#   Budget Constraint
#g[t-1]*RA[t] >= b_CM[t] + b_RW1[t] + b_RW2[t] + b_TR[t] + b_PP1[t] + b_PP2[t]   for all t
    for t in range(0,1):
        model.addConstr(210741069.91037*RA[t] >= (b_CM1[t] + b_CM2[t] + b_CM3[t] + b_CM4[t] + b_RW1[t] + b_RW2[t] + b_TR[t] + b_PP1[t] + b_PP2[t]))
    for t in range(1,YEARS):
        model.addConstr((g[t-1]*RA[t]) >= (b_CM1[t] + b_CM2[t] + b_CM3[t] + b_CM4[t] + b_RW1[t] + b_RW2[t] + b_TR[t] + b_PP1[t] + b_PP2[t]))        
#NOTE: year 0 is 2010.
##########FOR TEST: START ###################
    for t in range(0,YEARS):
        model.addConstr(total_cost[t] == (b_CM1[t] + b_CM2[t] + b_CM3[t] + b_CM4[t] + b_RW1[t] + b_RW2[t] + b_TR[t] + b_PP1[t] + b_PP2[t]))   
    for t in range(0,YEARS):
        model.addConstr(yearly_gap[t] == quicksum(GAP[n][t] - quicksum((0.92**DISTANCE2[k][n])*p[k][n][t] for k in range(0,PP)) for n in range(0,DEMANDZONE)))
################### TEST END ####################
#NOTE:This part is not given on a mathematical model, but is just used for checking results
####################################################################################################################
######################### FOR TEST START ############################
    for j in range(0,1):
        for k in range(0,PP):
            for t in range(0,5):
                model.addConstr(q[j][k][t] == 0.0)
    for j in range(1,2):
        for k in range(0,PP):
            for t in range(0,3):
                model.addConstr(q[j][k][t] == 0.0)   
    for j in range(2,SOURCE):
        for k in range(0,PP):
            for t in range(0,3):
                model.addConstr(q[j][k][t] == 0.0) 
    for k in range(0,PP):
        for n in range(0,DEMANDZONE):
            for t in range(0,3):
                model.addConstr(p[k][n][t] == 0.0)
######################### FOR TEST END ##############################                   
# For mine Sonda/Lahkra
    for j in range(0,SOURCE):
        for t in range(0,YEARS):
            if j == 1:
                model.addConstr(q[j][1][t] <= bigM*quicksum(w[1][tau] for tau in range(0,t+1)))
            elif j != 1:
                model.addConstr(q[j][1][t] <= (1 - quicksum(w[1][tau] for tau in range(0,t+1))))
# For mine Thar
    for j in range(0,SOURCE):
        for t in range(0,YEARS):
            if j == 0:
                model.addConstr(q[j][0][t] <= bigM*quicksum(w[0][tau] for tau in range(0,t+1)))
            elif j != 0:
                model.addConstr(q[j][0][t] <= (1 - quicksum(w[0][tau] for tau in range(0,t+1))))
    
    # Finalyzing Modeling
#    model.update()

#######################################
#   Setting Objective Function
#######################################

    model.setObjective(quicksum(BETA[t]*quicksum(GAP[n][t] - quicksum((0.92**DISTANCE2[k][n])*p[k][n][t] for k in range(0,PP)) for n in range(0,DEMANDZONE)) for t in range(YEARS)))

    model.optimize()


#   print "Model Constraints:"
#   for gCon in model.getConstrs():
#       print gCon
        
#   print "Done Pinting constraints"
#    print "Size of constraint list is %s" % (len(model.getConstrs()))


    #    Solve MILP for Coal-Based Energy Supply Chain Problem
#    model.optimize()

    
#     for v in model.getVars():
#        print v.varName, v.x  
#     print 'Obj:', model.objVal
# v.varName
################### PRINTING OUTPUT onto a Text file START ################################
#    Python_Output = open("python_output.txt", "w")
#   numPP = model.getVarByName('y_%s_%s'
#  Python_Output.write(str(numPP))
# Python_Output.close()
    if GDP_Indicator == 1:
        outputfile_name = "python_final_J%dK%dN%dT%dP%d.txt" % (SOURCE,PP,DEMANDZONE,YEARS,percentage)
    elif GDP_Indicator == 2:
        outputfile_name = "python_final_J%dK%dN%dT%dP%d.txt" % (SOURCE,PP,DEMANDZONE,YEARS,percentage)        
    Python_Output = open(outputfile_name, "w")
    for v in model.getVars():
        Python_Output.write("%.5f\t" % (v.x))
    Python_Output.close()
################### PRINTING OUTPUT onto a Text file END   ################################    
except Exception as e:
    print(e)


