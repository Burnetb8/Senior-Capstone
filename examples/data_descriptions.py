import json

all_manifest = 'utils/manifests/atcc_all.json'

all_file = open(all_manifest, 'r')

nice_data = []

for l in all_file:
    nice_data.append(json.loads(l))
    

duration_sum = 0
instance_count = 0
word_sum = 0

for l in nice_data:
    instance_count += 1
    duration_sum += l['duration']
    word_sum += l['text'].count(' ')


avg_dur = duration_sum / instance_count
avg_word = word_sum / instance_count

print('Average Duration ' + str(avg_dur))
print('Average Number of Words ' + str(avg_word))
    