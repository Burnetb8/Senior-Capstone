"""
this file merges the files created by atcc.py and hiwire.py, then splits them into suitable test and train files in the .json format

"""
import json
import io

all_manifest = 'manifests/atcc_all.json'
hiwire_manifest = 'manifests/hiwire_all.json'
train_manifest = 'manifests/atcc_train.json'
validation_manifest = 'manifests/atcc_validation.json'


def split_json(all_manifest : str, hiwire_manifest : str, train_manifest : str, validation_manifest : str):
    """
    
    load atcc_all.json and hiwire_all.json from file then combine and split them into test and train files
    split ratio is train/total so a split_ratio = 0.75 would mean 75% goes to train and 25% to validation

    """
    
    split_ratio = 0.75

    #atcc_all_json = open(all_manifest, "r")
    #to remove the first not nessicary line
    #print(atcc_all_json.readline())


    with open(all_manifest) as f:
        atcc_all_json = f.read().splitlines()

    with open(hiwire_manifest) as f:
        hiwire_all_json = f.read().splitlines()

    atcc_all_json += hiwire_all_json

    x = 3

    #print(type(atcc_all_json))
    #print(atcc_all_json[x])
    #print(type(json.loads(atcc_all_json[x])))
    #print(type(json.loads(atcc_all_json[x])['duration']))


    #Removing clips with duration less than 1 cause that is causing errors
    mininum_duration = 1

    for atc in atcc_all_json:
        if(json.loads(atc)['duration'] < mininum_duration):
            atcc_all_json.remove(atc)

    #creating training set
    training_length = int(len(atcc_all_json) * split_ratio)
    train_list = atcc_all_json[1:training_length]

    with open(train_manifest, 'w') as manifest:
        #manifest.write("[\n")
        manifest.write("\n".join(train_list))
        #manifest.write("]")

    #creating validation set
    data_len = int(len(atcc_all_json))
    validation_list = atcc_all_json[training_length + 1:data_len]

    with open(validation_manifest, 'w') as manifest:
        #manifest.write("[ \n")
        manifest.write("\n".join(validation_list))
        #manifest.write("]")


if __name__ == "__main__":
    
    #print(atcc_all_json.readline())
    #atcc_all = json.load(atcc_all_json.read())
    #print(atcc_all)

    # run split_json function
    split_json(all_manifest,hiwire_manifest,train_manifest,validation_manifest)




