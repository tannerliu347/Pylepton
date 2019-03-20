from pylepton.LeptonCamera import LeptonCamera

pixel2Follow = {'First point' : [1,1]}
camera1 = LeptonCamera.LeptonCamera('test1', pixel2Follow)
camera1.takeImg()
camera1.saveData()