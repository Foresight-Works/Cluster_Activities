import os
import subprocess
#script = 'modules/words_pairs.py'
#subprocess.call('python {s}'.format(s=script), shell=True)
# subprocess.call('python modules/words_pairs.py', shell=True)
results_dir = '/home/rony/Projects_Code/Cluster_Activities/results/CLP_CCGT'

def pipeline():
    subprocess.call('python tokens_distances.py', shell=True)
    #words_pairs_score = float(open(os.path.join(results_dir, 'words_pairs_score.txt')).read())
    #print('words_pairs_score from run script:', words_pairs_score)

pipeline()
