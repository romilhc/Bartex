import boto
import json
import sys
import time
import re
from nltk.corpus import stopwords
import string

stop = stopwords.words('english')
def realtime_predict(ml_model_id, record):
    """Takes a string ml_model_id, and a dict record, and makes a realtime
    prediction call, if the ML Model has a realtime endpoint.
    If the ML Model doesn't have a realtime endpoint, it creates one instead
    of calling predict()
    """
    ml = boto.connect_machinelearning()
    print("Hi: ", ml)
    ml.describe_ml_models(limit=1)
    model = ml.get_ml_model(ml_model_id)

    endpoint = model.get('EndpointInfo', {}).get('EndpointUrl', '')
    print("Hello: ")
    #endpoint = endpoint.replace("https://", "")  # This shouldn't be needed
    if endpoint:
        print('ml.predict("%s", %s, "%s") # returns...' % (ml_model_id,
                                                           json.dumps(record, indent=2), endpoint))
        start = time.time()
        prediction = ml.predict(ml_model_id, record, predict_endpoint=endpoint)
        latency_ms = (time.time() - start)*1000
        print(json.dumps(prediction, indent=2))
        print("Latency: %.2fms" % latency_ms)
        return prediction['Prediction']['predictedValue']
    else:
        print(
            '# Missing realtime endpoint\nml.create_realtime_endpoint("%s")' % ml_model_id)
        result = ml.create_realtime_endpoint(ml_model_id)
        print(json.dumps(result, indent=2))
        print("""# Predictions will fail until the endpoint has been fully created.
# Note that you will be charged a reservation fee until this endpoint is deleted.
# Delete with:
    python realtime.py %s --deleteEndpoint""" % ml_model_id)

# Remove punctuations
def clean_data(record):
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    for k in record.keys():
        v = record[k]
        if type(v) == str:
            v = regex.sub('', v)
            v = set([word.lower() for word in v.split() if word not in stop])
            record[k] = ' '.join(v)
            print(record[k])
    return record

def prediction(record):
    try:
        ml_model_id = 'ml-5MxkRcr866m'
        record = clean_data(record)
        return '{0:.2f}'.format(realtime_predict(ml_model_id, record))
    except:
        print(__doc__)
        sys.exit(-1)
