import pycolmap,numpy as np,json
r=pycolmap.Reconstruction('sparse/0');cam=list(r.cameras.values())[0];f,cx,cy,k1=cam.params
M=np.load('map_full.npz');xyz,des,kf=M['xyz'],M['des'],M['kf']
u=np.load('up.npy');floor=-9.74;desk=-3.55;deskH_m=0.71;scale=deskH_m/(desk-floor)  # m per unit (measured desk height 71 cm)
# keep up to 3 descriptors per 3D point, spread over keyframes
key=[tuple(np.round(p,5)) for p in xyz];groups={}
for i,k in enumerate(key):groups.setdefault(k,[]).append(i)
keep=[]
for k,ids in groups.items():
  ids=sorted(ids,key=lambda i:kf[i]);step=max(1,len(ids)//3);keep+=ids[::step][:3]
keep=np.array(sorted(keep));print('entries',len(keep),'points',len(groups))
X=xyz[keep].astype(np.float32);D=des[keep];KF=kf[keep].astype(np.uint16)
ims=sorted(r.images.values(),key=lambda i:i.name);kfs=[]
for im in ims:
  w2c=im.cam_from_world();R=w2c.rotation.matrix();C=-R.T@w2c.translation;kfs.append([*C.round(4),*(R[2]).round(4)])  # center + viewing dir
# desk points (for placement): points within the desk-top band
P=np.array([p.xyz for p in r.points3D.values()]);h=P@u;dp=P[(h>desk-0.15)&(h<desk+0.25)]
meta=dict(name='M13 desk 2026-11-22 (metric)',K=[f,cx,cy],k1=k1,size=[cam.width,cam.height],up=u.tolist(),scale_m_per_unit=scale,deskH=desk,floorH=floor,
  deskCenter=np.median(dp,0).tolist(),n=int(len(X)),keyframes=kfs,orb=dict(n=1500,scale=1.2,levels=8,edge=19,fast=10,longSide=480),assumption='measured desk height 71 cm; check: desk top from map 1.13x0.59 m vs real 1.20x0.60 m')
# point cloud preview subset (colors)
pts=[(p.xyz,p.color) for p in r.points3D.values() if len(p.track.elements)>=4];idx=np.random.default_rng(1).choice(len(pts),min(6000,len(pts)),replace=False)
PC=np.array([pts[i][0] for i in idx],np.float32);CC=np.array([pts[i][1] for i in idx],np.uint8)
with open('map.bin','wb') as fh:
  hdr=json.dumps(meta).encode();fh.write(np.uint32(len(hdr)).tobytes());fh.write(hdr);fh.write(b'\0'*((4-(4+len(hdr))%4)%4))
  fh.write(X.tobytes());fh.write(D.tobytes());fh.write(KF.tobytes());
  if len(KF)%2:fh.write(b'\0\0')
  fh.write(np.uint32(len(PC)).tobytes());fh.write(PC.tobytes());fh.write(CC.tobytes())
import os;print('bytes',os.path.getsize('map.bin'),'scale m/unit',round(scale,4))
