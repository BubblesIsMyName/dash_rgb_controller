from copy import copy
import json
import datetime

def save_json_output(dict_to_save,name):
        out_file = open("./{}.json".format(name),"w")
        json.dump(dict_to_save,out_file,indent=4)
        out_file.close()

def load_json(name):
        # in_file = open("./{}.json".format(name),"r")
        in_file = open(name,"r")
        dict_out  = json.load(in_file)
        return dict_out

