"""Anonymous final reflection; original answers and law results remain intact."""
import secrets
OPTIONS=['Conocer nuevos antecedentes','Escuchar un buen argumento','Encontrar una propuesta mejor','Todavía no lo sé']
def summary(s):
 answers=[p.get('closingChoice') for p in s['people'].values()]
 return {'options':OPTIONS,'counts':[answers.count(i) for i in range(4)],'answered':sum(v is not None for v in answers),'total':len(answers)}
def act(s,token,command,choice=None):
 if command in ['open','finish']:
  if token!=s['host']:raise ValueError('Solo el moderador dirige el cierre')
  if command=='open':
   if s['phase']!='results':raise ValueError('Termina las votaciones antes de abrir la reflexión')
   s['phase']='closing'
   for key,p in s['people'].items():
    if key.startswith('bot-'):p['closingChoice']=secrets.randbelow(4)
   if s.get('bots'):s['bots']['running']=False
  else:
   if s['phase']!='closing':raise ValueError('Abre primero la reflexión final')
   s['phase']='farewell'
 elif command=='answer':
  if s['phase']!='closing' or token not in s['people']:raise ValueError('La reflexión no está abierta')
  if type(choice)!=int or choice not in range(4):raise ValueError('Elige una de las cuatro respuestas')
  s['people'][token]['closingChoice']=choice
 else:raise ValueError('Acción de cierre no válida')
