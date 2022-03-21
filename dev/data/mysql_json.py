import mysql.connector as mysql
import json
import pandas as pd
## Create Table##
conn = mysql.connect(host="localhost", user="rony", passwd="exp8546$fs", database="toyDB")
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS jsonvals')
c.execute('CREATE TABLE IF NOT EXISTS jsonvals (name VARCHAR(255), city VARCHAR(255), jdoc JSON)')
c.execute('SHOW TABLES')
print(c.fetchall())

## Insert values to table ##
query = "INSERT INTO jsonvals (name, city) VALUES ('Jim', 'London')"
c.execute(query)
query = "INSERT INTO jsonvals (name, city) VALUES ('Jane', 'Paris')"
doc = {'key10': 'value10', 'key22': 'value22', "3": ["NDE", "NDE", "NDE"], "2": ["NDE", "NDE", "NDE"]}
doc = {"1": ["Turbine Hall GL5-7 /C-B (Bay 6b) - Kalbau (DEF_WK07 confirmed not required)", "Diversion Culvert - Backfill and  reinstate quay wall concrete block to 0.5m below 2nd layer of struts", "(BOP) BASIC DESIGN, SPECIFICATION WATER PIPEWORK SYSTEM", "Discharge Culvert /Zone A3 (Western Section) - Trim pipe piles", "LP-1 - Check Axial Displacement of Inner Casing", "Shaft F - Construct permanent shaft wall (Pour 3 of 8)", "Install Containers", "Shaft E - Trim pipe piles", "Align Check of Bearing Casings &amp; Baseplates After Grouting", "Grounding Supports", "Install Equipment/Skids/Pumps", "DETAIL DESIGN, MANUFACTURING, SHOP TEST CONDENSATE EXTRACTION PUMP LCB", "Turbine Hall GL.2-4 /D-C (Bay 6a) - Install upper roof steel structure", "Erection of Blending Station", "Perimeter RC Wall / West Elevation - GL.K -G", "DETAIL DESIGN / CHECKER STEEL MISC. PLATFORM UMC", "BA8 - (1st) BD Consent to Temp works for SCW &amp; Culvert Modification (Resubmit incl wall, excav.&amp; anchor)(Wet){5b1(r)}", "QUOTATION STAGE CONDENSER TUBE CLEANING SYSTEM PAH", "East Elevation at GL.1 / Glazing panels", "Turbine Table TT4 - Close formwork (if any)", "Install Primary Containment", "Install Skid+Auxiliaries", "Install Equipment/Skids/Pumps", "ST I&amp;C TRANSPORT TO SITE FIELD INSTRUMENTATION", "Turbine Hall GL.1-5 /C-B (Bay 7a) - Install standing seam roof cladding [Deferred Works]", "Shaft F - Micro tunneling and pipe jacking from Shaft E (Part 2 of 2)", "Set on Base Boiler Blowdown Vessel", "Placing Hotwell", "DPT /Zone A (Southern Section) - BD Consent for Commencement of Excavation &amp; ELS", "Install Containers - Skid", "ITP for - (00MBU) NOX Water Forwarding System incl. Supply Lines to GT Skid", "Turbine Hall GL.1-5 /F-E (Bay 4a) - Connect installed trusses by secondary beams and bracing", "Fans/Pumps cold commissioning", "(BOP) FINAL CHECK BEFORE SHIPMENT MV CABLES BZK", "RW Collection Pump Rm - Pour basement wall and staircase (Part 1 of 2)", "DPT /Zone C (Northern Section) - Connect CW supply pipeline to Shaft F", "Lifts - Review engineer's drawings and prepare design (AD TBC)", "ITP for - (10MKA) Generator Incl. Bearing System 10 MKD", "PREPARATION BASIC BUILDING DWGS UBF/UBE", "Install Accessories/Supports", "Painting/Insulation", "Install Small Bore Pipe/Valves/Supports", "Boiler Blow Down Pit - Erect wall and column formwork", "East Elevation at GL.1 / Subframe for aluminum features", "Completion of Gas Turbine", "ITP for - (10LCA) Main Condensate Pumps and Supply System for Min. Flow Operation Incl.", "BA5 - Consent for Temporary works for Shaft A, Pump Station, Diversion Culvert (Excav &amp; ELS) {4b4-4}", "Aluminum - BD Approval", "BA8 - Consent for Excav &amp; ELS Plan for Power Island Area (Open Cut)(Phase 3){7c2i}", "Shaft A - Construct 10th layer of 250mm skin wall", "Shaft E -  Intstall lagging plates and 8th layer of strut", "TRANSPORT LUBE OIL MODUL MAV", "Turbine Hall GL.7-10 (Bay 4c) - Deferred Opening", "Install Cabling", "BA5 - Resub.of (Type II) Amendment  for Zone A Sheet Pile Alternative {4b1-alt A-1} [APPROVED AS TYPE I]", "RW Collection Pump Rm - Vertical blinding to the profile of base slab and shallow sump pit", "Installation of Cable Support Structure for HRSG", "Bid Technical Evaluation/Review Process", "ITP for - (10QU) Sampling Container QC", "Close Cooling Water Structure - Construct foundation and plinths"], "2": ["Commissioning test", "Event 009 - 2 nos Pre-drill abortive", "Hydro Test", "Final check for readiness", "Event 008 - Declaration of unplanted area", "Event 017(I) - Advanced Precautionary Grouting", "PAB System commissioning", "Hydro Test", "Event 011A - Formal test report issued for submission in 7 calendar days", "ready for operation, pending operational licence", "testing of PAC chamber stoplog - dry and wet testing", "Precommissioning"], "3": ["NDE", "NDE", "NDE"]}
#doc = {'1': ['Turbine Hall GL5-7 /C-B (Bay 6b) - Kalbau (DEF_WK07 confirmed not required)', 'Diversion Culvert - Backfill and  reinstate quay wall concrete block to 0.5m below 2nd layer of struts', '(BOP) BASIC DESIGN, SPECIFICATION WATER PIPEWORK SYSTEM', 'Discharge Culvert /Zone A3 (Western Section) - Trim pipe piles', 'LP-1 - Check Axial Displacement of Inner Casing', 'Shaft F - Construct permanent shaft wall (Pour 3 of 8)', 'Install Containers', 'Shaft E - Trim pipe piles', 'Align Check of Bearing Casings &amp; Baseplates After Grouting', 'Grounding Supports', 'Install Equipment/Skids/Pumps', 'DETAIL DESIGN, MANUFACTURING, SHOP TEST CONDENSATE EXTRACTION PUMP LCB', 'Turbine Hall GL.2-4 /D-C (Bay 6a) - Install upper roof steel structure', 'Erection of Blending Station', 'Perimeter RC Wall / West Elevation - GL.K -G', 'DETAIL DESIGN / CHECKER STEEL MISC. PLATFORM UMC', 'BA8 - (1st) BD Consent to Temp works for SCW &amp; Culvert Modification (Resubmit incl wall, excav.&amp; anchor)(Wet){5b1(r)}', 'QUOTATION STAGE CONDENSER TUBE CLEANING SYSTEM PAH', 'East Elevation at GL.1 / Glazing panels', 'Turbine Table TT4 - Close formwork (if any)', 'Install Primary Containment', 'Install Skid+Auxiliaries', 'Install Equipment/Skids/Pumps', 'ST I&amp;C TRANSPORT TO SITE FIELD INSTRUMENTATION', 'Turbine Hall GL.1-5 /C-B (Bay 7a) - Install standing seam roof cladding [Deferred Works]', 'Shaft F - Micro tunneling and pipe jacking from Shaft E (Part 2 of 2)', 'Set on Base Boiler Blowdown Vessel', 'Placing Hotwell', 'DPT /Zone A (Southern Section) - BD Consent for Commencement of Excavation &amp; ELS', 'Install Containers - Skid', 'ITP for - (00MBU) NOX Water Forwarding System incl. Supply Lines to GT Skid', 'Turbine Hall GL.1-5 /F-E (Bay 4a) - Connect installed trusses by secondary beams and bracing', 'Fans/Pumps cold commissioning', '(BOP) FINAL CHECK BEFORE SHIPMENT MV CABLES BZK', 'RW Collection Pump Rm - Pour basement wall and staircase (Part 1 of 2)', 'DPT /Zone C (Northern Section) - Connect CW supply pipeline to Shaft F', 'Lifts - Review engineers drawings and prepare design (AD TBC)', 'ITP for - (10MKA) Generator Incl. Bearing System 10 MKD', 'PREPARATION BASIC BUILDING DWGS UBF/UBE', 'Install Accessories/Supports', 'Painting/Insulation', 'Install Small Bore Pipe/Valves/Supports', 'Boiler Blow Down Pit - Erect wall and column formwork', 'East Elevation at GL.1 / Subframe for aluminum features', 'Completion of Gas Turbine', 'ITP for - (10LCA) Main Condensate Pumps and Supply System for Min. Flow Operation Incl.', 'BA5 - Consent for Temporary works for Shaft A, Pump Station, Diversion Culvert (Excav &amp; ELS) {4b4-4}', 'Aluminum - BD Approval', 'BA8 - Consent for Excav &amp; ELS Plan for Power Island Area (Open Cut)(Phase 3){7c2i}', 'Shaft A - Construct 10th layer of 250mm skin wall', 'Shaft E -  Intstall lagging plates and 8th layer of strut', 'TRANSPORT LUBE OIL MODUL MAV', 'Turbine Hall GL.7-10 (Bay 4c) - Deferred Opening', 'Install Cabling', 'BA5 - Resub.of (Type II) Amendment  for Zone A Sheet Pile Alternative {4b1-alt A-1} [APPROVED AS TYPE I]', 'RW Collection Pump Rm - Vertical blinding to the profile of base slab and shallow sump pit', 'Installation of Cable Support Structure for HRSG', 'Bid Technical Evaluation/Review Process', 'ITP for - (10QU) Sampling Container QC', 'Close Cooling Water Structure - Construct foundation and plinths'], '2': ['Commissioning test', 'Event 009 - 2 nos Pre-drill abortive', 'Hydro Test', 'Final check for readiness', 'Event 008 - Declaration of unplanted area', 'Event 017(I) - Advanced Precautionary Grouting', 'PAB System commissioning', 'Hydro Test', 'Event 011A - Formal test report issued for submission in 7 calendar days', 'ready for operation, pending operational licence', 'testing of PAC chamber stoplog - dry and wet testing', 'Precommissioning'], '3': ['NDE', 'NDE', 'NDE']}
doc = json.dumps(doc)
doc = doc.replace("'", "''")
print('doc:', doc, type(doc))
table_name = 'jsonvals'
query = "UPDATE {tn} SET jdoc ='{d}' WHERE name='Jim' AND city='LONDON'".format(d=doc, tn=table_name)
print('query:', query)
c.execute(query)


# query = 'INSERT INTO jsonvals (jdoc) VALUES (%s)'
# c.execute(query, doc)

query = 'INSERT INTO jsonvals (name, jdoc) VALUES (%s, %s)'
values = ('Hafeez', '{"key1": "value1", "key2": "value2"}')
c.execute(query, values)
doc = {'key5': 'value5', 'key6': 'value6'}
doc = json.dumps(doc)
values = ('John', doc)
c.execute(query, values)

doc = {'key5': 'value5', 'key6': 'value6'}
doc = json.dumps(doc)
print(doc, type(doc))
values = ('Jack', doc)
c.execute(query, values)


conn.commit()
c.execute('SELECT * FROM jsonvals')
print(c.fetchall())
df = pd.read_sql_query('SELECT * FROM jsonvals', conn)
print(df)


