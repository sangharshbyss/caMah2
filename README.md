# caMah2
Case analysis of criminal cases filed in the state of Maharashtra
Currently, It collects data on FIRs from the state police website. 
For particular acts or cases, it downloads copies of those FIRs. 
Further, It envisages analysing these registered cases using different tools and applying statistical methods.
The current code, main.py, is for data collection. 
It works with a module dataCollection.py. The logic of the code is given below: 
1. Outer loop with from and to dates
1a. Inner loop iterating over all districts
1a.1.open page (with refresh - this is a requirement of the portal)
1a.2. insert from and to dates
1a.3. insert district
1a.4. view - set to 50
1a.5. Search
1a.6. catch number of records (with output of these numbers)
1a.7. if 1a.6>0 then crate csv of the table and separate csv with cell value of "x".
1a.7.a check for cell with "x" values (internal iteration).
If found click on links and download, iteratively.
1a.8. if 1a.6>50 then look for page 2 link and click or else
break and go to next iteration (district)
1a.8.a. check if page loaded if yes go ahead or else check 5 times with interval of 1sec.
if it still does not load break and go to next iteration (next district in this case)
1a.9 repeat 1a.7
1a.10 if 1a.6>100 then look for page 2 link and click or else
break and go to next iteration (district)
1a.11 repeat 1a8 followed by 1a.9
1a.12 if 1a.6>150 then look for page 3 link and click or else
break and go to next iteration (district)
1a.13 repeat 1a8 followed by 1a.9
1a.14 if 1a.6>200 then look for page 4 link and click or else
break and go to next iteration (district)
1a.15 repeat 1a8 followed by 1a.9
1a.16 if 1a.6>250 then look for page 5 link and click or else
break and go to next iteration (district)
1a.17 repeat 1a8 followed by 1a.9
1a.18 go to next district (iteration of 2 loop started at 1a).
