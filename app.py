from flask import Flask, render_template, request
from BackEnd import parser, engine, get_mapper, lstm_real
from datetime import datetime
import json
import os


template_dir = os.path.abspath('static')
cachedDir = "cachedData"
if (not os.path.isdir(cachedDir)):
    os.makedirs(cachedDir)
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/getDataSet', methods=["POST"])
def getDataSetWrapper():
    ticker = get_mapper.nameToTicker(request.form['stockTicker'])
    return getDataSet(ticker)

def getDataSet(ticker):
    fname = cachedDir+"/DataSet-" + ticker + ".txt"
    if os.path.isfile(fname):
        with open(fname, 'r') as json_file:  
            return json_file.read()
    with open(fname, 'w') as outfile: 
        data = parser.getDataSet(ticker)
        json.dump(data, outfile)
        return json.dumps(data)

@app.route("/marketData", methods=["POST"])
def getMarketData():
    fname =  cachedDir+"/marketData.txt"
    if os.path.isfile(fname):
        with open(fname, 'r') as json_file:  
            return json_file.read()
    with open(fname, 'w') as outfile: 
        data = [parser.getDataSet("^GSPC"), parser.getDataSet("^IXIC"), parser.getDataSet("^DJI")]
        json.dump(data, outfile)
        return json.dumps(data)

@app.route('/getStat', methods=["POST"])
def getStatWrapper():
    ticker = get_mapper.nameToTicker(request.form['stockTicker'])
    return getStat(ticker)

def getStat(ticker):
    fname =  cachedDir+"/Stat-" + ticker + ".txt"
    if os.path.isfile(fname):
        with open(fname, 'r') as json_file:  
            return json_file.read()
    with open(fname, 'w') as outfile: 
        data = parser.getStat(ticker)
        json.dump(data, outfile)
        return json.dumps(data)
    return json.dumps()

@app.route('/getMLStats', methods=['POST'])
def getNextDay():
    ticker = get_mapper.nameToTicker(request.form['stockTicker'])
    fname = cachedDir+"/MLStats-" + ticker + ".txt"
    if os.path.isfile(fname):
        with open(fname, 'r') as json_file:
            return json_file.read()
    with open(fname, 'w') as outfile: 
        jsonData = getDataSet(ticker)
        data = json.loads(jsonData)
        start, dates, prices = engine.parse_data(data)
        svm = engine.train(dates, prices)
        SVM_predictValue = engine.predict(svm, dates[len(dates) - 1])
        LSTM_predictValue = lstm_real.LSTM_engine(data)
        predictValue = {"SVM": SVM_predictValue, "LSTM": LSTM_predictValue}
        json.dump(predictValue, outfile)
        return json.dumps(predictValue)

if __name__ == "__main__":
    app.run()
