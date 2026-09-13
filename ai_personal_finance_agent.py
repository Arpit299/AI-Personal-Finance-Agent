import argparse
import csv
import json
import math
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path

class FinanceAgent:
 def __init__(self,transactions,budgets=None,goals=None):
  self.transactions=transactions
  self.budgets=budgets or {}
  self.goals=goals or {}
  self.categories=Counter()
  self.merchant_groups=defaultdict(list)
  self.recurring=[]
  self.anomalies=[]
 def money(self,value):
  try:return round(float(str(value).replace(',','').replace('₹','').replace('$','').strip()),2)
  except:return 0.0
 def parse_date(self,value):
  for fmt in ('%Y-%m-%d','%d-%m-%Y','%d/%m/%Y','%Y/%m/%d'):
   try:return datetime.strptime(str(value).strip(),fmt)
   except ValueError:pass
  raise ValueError(f'Invalid date: {value}')
 def normalize_category(self,value):
  text=str(value or '').strip().lower()
  mapping={'food':'Food','dining':'Food','restaurant':'Food','groceries':'Food','transport':'Transport','travel':'Transport','fuel':'Transport','rent':'Housing','housing':'Housing','utilities':'Utilities','electricity':'Utilities','internet':'Utilities','shopping':'Shopping','entertainment':'Entertainment','salary':'Income','income':'Income','medical':'Health','health':'Health','education':'Education'}
  return mapping.get(text,str(value or 'Other').strip().title() or 'Other')
 def prepare(self):
  for item in self.transactions:
   item['amount']=self.money(item.get('amount',0))
   item['date_obj']=self.parse_date(item.get('date',''))
   item['category']=self.normalize_category(item.get('category','Other'))
   item['merchant']=str(item.get('merchant') or item.get('description') or 'Unknown').strip()
   item['type']=str(item.get('type') or ('income' if item['category']=='Income' else 'expense')).lower()
   if item['type']!='income' and item['category']!='Income':self.categories[item['category']]+=item['amount']
   self.merchant_groups[item['merchant'].lower()].append(item)
 def summary(self):
  income=sum(x['amount'] for x in self.transactions if x['type']=='income' or x['category']=='Income')
  expenses=sum(x['amount'] for x in self.transactions if x['type']!='income' and x['category']!='Income')
  net=income-expenses
  return {'income':round(income,2),'expenses':round(expenses,2),'net':round(net,2),'savings_rate':round(net/income*100,2) if income else 0}
 def detect_recurring(self):
  for merchant,items in self.merchant_groups.items():
   expenses=[x for x in items if x['type']!='income' and x['category']!='Income']
   if len(expenses)<3:continue
   expenses.sort(key=lambda x:x['date_obj'])
   gaps=[(expenses[i]['date_obj']-expenses[i-1]['date_obj']).days for i in range(1,len(expenses))]
   avg_gap=sum(gaps)/len(gaps)
   avg_amount=sum(x['amount'] for x in expenses)/len(expenses)
   if 25<=avg_gap<=35:frequency='monthly'
   elif 6<=avg_gap<=8:frequency='weekly'
   elif 12<=avg_gap<=16:frequency='biweekly'
   elif 365<=avg_gap<=370:frequency='yearly'
   else:continue
   self.recurring.append({'merchant':expenses[0]['merchant'],'frequency':frequency,'average_amount':round(avg_amount,2),'occurrences':len(expenses),'average_gap_days':round(avg_gap,1)})
 def percentile(self,values,p):
  ordered=sorted(values)
  position=(len(ordered)-1)*p
  low=math.floor(position)
  high=math.ceil(position)
  if low==high:return ordered[low]
  return ordered[low]+(ordered[high]-ordered[low])*(position-low)
 def detect_anomalies(self):
  expenses=[x for x in self.transactions if x['type']!='income' and x['category']!='Income']
  amounts=[x['amount'] for x in expenses]
  if len(amounts)>=5:
   q1=self.percentile(amounts,.25);q3=self.percentile(amounts,.75);high=q3+1.5*(q3-q1)
   for item in expenses:
    if item['amount']>high:self.anomalies.append({'date':item['date'],'merchant':item['merchant'],'category':item['category'],'amount':item['amount'],'reason':'Transaction exceeds the overall IQR anomaly threshold.','threshold':round(high,2)})
  groups=defaultdict(list)
  for item in expenses:groups[item['category']].append(item)
  existing={(x['date'],x['merchant'],x['amount']) for x in self.anomalies}
  for category,items in groups.items():
   values=[x['amount'] for x in items]
   if len(values)<4:continue
   mean=sum(values)/len(values)
   sd=math.sqrt(sum((x-mean)**2 for x in values)/len(values))
   if sd==0:continue
   for item in items:
    z=abs((item['amount']-mean)/sd)
    if z>=2.5 and (item['date'],item['merchant'],item['amount']) not in existing:self.anomalies.append({'date':item['date'],'merchant':item['merchant'],'category':category,'amount':item['amount'],'reason':'Category spending is statistically unusual.','z_score':round(z,2)})
 def budget_report(self):
  result={}
  for name,limit in self.budgets.items():
   category=self.normalize_category(name);budget=self.money(limit);spent=self.categories.get(category,0)
   result[category]={'budget':budget,'spent':round(spent,2),'remaining':round(budget-spent,2),'utilization':round(spent/budget*100,2) if budget else 0,'status':'OVER' if spent>budget else 'OK'}
  return result
 def goal_report(self):
  monthly=max(0,self.summary()['net'])
  result={}
  for name,goal in self.goals.items():
   target=self.money(goal.get('target',0));saved=self.money(goal.get('saved',0));remaining=max(0,target-saved);months=math.ceil(remaining/monthly) if remaining and monthly else None
   result[name]={'target':target,'saved':saved,'remaining':round(remaining,2),'progress_percent':round(saved/target*100,2) if target else 0,'estimated_months':months}
  return result
 def report(self):
  self.prepare();summary=self.summary();self.detect_recurring();self.detect_anomalies()
  total_category=sum(self.categories.values())
  return {'summary':summary,'transaction_count':len(self.transactions),'categories':[{'category':k,'spent':round(v,2),'share_percent':round(v/total_category*100,2) if total_category else 0} for k,v in self.categories.most_common()],'top_merchants':[{'merchant':x,'spent':round(sum(i['amount'] for i in self.merchant_groups[x] if i['type']!='income' and i['category']!='Income'),2)} for x in sorted(self.merchant_groups,key=lambda k:sum(i['amount'] for i in self.merchant_groups[k] if i['type']!='income' and i['category']!='Income'),reverse=True)[:10]],'recurring_expenses':self.recurring,'anomalies':self.anomalies,'budgets':self.budget_report(),'goals':self.goal_report()}

def load_csv(path):
 with open(path,'r',encoding='utf-8-sig',newline='') as file:return list(csv.DictReader(file))
def load_json(path):
 data=json.loads(Path(path).read_text(encoding='utf-8'))
 if not isinstance(data,list) or not all(isinstance(x,dict) for x in data):raise ValueError('JSON must contain a list of transaction objects.')
 return data
def load_data(path):
 ext=Path(path).suffix.lower()
 if ext=='.csv':return load_csv(path)
 if ext=='.json':return load_json(path)
 raise ValueError('Supported input formats are CSV and JSON.')
def create_demo(path):
 rows=[['date','merchant','category','amount','type'],['2026-01-01','Company','Income','85000','income'],['2026-01-02','Rent','Housing','18000','expense'],['2026-01-05','Netflix','Entertainment','649','expense'],['2026-02-01','Company','Income','85000','income'],['2026-02-02','Rent','Housing','18000','expense'],['2026-02-05','Netflix','Entertainment','649','expense'],['2026-03-01','Company','Income','85000','income'],['2026-03-02','Rent','Housing','18000','expense'],['2026-03-05','Netflix','Entertainment','649','expense'],['2026-03-08','Electronics Store','Shopping','45000','expense'],['2026-03-12','Fuel','Transport','3000','expense'],['2026-03-18','Restaurant','Food','2200','expense'],['2026-03-25','Restaurant','Food','1800','expense']]
 with open(path,'w',encoding='utf-8',newline='') as file:csv.writer(file).writerows(rows)
def print_report(report):
 s=report['summary'];print('AI PERSONAL FINANCE AGENT');print('='*60);print(f"Transactions: {report['transaction_count']}");print(f"Income: {s['income']:.2f}");print(f"Expenses: {s['expenses']:.2f}");print(f"Net: {s['net']:.2f}");print(f"Savings Rate: {s['savings_rate']:.2f}%")
 print('\nTOP CATEGORIES')
 for x in report['categories'][:10]:print(f"{x['category']}: {x['spent']:.2f} ({x['share_percent']:.2f}%)")
 print('\nRECURRING EXPENSES')
 for x in report['recurring_expenses']:print(f"{x['merchant']}: {x['frequency']} | average {x['average_amount']:.2f} | occurrences {x['occurrences']}")
 print('\nANOMALIES')
 for x in report['anomalies'][:20]:print(f"{x['date']} | {x['merchant']} | {x['amount']:.2f} | {x['reason']}")
 print('\nBUDGETS')
 for k,v in report['budgets'].items():print(f"{k}: {v['spent']:.2f}/{v['budget']:.2f} | {v['status']}")
 print('\nGOALS')
 for k,v in report['goals'].items():print(f"{k}: {v['progress_percent']:.2f}% | remaining {v['remaining']:.2f} | months {v['estimated_months']}")
def main():
 parser=argparse.ArgumentParser(prog='ai_personal_finance_agent');parser.add_argument('file',nargs='?');parser.add_argument('--demo',action='store_true');parser.add_argument('--json',dest='json_file',default='');parser.add_argument('--budget',action='append',default=[]);parser.add_argument('--goal',action='append',default=[]);args=parser.parse_args()
 try:
  if args.demo:path=Path.cwd()/'finance_demo.csv';create_demo(path)
  elif args.file:path=Path(args.file).expanduser().resolve()
  else:path=Path(input('Enter CSV or JSON transaction file: ').strip().strip('"')).expanduser().resolve()
  if not path.exists():raise FileNotFoundError(path)
  budgets={};goals={}
  for item in args.budget:
   name,value=item.split('=',1);budgets[name]=value
  for item in args.goal:
   name,target,saved=item.split(':',2);goals[name]={'target':target,'saved':saved}
  report=FinanceAgent(load_data(path),budgets,goals).report();print_report(report)
  if args.json_file:
   output=Path(args.json_file).expanduser().resolve();output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8');print(f'\nSaved: {output}')
 except Exception as error:
  print(f'ERROR: {error}');raise SystemExit(1)
if __name__=='__main__':main()
