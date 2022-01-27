# Cluster_Activities
Search project plans for activities which are similar to the activity query, and analyze these activities for their planned and actual durations

**Project Names**  
Atif: Focus on the combined cycle gas turbines CCGT D1, D2 (CLT), DUKE 1, and DUKE 2 (Duke Energy).
*DGDA DG*: Diriyah Gate Development Authority - Diriyah Gate 2 is the 2nd part of the project  
*Sime Darby*: Name of the company that owned the projects in that file  
This file only has unique ID codes for projects rather than any project names but they are distinct and grouped  
*CCGT*: Combined Cycle Gas Turbine - a type of energy project  
*D1/D2*: Internal names of the projects owned by CLP  
*Duke*: Duke Energy, a company that builds energy projects such as CCGTs  

DB based Set-up  
1. Build project database (CA)  
script: dev/postgres/dp.py
2. CA.names: The raw data from the csv (check headers compatibility between csvs)
