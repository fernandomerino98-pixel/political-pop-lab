import json, os, time, secrets, threading, io, math
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import bots, legislation, closing
ROOT=Path(__file__).parent
LOCK=threading.RLock(); SESSIONS={}
PHASES=['lobby','round1','count1','round2','count2','vote','results']
AVATARS=[p['name'] for p in json.loads((ROOT/'public'/'catalog.json').read_text())]
QUESTION_BANK=json.loads((ROOT/'question-bank.json').read_text())
HISTORY_PATH=ROOT/'.question-history.json'
def select_questions():
 history=json.loads(HISTORY_PATH.read_text()) if HISTORY_PATH.exists() else []
 used={tuple(ids) for ids in history};rng=secrets.SystemRandom()
 topics=list(dict.fromkeys(q['topic'] for q in QUESTION_BANK))
 for attempt in range(10000):
  directions=[-1]*5+[1]*5;rng.shuffle(directions)
  chosen=[rng.choice([q for q in QUESTION_BANK if q['topic']==t and q['direction']==d]) for t,d in zip(topics,directions)]
  rng.shuffle(chosen);ids=tuple(q['id'] for q in chosen)
  if ids not in used:
   history.append(list(ids));temporary=HISTORY_PATH.with_suffix('.tmp');temporary.write_text(json.dumps(history));temporary.replace(HISTORY_PATH);return chosen
 raise ValueError('No se pudo seleccionar una secuencia nueva. Revisa el historial del banco.')
def position(p,n,questions):
 a=p['answers'][:n]; vals=[v*questions[i]['direction'] for i,v in enumerate(a) if v is not None and v!=9]
 return round(1.5*sum(vals)/len(vals),2) if vals else None

def snapshot(s, pid=None, host=False):
 ps=list(s['people'].values()); n=5 if s['phase'] in ['lobby','round1','count1','round2'] else 10
 out={'code':s['code'],'phase':s['phase'],'count':len(ps),'majority':len(ps)//2+1 if ps else 0,'ready':sum(all(v is not None for v in p['answers'][:(5 if s['phase'] in ['round1','count1'] else 10)]) for p in ps),'questions':[q['text'] for q in s['questions']],'questionDetails':s['questions'],'avatars':AVATARS,'law':s['law'],'revision':s['revision'],'announcedAt':s.get('announcedAt',0)}
 out['seats']=[{'number':i+1,'avatar':p['avatar'],'position':position(p,n,s['questions']) if s['phase'] not in ['lobby','round1'] else None} for i,p in enumerate(ps)]
 votes=[p['vote'] for p in ps]; out['votes']={v:votes.count(v) for v in ['yes','no','abstain']};out['voted']=sum(v is not None for v in votes)
 if host and s.get('bots'):out['simulation']={k:v for k,v in s['bots'].items() if k not in ['tokens','lastTick','phaseSince']};out['simulation']['count']=len(s['bots']['tokens'])
 if host:out['voterStatus']=[{'number':i+1,'avatar':p['avatar'],'voted':p['vote'] is not None} for i,p in enumerate(ps)]
 if host and s['phase'] in ['negotiation','results']:
  out['blocVotes']={k:{'yes':0,'no':0,'abstain':0,'pending':0} for k in ['left','center','right','unknown']}
  for p in ps:
   score=position(p,10,s['questions']);key='unknown' if score is None else 'left' if score<-.7 else 'right' if score>.7 else 'center'
   out['blocVotes'][key][p['vote'] or 'pending']+=1
 if pid in s['people']: out['mySeat']=list(s['people']).index(pid)+1;out['me']={**s['people'][pid],'final':position(s['people'][pid],10,s['questions']),'provisional':position(s['people'][pid],5,s['questions'])}
 out['closing']=closing.summary(s)
 out['crisis']={k:v for k,v in s.get('crisis',{}).items() if k!='savedVotes'}
 out['mixed']=s.get('mixed',False)
 out['humans']=sum(not k.startswith('bot-') for k in s['people']);out['botCount']=len(ps)-out['humans']
 if host:out['viewToken']=s.get('view')
 if s.get('legislation'):out['legislation']={**s['legislation'],'options':legislation.OPTIONS}
 return out
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def send(self,data,status=200,kind='application/json'):
  b=json.dumps(data,ensure_ascii=False).encode() if kind=='application/json' else data
  self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path); q=parse_qs(u.query)
  if u.path=='/healthz':return self.send({'status':'ok'})
  if u.path=='/api/state':
   with LOCK:
    s=SESSIONS.get(q.get('code',[''])[0]);
    if not s or time.time()-s['created']>14400:return self.send({'error':'Sesión no disponible. Pide un nuevo código.'},404)
    token=q.get('token',[''])[0]
    if token!=s['host'] and token!=s.get('view') and token not in s['people']:return self.send({'error':'Acceso no válido.'},403)
    result=snapshot(s,token,token==s['host'])
    if token==s.get('view'):
     # Projection carries no avatar names or participant seat identifiers.
     scores=sorted((seat['position'] for seat in result['seats']),key=lambda v:(v is None,v or 0))
     result['seats']=[{'number':i+1,'position':score} for i,score in enumerate(scores)]
    return self.send(result)
  if u.path=='/qr.svg':
   try:
    import qrcode, qrcode.image.svg
    target=q.get('url',[''])[0]
    if len(target)>500:raise ValueError()
    img=qrcode.make(target,image_factory=qrcode.image.svg.SvgPathImage);buf=io.BytesIO();img.save(buf);return self.send(buf.getvalue(),kind='image/svg+xml')
   except Exception:return self.send(b'QR no disponible: usa el enlace y el codigo.',503,'text/plain')
  f=ROOT/'public'/('index.html' if u.path=='/' else u.path.lstrip('/'))
  if (ROOT/'public').resolve() not in f.resolve().parents or not f.is_file():return self.send({'error':'No encontrado'},404)
  return self.send(f.read_bytes(),kind={'html':'text/html','js':'text/javascript','css':'text/css','png':'image/png','jpg':'image/jpeg','webp':'image/webp','m4a':'audio/mp4','json':'application/json'}.get(f.suffix[1:],'text/plain'))
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length',0))
   if size>8192:raise ValueError('Solicitud demasiado grande')
   d=json.loads(self.rfile.read(size)); action=urlparse(self.path).path
   with LOCK:
    now=time.time()
    for c in list(SESSIONS):
     if now-SESSIONS[c]['created']>14400:del SESSIONS[c]
    if action=='/api/create':
     if len(SESSIONS)>=100:raise ValueError('Capacidad de sesiones alcanzada')
     code=''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(6))
     while code in SESSIONS:code=secrets.token_hex(3).upper()
     s={'code':code,'host':secrets.token_urlsafe(24),'view':secrets.token_urlsafe(24),'mixed':bool(d.get('mixed')), 'people':{},'questions':select_questions(),'phase':'lobby','revision':0,'created':now,'law':'Proyecto ficticio: ofrecer un pase de transporte público gratuito a estudiantes, financiado con recursos públicos.'};SESSIONS[code]=s
     if d.get('legislative'):legislation.setup(s)
     return self.send({'code':code,'token':s['host'],'viewToken':s['view'],'mixed':s['mixed']})
    s=SESSIONS.get(str(d.get('code','')).upper())
    if not s:raise ValueError('Sesión no disponible')
    token=d.get('token');p=s['people'].get(token)
    if action=='/api/join':
     if s.get('bots') and not s.get('mixed'):raise ValueError('Esta sesión es de bots. Crea una sesión mixta para participar.')
     if s['phase']!='lobby':raise ValueError('El ingreso está cerrado. Espera la próxima sesión.')
     if len(s['people'])>=300:raise ValueError('Sesión completa')
     avatar=d.get('avatar');initial=d.get('initial')
     if avatar not in AVATARS or (initial is not None and (type(initial) not in (int,float) or not math.isfinite(initial) or not -3<=initial<=3)):raise ValueError('Selección no válida')
     token=secrets.token_urlsafe(24);s['people'][token]={'avatar':avatar,'initial':initial,'answers':[None]*10,'vote':None};s['revision']+=1
     return self.send({'token':token,'code':s['code']})
    if action=='/api/closing':
     closing.act(s,token,d.get('command'),d.get('choice'));s['revision']+=1;return self.send({'ok':True})
    if action=='/api/amend':
     if token!=s['host']:return self.send({'error':'Solo el anfitrión modifica el proyecto'},403)
     legislation.amend(s,d.get('option'));s['revision']+=1;return self.send({'ok':True})
    if action=='/api/bots':
     if token!=s['host']:return self.send({'error':'Solo el anfitrión controla los bots'},403)
     command=d.get('command')
     if not s.get('bots'):
      count=d.get('count',24);speed=d.get('speed',.25)
      if type(count)!=int or not 1<=count<=120 or type(speed) not in (int,float) or not .05<=speed<=3:raise ValueError('Cantidad o velocidad no válida')
      bots.configure(s,count,speed,AVATARS)
     if command=='start':s['bots']['running']=True
     elif command=='pause':s['bots']['running']=False
     elif command=='step':
      s['bots']['running']=False;bots.step(s,True)
     else:raise ValueError('Acción de simulación no válida')
     s['revision']+=1;return self.send({'ok':True})
    if action=='/api/crisis':
     if token!=s['host']:raise ValueError('Solo el anfitrión controla la emergencia')
     legislation.crisis_action(s,d.get('command'));s['revision']+=1;return self.send({'ok':True})
    if action=='/api/host':
     if token!=s['host']:return self.send({'error':'Solo el anfitrión puede controlar la sesión'},403)
     cmd=d.get('command')
     if cmd=='next':
      if d.get('phase') and d['phase']!=s['phase']:raise ValueError('La etapa ya cambió. Actualiza la pantalla.')
      if s.get('legislation') and s['phase'] in ['vote','vote2']:
       legislation.close(s);s['revision']+=1;return self.send({'ok':True})
      if s['phase']=='negotiation':raise ValueError('Selecciona una modificación del proyecto')
      i=PHASES.index(s['phase'])
      if i==len(PHASES)-1:raise ValueError('La sesión terminó')
      if d.get('phase') and d['phase']!=s['phase']:raise ValueError('La etapa ya cambió. Actualiza la pantalla.')
      s['phase']=PHASES[i+1]
      if s['phase']=='vote' and s['people'] and all(x['vote'] is not None for x in s['people'].values()):s['phase']='results'
      if s['phase'] in ['count1','count2','results']:s['announcedAt']=now
     elif cmd=='delete':del SESSIONS[s['code']];return self.send({'deleted':True})
     elif cmd=='demo':
      if s['phase']!='lobby':raise ValueError('El ensayo se agrega antes de comenzar')
      for i in range(24):s['people']['demo-'+str(i)]={'avatar':AVATARS[i%len(AVATARS)],'initial':i%7-3,'answers':[[-1,0,1][(i+j*2)%3] for j in range(10)],'vote':['yes','no','abstain'][i%3]}
     else:raise ValueError('Acción no válida')
    elif action=='/api/answer':
     if not p:raise ValueError('Acceso no válido')
     start=0 if s['phase']=='round1' else 5 if s['phase']=='round2' else None
     a=d.get('answers')
     if start is None or not isinstance(a,list) or len(a)!=5 or any(type(v)!=int or v not in [-2,-1,0,1,2,9] for v in a):raise ValueError('La ronda no está abierta o faltan respuestas')
     p['answers'][start:start+5]=a
    elif action=='/api/reflection':
     revised=d.get('revisedInitial')
     if not p or s['phase']!='results':raise ValueError('La reflexión se abre al terminar la actividad')
     if revised is not None and (type(revised) not in (int,float) or not math.isfinite(revised) or not -3<=revised<=3):raise ValueError('Posición no válida')
     p['revisedInitial']=revised;p['reflectionSaved']=True
    elif action=='/api/vote':
     if not p or s['phase'] not in ['vote','vote2','crisisvote'] or d.get('vote') not in ['yes','no','abstain']:raise ValueError('Votación no disponible')
     p['vote']=d['vote']
     if s['people'] and all(x['vote'] is not None for x in s['people'].values()):
      legislation.close(s)
    else:raise ValueError('Ruta no válida')
    s['revision']+=1;return self.send({'ok':True})
  except (ValueError,TypeError,KeyError) as e:self.send({'error':str(e)},400)
def expire_sessions():
 while True:
  time.sleep(15)
  with LOCK:
   for code in list(SESSIONS):
    if time.time()-SESSIONS[code]['created']>=14400:del SESSIONS[code]

def run_bots():
 while True:
  time.sleep(.05)
  with LOCK:
   for s in list(SESSIONS.values()):
    cfg=s.get('bots')
    if cfg and cfg['running'] and time.time()-cfg['lastTick']>=cfg['speed']:
     cfg['lastTick']=time.time();bots.step(s)

if __name__=='__main__':
 threading.Thread(target=expire_sessions,daemon=True).start()
 threading.Thread(target=run_bots,daemon=True).start()
 port=int(os.environ.get('PORT','8002'));print('Political Pop Lab · Bots: http://localhost:'+str(port),flush=True);ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
