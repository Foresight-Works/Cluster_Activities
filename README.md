# Cluster_Activities

Group program activities by name and WBS charecteristics.  
*Data*: Zipped file produced from program files(.xer) converted to graphml.  
The data is posted as an http request.   
*Result*: Activity clusters keyed by a cluster name derived from the name of cluster members.  
## Process and Method 
Versions 1,2  
To be documented  
## Research UI  
The research UI is formed in a Jupyter notebook allowing the user to load the data and define the characteristics of the run.  
**Run configuration**  
1. The file(s) to analyse
2. Granularity level, number of clusters (optional)  
3. Minimum number of tasks in cluster (Default=4)
4. Evaluation metrics weights (Default=1)   

## Results 
*Database*: CAdb (Squlite DB)  
*Table*: experiments, indexed by experiment_id (PK) and run ids      
*UI*: The valuation scores table is returned to the UI   
*Clustering file*: response.npy, enabling clusters query by cluster names.  






