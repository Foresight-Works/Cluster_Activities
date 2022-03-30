from dev.pipeline.service.cluster_service5.setup import *

files = [f for f in os.listdir(raw_data_dir) if 'csv' in f]
dfs = {}
names_companies_dicts = []
task_names = []
cols = ['ID', 'Activity ID', 'Activity Name', 'Project ID', 'Project Name', 'Activity type',\
        'Parent WBS ID', 'Resources', 'Resource IDs', 'Primary Resource', 'Schedule % Complete',\
        'Activity Status', 'Planned Start', 'Actual Start', 'Planned Finish', 'Actual Finish', 'Predecessor Details',\
        'Predecessors', 'Successor Details', 'Successors', 'Project Week Planned Start', 'Project Week Actual Start',\
        'Project Week Planned Finish', 'Project Week Actual Finish', 'Project Month Planned Start', 'Project Month Actual Start',\
        'Project Month Planned Finish', 'Project Month Actual Finish', 'Activity nth Percentile Rank by Start Date', 'Total Float',\
        'Full Path', 'In Degree Original', 'Out Degree Original', 'Betweeness Centrality Original', 'Forward Reach Original',\
        'Reverse Reach Original', 'Duration Original', 'Critical Path Index Original', 'Page Rank Original', 'In Degree Normalized',\
        'Out Degree Normalized', 'Betweeness Centrality Normalized', 'Forward Reach Normalized', \
        'Reverse Reach Normalized', 'Duration Normalized',\
        'Critical Path Index Normalized', 'Page Rank Normalized']

print('Read and merge datasets')
companies_df = pd.DataFrame(columns=cols)
for index, file in enumerate(files):
    df = pd.read_csv(os.path.join(raw_data_dir, file))
    print('Reading file:', file)
    company = re.sub('\d{4}[-|_]\d{2}[-|_]\d{2}|\.csv|_', '', file).rstrip().lstrip()
    company = company.replace(' ', '_')
    company_id = index+1
    df['company'], df['company_id'] = company, company_id
    print('Company:{c} | Company ID:{cid}'.format(c=company, cid=company_id))
    companies_df = companies_df.append(df)
del(df)
print('Filter empty columns')

companies_df = filter_empty_columns(companies_df)
companies_df.columns = [c.replace(' ', '_').lower() for c in companies_df.columns]
df_info(companies_df).to_excel(os.path.join(results_dir, 'companies_df_info.xlsx'), index=False)

# Count task cluster_key repeats in the dataset
names_counts = count_names(companies_df)
names_counts.to_excel(os.path.join(results_dir, 'names_counts.xlsx'), index=False)
#companies_df.to_excel(os.path.join(data_dir, 'companies_data.xlsx'), index=False)