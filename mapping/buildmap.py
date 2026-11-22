import pycolmap,numpy as np,cv2,json,sys
r=pycolmap.Reconstruction('sparse/0');cam=list(r.cameras.values())[0]
f,cx,cy,k1=cam.params;W0,H0=cam.width,cam.height
S=480/max(W0,H0);w,h=round(W0*S),round(H0*S)
orb=cv2.ORB_create(2000,1.2,8,19,0,2,cv2.ORB_HARRIS_SCORE,31,10);clahe=cv2.createCLAHE(2.5,(8,8))
ims=sorted(r.images.values(),key=lambda i:i.name)
def feats(im):
  g=cv2.cvtColor(cv2.resize(cv2.imread('imgs/'+im.name),(w,h),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY);g=clahe.apply(g)
  kp,des=orb.detectAndCompute(g,None);return kp,des
def assoc(im,kp,des):
  obs=[(p.xy*S,p.point3D_id) for p in im.points2D if p.has_point3D()]
  if not obs or des is None:return []
  O=np.array([o[0] for o in obs]);ids=[o[1] for o in obs];out=[]
  for k,dsc in zip(kp,des):
    dd=np.linalg.norm(O-np.array(k.pt),axis=1);j=dd.argmin()
    if dd[j]<2.5:out.append((ids[j],dsc))
  return out
mode=sys.argv[1] if len(sys.argv)>1 else 'full'
mapIms=ims if mode=='full' else ims[0::2]
pid2=[];D=[];kfid=[]
for ki,im in enumerate(mapIms):
  kp,des=feats(im)
  for pid,dsc in assoc(im,kp,des):pid2.append(pid);D.append(dsc);kfid.append(ki)
P3={pid:r.points3D[pid].xyz for pid in set(pid2)}
XYZ=np.array([P3[p] for p in pid2],np.float32);D=np.array(D,np.uint8);KF=np.array(kfid,np.int16)
print(mode,'map entries',len(D),'unique 3D',len(P3),'keyframes',len(mapIms))
np.savez(f'map_{mode}.npz',xyz=XYZ,des=D,kf=KF)
if mode=='half':
  K=np.array([[f*S,0,cx*S],[0,f*S,cy*S],[0,0,1]]);dist=np.array([k1,0,0,0])
  bf=cv2.BFMatcher(cv2.NORM_HAMMING);errs=[];inls=[];fails=0
  for im in ims[1::2]:
    kp,des=feats(im);m=bf.knnMatch(des,D,k=2);good=[a for a,b in m if a.distance<0.8*b.distance]
    if len(good)<12:fails+=1;continue
    p2=np.float32([kp[g.queryIdx].pt for g in good]);p3=XYZ[[g.trainIdx for g in good]]
    ok,rv,tv,inl=cv2.solvePnPRansac(p3,p2,K,dist,iterationsCount=300,reprojectionError=4.0,flags=cv2.SOLVEPNP_SQPNP)
    if not ok or inl is None or len(inl)<12:fails+=1;continue
    R,_=cv2.Rodrigues(rv);Cest=(-R.T@tv).ravel()
    w2c=im.cam_from_world();Rg=w2c.rotation.matrix();Cgt=-Rg.T@w2c.translation
    errs.append(np.linalg.norm(Cest-Cgt));inls.append(len(inl))
    ang=np.degrees(np.arccos(np.clip((np.trace(R@Rg.T)-1)/2,-1,1)));errs[-1]=(errs[-1],ang)
  e=np.array([x[0] for x in errs]);a=np.array([x[1] for x in errs])
  print('held-out',len(ims[1::2]),'localized',len(errs),'fails',fails)
  print('pos err units median %.4f p90 %.4f | rot err deg median %.2f p90 %.2f | inliers median %d'%(np.median(e),np.percentile(e,90),np.median(a),np.percentile(a,90),np.median(inls)))
  np.save('heldout_err.npy',e)
