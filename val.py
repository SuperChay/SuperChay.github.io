import h5py
import scipy.io as io
import PIL.Image as Image
import numpy as np
import os
import glob
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter
import scipy
import json
import torchvision.transforms.functional as F
from matplotlib import cm as CM
from image import *
from model import CSRNet
import torch
# %matplotlib inline

from torchvision import datasets, transforms
transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ])

root = './dataset'

#now generate the ShanghaiA's ground truth
part_A_train = os.path.join(root,'part_A_final/train_data','images')
part_A_test = os.path.join(root,'part_A_final/test_data','images')
part_B_train = os.path.join(root,'part_B_final/train_data','images')
part_B_test = os.path.join(root,'part_B_final/test_data','images')
path_sets = [part_A_test]
# path_sets = [test_image,]
img_paths = []
for path in path_sets:
    for img_path in glob.glob(os.path.join(path, '*.jpg')):
        img_paths.append(img_path)

with torch.no_grad():
    model = CSRNet()
    model = model.cuda()
    checkpoint = torch.load(r'C:\Users\36432\Desktop\PartBmodel_best.pth.tar')
    model.load_state_dict(checkpoint['state_dict'])


    mae = 0
    for i in range(len(img_paths)):
        img = 255.0 * F.to_tensor(Image.open(img_paths[i]).convert('RGB'))

        img[0,:,:]=img[0,:,:]-92.8207477031
        img[1,:,:]=img[1,:,:]-95.2757037428
        img[2,:,:]=img[2,:,:]-104.877445883
        img = img.cuda()
        #img = transform(Image.open(img_paths[i]).convert('RGB')).cuda()
        gt_file = h5py.File(img_paths[i].replace('.jpg','.h5').replace('images','ground_truth'),'r')
        groundtruth = np.asarray(gt_file['density'])
        output = model(img.unsqueeze(0))
        mae += abs(output.detach().cpu().sum().numpy()-np.sum(groundtruth))
        print(i,mae)
    print(mae/len(img_paths))
