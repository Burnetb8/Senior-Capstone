import json
import pandas
import matplotlib.pyplot as plt

all_manifest = 'utils/manifests/atcc_all.json'

all_file = open(all_manifest, 'r')

nice_data = []

for l in all_file:
    nice_data.append(json.loads(l))
    

durations = []
words = []

for l in nice_data:

    durations.append(l['duration'])
    words.append(l['text'].count(' '))

temp = {"durations":durations , "words":words}

datavals = pandas.DataFrame(temp)

#print(datavals)

print('Average Duration ' + str(datavals["durations"].mean()))
print('Std of Duration ' + str(datavals["durations"].std()))
print('With a minimum of ' + str(datavals["durations"].min()) + ' and a max of ' + str(datavals["durations"].max()) + ' seconds')
print('Average Number of Words ' + str(datavals["words"].mean()))
print('Std of Words ' + str(datavals["words"].std()))
print('With a minimum of ' + str(datavals["words"].min()) + ' and a max of ' + str(datavals["words"].max()) + ' words')

dur_graph = datavals['durations'].plot.hist(bins=24)
#word_graph = datavals['words'].plot.hist(bins=72)

plt.show()