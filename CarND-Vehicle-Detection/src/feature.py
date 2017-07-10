import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2
from skimage.feature import hog
import os, pdb

# Define a function to return HOG features and visualization
def get_hog_features(img, orient, pix_per_cell, cell_per_block, 
                        vis=False, feature_vec=True):
    # Call with two outputs if vis==True
    if vis == True:
        features, hog_image = hog(img, orientations=orient, 
                                  pixels_per_cell=(pix_per_cell, pix_per_cell),
                                  cells_per_block=(cell_per_block, cell_per_block), 
                                  transform_sqrt=True, 
                                  visualise=vis, feature_vector=feature_vec)
        return features, hog_image
    # Otherwise call with one output
    else:      
        features = hog(img, orientations=orient, 
                       pixels_per_cell=(pix_per_cell, pix_per_cell),
                       cells_per_block=(cell_per_block, cell_per_block), 
                       transform_sqrt=True, 
                       visualise=vis, feature_vector=feature_vec)
        return features

# Define a function to compute binned color features  
def bin_spatial(img, size=(32, 32)):
    # Use cv2.resize().ravel() to create the feature vector
    features = cv2.resize(img, size).ravel() 
    # Return the feature vector
    return features

# Define a function to compute color histogram features 
# NEED TO CHANGE bins_range if reading .png files with mpimg!
def color_hist(img, nbins=32, bins_range=(0, 256)):
    # Compute the histogram of the color channels separately
    channel1_hist = np.histogram(img[:,:,0], bins=nbins, range=bins_range)
    channel2_hist = np.histogram(img[:,:,1], bins=nbins, range=bins_range)
    channel3_hist = np.histogram(img[:,:,2], bins=nbins, range=bins_range)
    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((channel1_hist[0], channel2_hist[0], channel3_hist[0]))
    # Return the individual histograms, bin_centers and feature vector
    return hist_features

def color_convert_from_RGB(img, color_space):
    if color_space == 'HSV':
        feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    elif color_space == 'LUV': # LUV will give negative number, hog needs non-negative
        feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2LUV)
    elif color_space == 'HLS':
        feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    elif color_space == 'YUV': # YUV will give negative number?? hog needs non-negative
        feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    elif color_space == 'YCrCb':
        feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    return feature_image

# Define a function to extract features from a single image window
# This function is very similar to extract_features()
# just for a single image rather than list of images
def single_img_features(img, color_space='RGB', spatial_size=(32, 32),
                        hist_bins=32, orient=9, 
                        pix_per_cell=8, cell_per_block=2, hog_channel=0,
                        spatial_feat=True, hist_feat=True, hog_feat=True):    
    #1) Define an empty list to receive features
    img_features = []
    #2) Apply color conversion if other than 'RGB'
    if color_space != 'RGB':
        feature_image = color_convert_from_RGB(img, color_space)
    else: feature_image = np.copy(img)      
    #3) Compute spatial features if flag is set
    if spatial_feat == True:
        spatial_features = bin_spatial(feature_image, size=spatial_size)
        #4) Append features to list
        img_features.append(spatial_features)
    #5) Compute histogram features if flag is set
    if hist_feat == True:
        hist_features = color_hist(feature_image, nbins=hist_bins)
        #6) Append features to list
        img_features.append(hist_features)
    #7) Compute HOG features if flag is set
    if hog_feat == True:
        if hog_channel == 'ALL':
            hog_features = []
            for channel in range(feature_image.shape[2]):
                hog_features.extend(get_hog_features(feature_image[:,:,channel], 
                                    orient, pix_per_cell, cell_per_block, 
                                    vis=False, feature_vec=True))      
        else:
            hog_features = get_hog_features(feature_image[:,:,hog_channel], orient, 
                        pix_per_cell, cell_per_block, vis=False, feature_vec=True)
        #8) Append features to list
        img_features.append(hog_features)

    #9) Return concatenated array of features
    return np.concatenate(img_features)

    
# Define a function to extract features from a list of images
# Have this function call bin_spatial() and color_hist()
def extract_features(img_paths, param, data_aug=True):
    # color_space='RGB', spatial_size=(32, 32),
    #                     hist_bins=32, orient=9, 
    #                     pix_per_cell=8, cell_per_block=2, hog_channel=0,
    #                     spatial_feat=True, hist_feat=True, hog_feat=True):
    # Create a list to append feature vectors to
    features = []
    # Iterate through the list of images
    for file in img_paths:
        file_features = []
        # Read in each one by one

        # image = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
        image = mpimg.imread(file)
        # # if file.endswith('jpg') or file.endswith('jpeg'):
        # #     image = image.astype(np.float32)/255
        if file.endswith('png'):
            image = image.astype(np.float32)*255
        # pdb.set_trace()
        file_features = single_img_features(image, param['color_space'], param['spatial_size'],
                        param['hist_bins'], param['orient'], 
                        param['pix_per_cell'], param['cell_per_block'], param['hog_channel'],
                        param['spatial_feat'], param['hist_feat'], param['hog_feat'])
        features.append(file_features)

    if data_aug:
        for file in img_paths:
            file_features = []
            # Read in each one by one
            image = mpimg.imread(file)
            # image = cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB)
            image = np.fliplr(image)
            # if file.endswith('jpg') or file.endswith('jpeg'):
            #     image = image.astype(np.float32)/255
            if file.endswith('png'):
                image = image.astype(np.float32)*255
            # pdb.set_trace()
            file_features = single_img_features(image, param['color_space'], param['spatial_size'],
                            param['hist_bins'], param['orient'], 
                            param['pix_per_cell'], param['cell_per_block'], param['hog_channel'],
                            param['spatial_feat'], param['hist_feat'], param['hog_feat'])
            features.append(file_features)

    # Return list of feature vectors
    return features


def sample_hog_vis(car_img_path, notcar_img_path, param):
    plt.subplot(1,4,1)
    img = mpimg.imread(car_img_path)
    if car_img_path.endswith('png'):
        img = img.astype(np.float32)*255
    # img = cv2.cvtColor(cv2.imread(car_img_path), cv2.COLOR_BGR2RGB)
    plt.tight_layout()
    plt.imshow(img)
    plt.title('original')
    feature_image = color_convert_from_RGB(img, param['color_space'])
    for ch in range(3):
        _, hog_image = get_hog_features(feature_image[:,:,ch], param['orient'], param['pix_per_cell'], param['cell_per_block'], vis=True, feature_vec=True)
        plt.subplot(1,4,ch+2)
        plt.imshow(hog_image)
        plt.title('hog of channel %s'%param['color_space'][ch])
    plt.savefig('car_hog.jpg', bbox_inches='tight', dpi=400)

    plt.subplot(1,4,1)
    img = mpimg.imread(notcar_img_path)
    if notcar_img_path.endswith('png'):
        img = img.astype(np.float32)*255
    # img = cv2.cvtColor(cv2.imread(notcar_img_path), cv2.COLOR_BGR2RGB)
    plt.tight_layout()
    plt.imshow(img)
    plt.title('original')
    feature_image = color_convert_from_RGB(img, param['color_space'])
    for ch in range(3):
        _, hog_image = get_hog_features(feature_image[:,:,ch], param['orient'], param['pix_per_cell'], param['cell_per_block'], vis=True, feature_vec=True)
        plt.subplot(1,4,ch+2)
        plt.imshow(hog_image)
        plt.title('hog of channel %s'%param['color_space'][ch])
    plt.savefig('notcar_hog.jpg', bbox_inches='tight', dpi=400)