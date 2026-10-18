import os, json
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, make_response

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "demo-only-change-before-production")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

SEED = {
 "centres":[
  {"id":1,"name":"PHC Sukhpur","district":"Demo District","type":"PHC","patients":86,"beds":12,"occupied":10,"doctors":4,"present":3,"tests":8,"available_tests":6,"paracetamol":18,"ors":7,"expiry_days":22,"weekly":[54,60,63,70,72,80,86]},
  {"id":2,"name":"CHC Rampur","district":"Demo District","type":"CHC","patients":132,"beds":30,"occupied":18,"doctors":8,"present":7,"tests":12,"available_tests":11,"paracetamol":65,"ors":42,"expiry_days":120,"weekly":[94,98,104,110,115,125,132]},
  {"id":3,"name":"PHC Devgarh","district":"Demo District","type":"PHC","patients":48,"beds":10,"occupied":3,"doctors":3,"present":2,"tests":7,"available_tests":5,"paracetamol":9,"ors":22,"expiry_days":65,"weekly":[35,39,41,44,46,45,48]},
  {"id":4,"name":"CHC Nandgaon","district":"Demo District","type":"CHC","patients":101,"beds":24,"occupied":21,"doctors":6,"present":4,"tests":10,"available_tests":7,"paracetamol":34,"ors":12,"expiry_days":14,"weekly":[70,73,80,84,91,95,101]}
 ]
}

def clone(obj):
 return json.loads(json.dumps(obj))

def load_data():
 if not os.path.exists(DATA_FILE): save_data(clone(SEED))
 try:
  with open(DATA_FILE, encoding="utf-8") as f: return json.load(f)
 except (ValueError,OSError): return clone(SEED)

def save_data(data):
 with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)

def analyze(centres):
 alerts=[]; forecasts=[]; risks=[]
 for c in centres:
  occ=round(c["occupied"]/max(c["beds"],1)*100)
  attend=round(c["present"]/max(c["doctors"],1)*100)
  for item,key,threshold in [("Paracetamol","paracetamol",20),("ORS","ors",15)]:
   if c[key] < threshold:
    alerts.append({"level":"critical" if c[key] < 10 else "warning","kind":"Stock","centre":c["name"],"title":f"{item} stock low at {c['name']}","detail":f"{c[key]} units remaining · threshold {threshold}"})
  if occ>=80:
   alerts.append({"level":"warning","kind":"Beds","centre":c["name"],"title":f"Bed capacity pressure at {c['name']}","detail":f"{occ}% occupied · {c['beds']-c['occupied']} beds free"})
  if attend<75:
   alerts.append({"level":"warning","kind":"Staff","centre":c["name"],"title":f"Doctor attendance needs review","detail":f"{c['present']} of {c['doctors']} doctors present at {c['name']}"})
  if c["available_tests"]<c["tests"]:
   alerts.append({"level":"info","kind":"Diagnostics","centre":c["name"],"title":f"Test availability gap at {c['name']}","detail":f"{c['available_tests']} of {c['tests']} tests available"})
  if c["expiry_days"]<=30:
   alerts.append({"level":"warning","kind":"Expiry","centre":c["name"],"title":f"Expiry watch at {c['name']}","detail":f"Demo stock has an item expiring in {c['expiry_days']} days"})
  w=c.get("weekly",[c["patients"]]*7)
  delta=(w[-1]-w[0])/max(len(w)-1,1)
  forecast=max(0,round(w[-1]+delta))
  forecasts.append({"name":c["name"],"today":c["patients"],"forecast":forecast,"delta":forecast-c["patients"],"weekly":w})
  risk=min(100, round((max(0,100-occ)*0.12)+(max(0,100-attend)*0.22)+(max(0,20-c["paracetamol"])*1.3)+(max(0,15-c["ors"])*1.1)+(max(0,c["tests"]-c["available_tests"])*2)))
  risks.append({"name":c["name"],"score":risk,"label":"High" if risk>=55 else ("Medium" if risk>=30 else "Low")})
 # Simple stock-transfer proposal, subject to human review
 by_stock=sorted(centres,key=lambda x:x["paracetamol"])
 transfers=[]
 if len(by_stock)>1:
  receiver,donor=by_stock[0],by_stock[-1]
  need=max(0,20-receiver["paracetamol"])
  surplus=max(0,donor["paracetamol"]-30)
  qty=min(need,surplus,15)
  if qty:
   transfers.append({"item":"Paracetamol","from":donor["name"],"to":receiver["name"],"qty":qty,"why":f"{receiver['name']} has {receiver['paracetamol']} units; {donor['name']} has {donor['paracetamol']} units."})
 return alerts,forecasts,risks,transfers

@app.route("/")
def dashboard():
 data=load_data(); centres=data["centres"]
 alerts,forecasts,risks,transfers=analyze(centres)
 return render_template("index.html",centres=centres,alerts=alerts,forecasts=forecasts,risks=risks,transfers=transfers,
  total_patients=sum(c["patients"] for c in centres),free_beds=sum(c["beds"]-c["occupied"] for c in centres),
  total_doctors=sum(c["doctors"] for c in centres),present_doctors=sum(c["present"] for c in centres),
  today=date.today().strftime("%d %b %Y"))

@app.post("/update")
def update():
 data=load_data()
 try:
  c=next(c for c in data["centres"] if c["id"]==int(request.form.get("centre_id","0")))
  c["patients"]=max(0,int(request.form["patients"]))
  c["occupied"]=min(c["beds"],max(0,int(request.form["occupied"])))
  c["present"]=min(c["doctors"],max(0,int(request.form["present"])))
  c["available_tests"]=min(c["tests"],max(0,int(request.form["available_tests"])))
  c["paracetamol"]=max(0,int(request.form["paracetamol"]))
  c["ors"]=max(0,int(request.form["ors"]))
  c["weekly"][-1]=c["patients"]
  save_data(data); flash("Centre updated. Alerts and insights recalculated.","success")
 except (ValueError,KeyError,StopIteration):
  flash("Please check the entered values and try again.","error")
 return redirect(url_for("dashboard"))

@app.post("/simulate")
def simulate():
 data=load_data()
 try:
  c=next(c for c in data["centres"] if c["id"]==int(request.form.get("centre_id","1")))
  c["paracetamol"]=max(0,c["paracetamol"]-12)
  c["ors"]=max(0,c["ors"]-5)
  c["patients"]+=15
  c["occupied"]=min(c["beds"],c["occupied"]+2)
  c["weekly"][-1]=c["patients"]
  save_data(data); flash(f"Scenario simulated for {c['name']}: patient surge and medicine use. Review updated alerts.","info")
 except (ValueError,StopIteration):
  flash("Could not run the scenario.","error")
 return redirect(url_for("dashboard"))

@app.post("/reset")
def reset():
 save_data(clone(SEED)); flash("Sample data restored to original demo scenario.","success")
 return redirect(url_for("dashboard"))

@app.get("/health")
def health():
 return {"status":"ok","app":"SwasthyaSetu"}

if __name__=="__main__":
 app.run(host="0.0.0.0",port=int(os.environ.get("PORT",8080)),debug=False)
