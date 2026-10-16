"""Synthetic participants for a separate demonstration server. No real students."""
import random, time, secrets
import legislation
RNG=random.SystemRandom()
def configure(s,count,speed,avatars):
 if s.get('bots'):raise ValueError('Los bots ya están configurados')
 if len(s['people'])+count>300:raise ValueError('Sesión completa')
 tokens=[];pool=list(avatars);RNG.shuffle(pool)
 for i in range(count):
  token='bot-'+secrets.token_hex(8);tokens.append(token)
  s['people'][token]={'avatar':pool[i%len(pool)],'initial':round(RNG.uniform(-3,3),2),'answers':[None]*10,'vote':None,'botLean':RNG.uniform(-1,1)}
 s['bots']={'tokens':tokens,'running':False,'speed':speed,'lastTick':0,'phaseSince':time.time(),'events':0}
def change_phase(s,phase):
 s['phase']=phase;s['bots']['phaseSince']=time.time()
 if phase in ['count1','count2','results']:s['announcedAt']=time.time()
def step(s,force=False):
 cfg=s.get('bots')
 if not cfg or s['phase']=='results':
  if cfg:cfg['running']=False
  return False
 if s['phase']=='lobby':
  if s.get('mixed') and not force:return False
  change_phase(s,'round1')
 elif s['phase'] in ['round1','round2']:
  start=0 if s['phase']=='round1' else 5
  pending=[s['people'][t] for t in cfg['tokens'] if any(v is None for v in s['people'][t]['answers'][start:start+5])]
  if not pending and any(any(v is None for v in p['answers'][start:start+5]) for p in s['people'].values()):return False
  if pending:
   p=RNG.choice(pending);i=next(i for i in range(start,start+5) if p['answers'][i] is None);q=s['questions'][i]
   p['answers'][i]=9 if RNG.random()<.12 else 0 if RNG.random()<.15 else RNG.choice([1,2])*(q['direction'] if RNG.random()<(p['botLean']+1)/2 else -q['direction'])
  if all(all(v is not None for v in p['answers'][start:start+5]) for p in s['people'].values()):change_phase(s,'count1' if start==0 else 'count2')
 elif s['phase'] in ['count1','count2']:
  if s.get('mixed') and not force:return False
  if not force and time.time()-cfg['phaseSince']<5:return False
  change_phase(s,'round2' if s['phase']=='count1' else 'vote')
 elif s['phase'] in ['negotiation','crisisdiscussion','crisisresult']:return False
 elif s['phase'] in ['vote','vote2','crisisvote']:
  pending=[s['people'][t] for t in cfg['tokens'] if s['people'][t]['vote'] is None]
  if not pending and any(p['vote'] is None for p in s['people'].values()):return False
  if pending:
   p=RNG.choice(pending);lean=p['botLean'];version=s.get('legislation',{}).get('version','universal')
   support=(.55-.25*lean) if version=='universal' else (.68-.08*lean) if version=='targeted' else (.60+.12*lean)
   if s['phase']=='crisisvote':support=.58
   p['vote']='abstain' if RNG.random()<.1 else ('yes' if RNG.random()<support else 'no')
  if all(p['vote'] is not None for p in s['people'].values()):legislation.close(s)
  if s['phase']=='results':cfg['running']=False
 cfg['events']+=1;s['revision']+=1;return True
