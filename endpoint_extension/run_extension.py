#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, itertools, math, re
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'Source_Reconstructed_Master_44.csv'
METALS=['Fe','Zn','Cu','Cr','Co','Ni','Mn','Pb','Cd']
CANDIDATES=['F','C','Fν','Cν','FC']
MEAS_COUNT={'F':1,'C':1,'Fν':2,'Cν':2,'FC':2}
ORDER={n:i for i,n in enumerate(CANDIDATES)}


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()


def read_rows(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    if not rows: return
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

rows=read_rows(SOURCE)
paired=[r for r in rows if r['Coarse_LF_reconstructed']]
ids=np.array([int(r['Sample']) for r in paired])
blocks=np.array([int(re.search(r'(\d+)$',r['SiteCode']).group(1)) for r in paired])
Y=np.column_stack([np.log10(np.array([float(r[f'{m}_mgkg']) for r in paired])) for m in METALS])
flf=np.array([float(r['Fine_LF_reconstructed']) for r in paired])
fhf=np.array([float(r['Fine_HF_reconstructed']) for r in paired])
clf=np.array([float(r['Coarse_LF_reconstructed']) for r in paired])
chf=np.array([float(r['Coarse_HF_reconstructed']) for r in paired])
ffd=np.array([float(r['Fine_FD_pct']) for r in paired])
cfd=np.array([float(r['Coarse_FD_pct']) for r in paired])
assert len(ids)==43 and len(np.unique(blocks))==10
assert min(flf)>0 and min(fhf)>0 and min(clf)>0 and min(chf)>0


def features(rep):
    d={'F':np.log10(flf)[:,None],'C':np.log10(clf)[:,None],
       'FC':np.c_[np.log10(flf),np.log10(clf)]}
    if rep=='FD':
        d['Fν']=np.c_[np.log10(flf),ffd]; d['Cν']=np.c_[np.log10(clf),cfd]
    else:
        d['Fν']=np.c_[np.log10(flf),np.log10(fhf)]; d['Cν']=np.c_[np.log10(clf),np.log10(chf)]
    return {k:d[k] for k in CANDIDATES}


def fit_predict(X,tr,te):
    mu=X[tr].mean(0); sd=X[tr].std(0); sd=sd.copy(); sd[sd<1e-12]=1.0
    A=np.c_[np.ones(len(tr)),(X[tr]-mu)/sd]; B=np.c_[np.ones(len(te)),(X[te]-mu)/sd]
    return B@np.linalg.lstsq(A,Y[tr],rcond=None)[0]


def order(scores,sids): return np.lexsort((sids,-scores))

def recall(y,p,sids):
    n=len(y); h=k=math.ceil(n/4); hi=set(order(y,sids)[:h]); se=set(order(p,sids)[:k]); hit=len(hi&se)
    return hit/h,hit,h,k


def primary(rep):
    X=features(rep); pred={c:np.full_like(Y,np.nan) for c in CANDIDATES}; out=[]
    for b in sorted(np.unique(blocks)):
        te=np.flatnonzero(blocks==b); tr=np.flatnonzero(blocks!=b)
        for c in CANDIDATES: pred[c][te]=fit_predict(X[c],tr,te)
    for c in CANDIDATES:
        for j,m in enumerate(METALS):
            y=Y[:,j]; p=pred[c][:,j]; e=np.abs(y-p)
            r2=1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)
            bmae=np.mean([e[blocks==b].mean() for b in sorted(np.unique(blocks))])
            rr,hit,h,k=recall(y,p,ids)
            out.append({'Representation':rep,'Metal':m,'Configuration':c,'R2':r2,'Block_MAE':bmae,
                        'Recall_k11':rr,'Hits_k11':hit,'High_n':h,'Budget_k':k})
    return out


def inner_scores(X,outer_train):
    ub=sorted(np.unique(blocks[outer_train])); pairs=list(itertools.combinations(ub,2))
    ma=np.zeros((5,9)); rc=np.zeros((5,9))
    for a,b in pairs:
        te=outer_train[(blocks[outer_train]==a)|(blocks[outer_train]==b)]
        tr=outer_train[(blocks[outer_train]!=a)&(blocks[outer_train]!=b)]
        aa=blocks[te]==a; bb=blocks[te]==b
        for ci,c in enumerate(CANDIDATES):
            p=fit_predict(X[c],tr,te); ae=np.abs(Y[te]-p)
            ma[ci]+=0.5*(ae[aa].mean(0)+ae[bb].mean(0))
            for j in range(9): rc[ci,j]+=recall(Y[te,j],p[:,j],ids[te])[0]
    return ma/len(pairs),rc/len(pairs),len(pairs)


def selectors(ma,rc,tol=1e-12):
    sm=[]; sr=[]; ts=[]; sets=[]
    for j in range(9):
        mv=ma[:,j].min(); cand=[i for i,v in enumerate(ma[:,j]) if v<=mv+tol]
        cand.sort(key=lambda i:(MEAS_COUNT[CANDIDATES[i]],ORDER[CANDIDATES[i]])); sm.append(CANDIDATES[cand[0]])
        rv=rc[:,j].max(); tied=[i for i,v in enumerate(rc[:,j]) if v>=rv-tol]
        ts.append(len(tied)); sets.append('|'.join(CANDIDATES[i] for i in tied))
        best=min(ma[i,j] for i in tied); t2=[i for i in tied if ma[i,j]<=best+tol]
        t2.sort(key=lambda i:(MEAS_COUNT[CANDIDATES[i]],ORDER[CANDIDATES[i]])); sr.append(CANDIDATES[t2[0]])
    return sm,sr,ts,sets


def experiment(rep,deleted=0):
    X=features(rep); use=np.arange(len(ids)) if deleted==0 else np.flatnonzero(blocks!=deleted); ub=sorted(np.unique(blocks[use])); out=[]
    for a,b in itertools.combinations(ub,2):
        te=use[(blocks[use]==a)|(blocks[use]==b)]; tr=use[(blocks[use]!=a)&(blocks[use]!=b)]
        ma,rc,npairs=inner_scores(X,tr); sm,sr,ts,sets=selectors(ma,rc); pred={c:fit_predict(X[c],tr,te) for c in CANDIDATES}
        aa=blocks[te]==a; bb=blocks[te]==b
        for j,m in enumerate(METALS):
            cm,cr=sm[j],sr[j]; rm,hm,h,k=recall(Y[te,j],pred[cm][:,j],ids[te]); rr,hr,_,_=recall(Y[te,j],pred[cr][:,j],ids[te])
            em=np.abs(Y[te,j]-pred[cm][:,j]); er=np.abs(Y[te,j]-pred[cr][:,j])
            out.append({'Representation':rep,'Deleted_Block':deleted,'Outer_Block_A':a,'Outer_Block_B':b,'Test_n':len(te),'Metal':m,
                        'S_MAE':cm,'S_REC':cr,'Inner_MAE_of_S_MAE':ma[CANDIDATES.index(cm),j],
                        'Inner_Recovery_of_S_MAE':rc[CANDIDATES.index(cm),j],'Inner_MAE_of_S_REC':ma[CANDIDATES.index(cr),j],
                        'Inner_Recovery_of_S_REC':rc[CANDIDATES.index(cr),j],'Recovery_Primary_Tie_Size':ts[j],
                        'Recovery_Primary_Tied_Set':sets[j],'Outer_Recall_S_MAE':rm,'Outer_Recall_S_REC':rr,'Delta_Recall':rr-rm,
                        'Outer_Hits_S_MAE':hm,'Outer_Hits_S_REC':hr,'High_n':h,'Budget_k':k,
                        'Outer_BlockMAE_S_MAE':0.5*(em[aa].mean()+em[bb].mean()),
                        'Outer_BlockMAE_S_REC':0.5*(er[aa].mean()+er[bb].mean()),
                        'Delta_BlockMAE_REC_minus_MAE':0.5*(er[aa].mean()+er[bb].mean()-em[aa].mean()-em[bb].mean()),'Inner_Pairs':npairs})
    return out

fixed={rep:primary(rep) for rep in ['FD','logHF']}
central={rep:experiment(rep) for rep in ['FD','logHF']}
delete=[r for rep in ['FD','logHF'] for b in sorted(np.unique(blocks)) for r in experiment(rep,int(b))]

summary=[]
for rep in ['FD','logHF']:
    for m in METALS:
        x=[r for r in central[rep] if r['Metal']==m]; d=np.array([r['Delta_Recall'] for r in x])
        summary.append({'Representation':rep,'Metal':m,'Outer_Batches':45,
                        'Mean_Recall_S_MAE':np.mean([r['Outer_Recall_S_MAE'] for r in x]),
                        'Mean_Recall_S_REC':np.mean([r['Outer_Recall_S_REC'] for r in x]),'Mean_Delta_Recall':d.mean(),
                        'Median_Delta_Recall':np.median(d),'Wins_REC':int(np.sum(d>1e-15)),'Ties':int(np.sum(np.abs(d)<=1e-15)),
                        'Losses_REC':int(np.sum(d<-1e-15)),'RecoverySelection_Differs_from_MAE':sum(r['S_MAE']!=r['S_REC'] for r in x)})

bydel=[]
for rep in ['FD','logHF']:
    for b in sorted(np.unique(blocks)):
        for m in METALS:
            x=[r for r in delete if r['Representation']==rep and r['Deleted_Block']==b and r['Metal']==m]
            bydel.append({'Representation':rep,'Deleted_Block':b,'Metal':m,'Mean_Delta_Recall':np.mean([r['Delta_Recall'] for r in x])})
rob=[]
for rep in ['FD','logHF']:
    for m in METALS:
        v=np.array([r['Mean_Delta_Recall'] for r in bydel if r['Representation']==rep and r['Metal']==m])
        rob.append({'Representation':rep,'Metal':m,'DeleteBlock_Min_MeanDelta':v.min(),'DeleteBlock_Max_MeanDelta':v.max(),
                    'DeleteBlock_Median_MeanDelta':np.median(v),'Positive_Deletes':int(np.sum(v>1e-12)),
                    'Zero_Deletes':int(np.sum(np.abs(v)<=1e-12)),'Negative_Deletes':int(np.sum(v<-1e-12))})

write_csv(ROOT/'Selector_OuterPairs.csv',central['FD']+central['logHF'])
write_csv(ROOT/'Selector_Summary.csv',summary)
write_csv(ROOT/'DeleteBlock_ByDeletion.csv',bydel)
write_csv(ROOT/'DeleteBlock_Robustness.csv',rob)
write_csv(ROOT/'Fixed_FD.csv',fixed['FD'])
write_csv(ROOT/'Fixed_logHF.csv',fixed['logHF'])
print('PASS',len(paired),'paired rows',len(central['FD'])+len(central['logHF']),'central metal-batch records',len(delete),'delete-block records')

# Derived summaries used by the manuscript/audit package.
counts=[]
for rep in ['FD','logHF']:
    for m in METALS:
        x=[r for r in central[rep] if r['Metal']==m]
        for selector in ['S_MAE','S_REC']:
            cc=Counter(r[selector] for r in x)
            counts.append({'Representation':rep,'Metal':m,'Selector':selector,
                           **{c:int(cc.get(c,0)) for c in CANDIDATES}})
write_csv(ROOT/'Selection_Counts.csv',counts)

# Representation-to-representation selection stability on matched outer batches.
stab=[]
for m in METALS:
    a=sorted([r for r in central['FD'] if r['Metal']==m],key=lambda z:(z['Outer_Block_A'],z['Outer_Block_B']))
    b=sorted([r for r in central['logHF'] if r['Metal']==m],key=lambda z:(z['Outer_Block_A'],z['Outer_Block_B']))
    assert [(r['Outer_Block_A'],r['Outer_Block_B']) for r in a]==[(r['Outer_Block_A'],r['Outer_Block_B']) for r in b]
    stab.append({'Metal':m,
                 'S_MAE_config_diff_batches':sum(x['S_MAE']!=y['S_MAE'] for x,y in zip(a,b)),
                 'S_REC_config_diff_batches':sum(x['S_REC']!=y['S_REC'] for x,y in zip(a,b)),
                 'S_MAE_outer_recall_diff_batches':sum(abs(float(x['Outer_Recall_S_MAE'])-float(y['Outer_Recall_S_MAE']))>1e-15 for x,y in zip(a,b)),
                 'S_REC_outer_recall_diff_batches':sum(abs(float(x['Outer_Recall_S_REC'])-float(y['Outer_Recall_S_REC']))>1e-15 for x,y in zip(a,b)),
                 'MeanDelta_FD':np.mean([r['Delta_Recall'] for r in a]),
                 'MeanDelta_logHF':np.mean([r['Delta_Recall'] for r in b])})
write_csv(ROOT/'Representation_Selection_Stability.csv',stab)

# Fixed-model representation sensitivity for the two frequency-aware configurations.
fr=[]
for m in METALS:
    for c in ['Fν','Cν']:
        a=next(r for r in fixed['FD'] if r['Metal']==m and r['Configuration']==c)
        b=next(r for r in fixed['logHF'] if r['Metal']==m and r['Configuration']==c)
        fr.append({'Metal':m,'Configuration':c,
                   'FD_R2':a['R2'],'logHF_R2':b['R2'],'Delta_R2_logHF_minus_FD':b['R2']-a['R2'],
                   'FD_BlockMAE':a['Block_MAE'],'logHF_BlockMAE':b['Block_MAE'],
                   'Delta_BlockMAE_logHF_minus_FD':b['Block_MAE']-a['Block_MAE'],
                   'FD_Hits_k11':a['Hits_k11'],'logHF_Hits_k11':b['Hits_k11']})
write_csv(ROOT/'Fixed_Representation_Sensitivity.csv',fr)

# Condition numbers after training-set standardization in the ten primary folds.
cond=[]
for rep in ['FD','logHF']:
    X=features(rep)
    for c in ['Fν','Cν']:
        vv=[]
        for b in sorted(np.unique(blocks)):
            tr=np.flatnonzero(blocks!=b)
            mu=X[c][tr].mean(0); sd=X[c][tr].std(0); sd=sd.copy(); sd[sd<1e-12]=1.0
            A=np.c_[np.ones(len(tr)),(X[c][tr]-mu)/sd]
            vv.append(float(np.linalg.cond(A)))
        cond.append({'Representation':rep,'Configuration':c,
                     'Condition_Min':min(vv),'Condition_Median':float(np.median(vv)),'Condition_Max':max(vv)})
write_csv(ROOT/'Representation_Conditioning.csv',cond)

# Numerical reproduction anchors from the locked V11R2/public central results.
locked={
 ('Fe','F'):{'R2':0.03283064541809344,'Block_MAE':0.17470615865416136},
 ('Cr','Cν'):{'R2':0.3434805277510792,'Block_MAE':0.09466061350480734},
 ('Mn','FC'):{'R2':0.4054977418187876,'Block_MAE':0.1161826732903406},
 ('Cu','FC'):{'R2':0.48750181366204115,'Block_MAE':0.12133750009875095},
}
anchors=[]
for (m,c),metrics in locked.items():
    got=next(r for r in fixed['FD'] if r['Metal']==m and r['Configuration']==c)
    for metric,expected in metrics.items():
        anchors.append({'Metal':m,'Configuration':c,'Metric':metric,
                        'Absolute_Difference':abs(float(got[metric])-expected)})
write_csv(ROOT/'Reproduction_Anchor_Differences.csv',anchors)
