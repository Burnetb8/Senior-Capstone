"""
this file contains the nessicary code to split the .json file 
created by atcc.py into suitable test and train files

"""
import json
import io

all_manifest = 'manifests/atcc_all.json'
train_manifest = 'manifests/atcc_train.json'
validation_manifest = 'manifests/atcc_validation.json'


def split_json(all_manifest : str, train_manifest : str, validation_manifest : str) -> []:
    
    #atcc_all_json = open(all_manifest, "r")
    #to remove the first not nessicary line
    #print(atcc_all_json.readline())


    with open(all_manifest) as f:
        atcc_all_json = f.read().splitlines()

    #training dataset
    train_list = atcc_all_json[1:600]

    with open(train_manifest, 'w') as manifest:
        #manifest.write("[\n")
        manifest.write("\n".join(train_list))
        #manifest.write("]")

    validation_list = atcc_all_json[601:900]

    with open(validation_manifest, 'w') as manifest:
        #manifest.write("[ \n")
        manifest.write("\n".join(validation_list))
        #manifest.write("]")


if __name__ == "__main__":
    
    #print(atcc_all_json.readline())
    #atcc_all = json.load(atcc_all_json.read())
    #print(atcc_all)

    # run split_json function
    split_json(all_manifest,train_manifest,validation_manifest)




