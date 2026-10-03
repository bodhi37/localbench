"""Independent re-derivation: defer evaluation by recording, per (bin,sku), an
ordered list of operations (add/set) in global event order, then fold each key
from its INITIAL value. No mutable global state during replay."""
import json
R="../resources/warehouse_events.log"
init={}; evs=[]
for ln in open(R):
    t=ln.split()
    if not t or not (t[0]=="INITIAL" or t[0].isdigit()): continue
    if t[0]=="INITIAL": init[(t[1],t[2])]=int(t[3])
    else: evs.append((int(t[0]),t[1],t[2:]))
ops={}
def push(k,op): ops.setdefault(k,[]).append(op)
applied={}; voided=set(); eff=0
for seq,op,a in evs:
    if op=="VOID":
        t=int(a[0]); tgt=applied.get(t)
        if tgt is None or t in voided or tgt[0]=="RECOUNT": continue
        o2,a2=tgt
        if o2=="RECEIVE": push((a2[0],a2[1]),("add",-int(a2[2])))
        elif o2=="PICK": push((a2[0],a2[1]),("add",+int(a2[2])))
        else:
            push((a2[0],a2[2]),("add",+int(a2[3]))); push((a2[1],a2[2]),("add",-int(a2[3])))
        voided.add(t); eff+=1
    elif op=="RECEIVE": push((a[0],a[1]),("add",int(a[2]))); applied[seq]=(op,a)
    elif op=="PICK": push((a[0],a[1]),("add",-int(a[2]))); applied[seq]=(op,a)
    elif op=="TRANSFER":
        push((a[0],a[2]),("add",-int(a[3]))); push((a[1],a[2]),("add",int(a[3]))); applied[seq]=(op,a)
    elif op=="RECOUNT": push((a[0],a[1]),("set",int(a[2]))); applied[seq]=(op,a)
    else: raise SystemExit("bad op %r"%op)

def fold(key):
    v=init.get(key,0)
    for kind,n in ops.get(key,[]):
        v = n if kind=="set" else v+n
    return v
final={b: fold((b,"NX-4471")) for b in ["A-01","A-02","B-07"]}
init_total=sum(q for (b,s),q in init.items() if s=="NX-4471")
res={"final_bins":final,"effective_voids":eff,"net_change":sum(final.values())-init_total}
exp=json.load(open("expected.json"))
print(json.dumps(res,indent=2))
print("independent ordered-fold replay matches expected.json:", res==exp)
