import time
OPTIONS={
 'universal':{'title':'Pase gratuito para todos los estudiantes','proposal':'Todos los estudiantes viajan gratis en transporte público.','funding':'Se financia con recursos del presupuesto público provenientes de impuestos.','tradeoff':'Requiere más recursos públicos; hay que decidir cuánto destinar y cómo organizarlo.'},
 'targeted':{'title':'Pase gratuito para estudiantes con menos recursos','proposal':'La gratuidad se dirige a estudiantes de hogares con menores ingresos.','funding':'Usa presupuesto público, con una cobertura menor que la propuesta universal.','tradeoff':'Requiere un mecanismo de acceso y deja a otros estudiantes pagando su pasaje.'},
 'discount':{'title':'Pasaje a mitad de precio para todos los estudiantes','proposal':'Cada estudiante paga la mitad del pasaje.','funding':'El presupuesto público cubre la otra mitad.','tradeoff':'Reduce el aporte público respecto de la gratuidad total, pero el viaje sigue teniendo un costo para el estudiante.'}}
def setup(s):
 s['legislation']={'version':'universal','ballot':1,'history':[]};s['law']=OPTIONS['universal']['proposal']+' '+OPTIONS['universal']['funding']
def close(s):
 if s['phase']=='crisisvote':
  c=s['crisis'];votes=[p['vote'] for p in s['people'].values()];c['votes']={k:votes.count(k) for k in ['yes','no','abstain']};c['pending']=votes.count(None);c['removed']=votes.count('yes')>=c['threshold'];s['phase']='crisisresult';s['announcedAt']=time.time()
  if s.get('bots'):s['bots']['running']=False
  return
 if s.get('legislation'):
  l=s['legislation'];votes=[p['vote'] for p in s['people'].values()];n=len(votes)
  l['history'].append({'ballot':l['ballot'],'version':l['version'],'votes':{k:votes.count(k) for k in ['yes','no','abstain']},'pending':votes.count(None),'majority':votes.count('no')+1,'rule':'simple','approved':votes.count('yes')>votes.count('no')})
  s['phase']='negotiation' if l['ballot']==1 and not l['history'][-1]['approved'] else 'results'
 else:s['phase']='results'
 s['announcedAt']=time.time()
 if s.get('bots'):
  s['bots']['phaseSince']=time.time()
  if s['phase']=='negotiation':s['bots']['running']=False
def amend(s,key):
 if s.get('crisis',{}).get('active'):raise ValueError('Termina la emergencia antes de modificar el proyecto')
 if not s.get('legislation',{}).get('history') or s['legislation']['history'][0]['approved']:raise ValueError('Un proyecto aprobado no necesita modificación')
 if s['phase']!='negotiation' or key not in ['targeted','discount']:raise ValueError('Elige una modificación durante la negociación')
 s['legislation']['version']=key;s['legislation']['ballot']=2;s['law']=OPTIONS[key]['proposal']+' '+OPTIONS[key]['funding']
 for p in s['people'].values():p['vote']=None
 s['phase']='vote2'
 if s.get('bots'):s['bots']['running']=True

def crisis_action(s,command):
 if command=='start' and s['phase'] in ['negotiation','results'] and not s.get('crisis'):
  n=len(s['people'])
  if not n:raise ValueError('Se necesitan participantes')
  s['crisis']={'active':True,'returnPhase':s['phase'],'threshold':(2*n+2)//3,'savedVotes':{k:p['vote'] for k,p in s['people'].items()}}
  s['phase']='crisisdiscussion';s['announcedAt']=time.time()
  if s.get('bots'):s['bots']['running']=False
 elif command=='vote' and s['phase']=='crisisdiscussion':
  for p in s['people'].values():p['vote']=None
  s['phase']='crisisvote'
  if s.get('bots'):s['bots']['running']=True
 elif command=='close' and s['phase']=='crisisvote':close(s)
 elif command=='resume' and s['phase']=='crisisresult':
  for k,p in s['people'].items():p['vote']=s['crisis']['savedVotes'][k]
  s['crisis']['active']=False;s['phase']=s['crisis']['returnPhase']
 else:raise ValueError('La etapa de la emergencia ya cambió')
