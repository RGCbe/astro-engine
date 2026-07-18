#!/bin/bash
cd /opt/astro
for book in Sarvartha_Chintamani BPHS1 KP_Reader_3_Predictive Bhrigu_Samhita Jataka_Bharanam; do
  ./venv/bin/python -c "
import json
d=json.load(open('gemma_extractions/${book}_deep.json'))
last=d.get('last_chunk_processed',-1)
total=d.get('n_chunks_total',0)
print('${book}:', last+1, '/', total, 'complete='+str(d.get('is_complete',False)), 'rules='+str(len(d.get('rules',[]))))
"
done
ps aux | grep deep_extract | grep -v grep || echo "no extract running"
