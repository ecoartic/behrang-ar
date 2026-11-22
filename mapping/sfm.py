import pycolmap,time,pathlib,sys
db='db.db';img='imgs';out=pathlib.Path('sparse');out.mkdir(exist_ok=True)
t=time.time()
ro=pycolmap.ImageReaderOptions();ro.camera_model='SIMPLE_RADIAL'
ex=pycolmap.FeatureExtractionOptions();ex.sift.max_num_features=4000
pycolmap.extract_features(db,img,camera_mode=pycolmap.CameraMode.SINGLE,reader_options=ro,extraction_options=ex)
print('extract',round(time.time()-t));t=time.time()
so=pycolmap.SequentialPairingOptions();so.overlap=12;so.loop_detection=False
pycolmap.match_sequential(db,pairing_options=so)
print('match',round(time.time()-t));t=time.time()
recs=pycolmap.incremental_mapping(db,img,str(out))
print('map',round(time.time()-t))
for k,r in recs.items():print(k,r.summary())
