import phpserialize
import xmltodict, json
from phpserialize import unserialize
import json
import base64
import os
from datetime import datetime
import logging
from pymongo import MongoClient
import certifi
from bson import BSON
import re

logging.basicConfig(filename='error.log', level=logging.DEBUG, 
                    format='%(asctime)s %(lineno)d %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

#strptime = datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

incomingDirectory = 'incoming'
processedDirectory = 'processed'
outputDirectory = 'output/output - '+str(datetime.today().strftime("%Y%m%d %H%M%S"))
failDirectory = 'fail'

countFail = 0
countXml = 0
countElse = 0

def unserializePWA(phpSerial):
    # cast string to bytes
    phpSerial = phpSerial.encode('utf-8')

    # unserialize array
    output = phpserialize.unserialize(phpSerial, decode_strings=True)

    # dump and load to force keys to strings
    output = json.dumps(output)
    output = json.loads(output)

    return output

def base64Decode(stepDetailsBase64):
    # decode base64
    base64_message = stepDetailsBase64
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    #print(message)
    
    return message

def jsonifyFlow(pwaFlow):
    for step, value in pwaFlow["root"]["steps"].items():
        #unpack tuples and iterate
        #print(value["stepDetails"])
        
        phpSerial = base64Decode(value["stepDetails"])
        unserialized = unserializePWA(phpSerial)

        pwaFlow["root"]["steps"][step]['stepDetails'] = unserialized

        #print(value)

    return pwaFlow

def connectToMongo():
    #connect to mongodb
    print("Connecting to MongoDB...")
    connection_string = "mongodb+srv://dGarcia:DuuopmPyH2VcpG4D@migratecluster0.si2d6.mongodb.net/admin?readPreference=nearest"
    mongo_client = MongoClient(connection_string, tlsCAFile=certifi.where())
    db = mongo_client['Workflows_1129_4992']
    collection = db['SCPodio']

    print("Count in Workflows_1129_4992/SCPodio: "+str(collection.count_documents({})))

    return collection

def writeToMongo(mongoDBCollection, document):
    #testVal = {"some text": "ObjectRocket: Database Management and Hosting"}
    result = mongoDBCollection.update_one(
        {"filename": "flow-2814646.xml"},
        {"$set": BSON.encode(document)},
        upsert=True
    )
    # upserted_id is 'None' if ID already existed at time of call
    return "Upserted ID:"+str(result.upserted_id)

#### MAIN ####
#create output directory
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

#connect to mongodb
mongoDBCollection = connectToMongo()

# get all files in the directory
for filename in os.listdir(incomingDirectory):
    if filename.endswith(".xml"):
        try:
            #read the file
            with open(os.path.join(incomingDirectory, filename), 'rb') as file:
                #print(filename)

                #convert xml to json
                pwaFlow = xmltodict.parse(file)
                jsonifiedPwaFlow = jsonifyFlow(pwaFlow)
                #add filename to json
                jsonifiedPwaFlow["_id"] = re.sub('\D', '', filename) 
                jsonifiedPwaFlow["root"]["filename"] = filename
                #add date processed to json
                jsonifiedPwaFlow["root"]["dateProcessed"] = datetime.now().strftime("%Y%m%d %H%M%S")

                #print(json.dumps(jsonifiedPwaFlow, indent=2))
                countXml += 1
        except Exception as err:
            #logging(error=err)            
            logger.error(err)
            countFail += 1
            #move file to new folder
            os.rename(os.path.join(incomingDirectory, filename), os.path.join(failDirectory, filename))
        else:
            #move file to new folder
            os.rename(os.path.join(incomingDirectory, filename), os.path.join(processedDirectory, filename))
            #write to new file
            with open(os.path.join(outputDirectory, filename[:-4]) + '.json', 'w') as file:
                json.dump(jsonifiedPwaFlow, file, indent=2)

            with open(os.path.join(outputDirectory, filename[:-4]) + '.json', 'r') as file:
                #get contents of file as string
                fileContents = file.read()

                result = mongoDBCollection.update_one(
                    {"filename": jsonifiedPwaFlow["root"]["filename"]},
                    {"$set": jsonifiedPwaFlow},
                    upsert=True,
                    bypass_document_validation=True
                )
                print("Upserted ID:"+str(result.upserted_id))

    else:
        countElse += 1
        continue

print('XML files processed:', countXml)
print('Other files:', countElse)
print('Failed files:', countFail)