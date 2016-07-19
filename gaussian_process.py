import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

#-------------------------------------------------------------

#First initiialize the needed variables
n_dim = 2

data_start = -10
data_stop = 10
data_num = 10

data_std = 1.0

predict_start = -15
predict_stop = 15
predict_num = 100

band_amp_ranges = np.array([0.1,10.0])
band_amp_num = 10
band_data_ranges = np.array([0.1,10.0])
band_data_num = 10
band_std_ranges = np.array([[0.1,10.0],[0.1,10.0]])
band_std_num = np.array([10,10])

if len(band_std_ranges) != n_dim or len(band_std_num) != n_dim:
	raise ValueError, "Must provide one and only one bandwidth for each dimension"

#-------------------------------------------------------------

#Initialize grid over data points
data_coords = [None]*n_dim
for i in xrange(n_dim):
	data_coords[i] = np.linspace(start=data_start, stop=data_stop, num=data_num)

if n_dim == 1:
	data_coords = np.transpose(np.array(data_coords))
else:
	data_coords = np.array(np.meshgrid(*data_coords,indexing='ij'))
	data_coords = np.rollaxis(data_coords, 0, (n_dim + 1))

data_grid_shape = ()
for i in xrange(n_dim):
	data_grid_shape += (data_num,)
data_values = np.ones(data_grid_shape)*np.nan

#Initialize grid over predictive points
predict_coords = [None]*n_dim
for i in xrange(n_dim):
	predict_coords[i] = np.linspace(start=predict_start, stop=predict_stop, num=predict_num)

if n_dim == 1:
	predict_coords = np.transpose(np.array(predict_coords))
else:
	predict_coords = np.array(np.meshgrid(*predict_coords,indexing='ij'))
	predict_coords = np.rollaxis(predict_coords, 0, (n_dim + 1))

data_list = data_coords.reshape((-1,n_dim))
predict_list = predict_coords.reshape((-1,n_dim))

#-------------------------------------------------------------

#Generate function and noise to produce data
data_noise = np.random.normal(0,data_std,data_grid_shape)

#data_signal = 1.*data_coords[...,0]
#data_signal = 1.*data_coords[...,0] + 1.*data_coords[...,1]
data_signal = 1.*data_coords[...,0]**2. + 1.*data_coords[...,1]**2.
#data_signal = 1.*np.sin(0.5*data_coords[...,0]) + 1.*np.sin(0.5*data_coords[...,1])


data_values = data_signal + data_noise
data_values = data_values.reshape(-1)

#------------------------------------------------------------

#Loop over a grid of bandwidths
band_coords = [None]*(n_dim+2)
for i in xrange(n_dim):
	band_coords[i+2] = np.logspace(start=np.log10(band_std_ranges[i,0]), stop=np.log10(band_std_ranges[i,1]), num=band_std_num[i])
band_coords[0] = np.logspace(start=np.log10(band_amp_ranges[0]), stop=np.log10(band_amp_ranges[1]), num=band_amp_num)
band_coords[1] = np.logspace(start=np.log10(band_data_ranges[0]), stop=np.log10(band_data_ranges[1]), num=band_data_num)

band_coords = np.array(np.meshgrid(*band_coords,indexing='ij'))
band_coords = np.rollaxis(band_coords, 0, len(band_coords)+1)

band_grid_shape = ()
band_grid_shape += (band_amp_num,)
band_grid_shape += (band_data_num,)
for i in xrange(n_dim):
	band_grid_shape += (band_std_num[i],)
band_values = np.ones(band_grid_shape)*np.nan

band_coords = band_coords.reshape((-1,n_dim+2))
band_values = band_values.reshape(-1)

for j,bands in enumerate(band_coords):
	#Generate the Gaussian-process covariances and invert
	K_data_data = np.ones((len(data_list),len(data_list)))*np.nan
	for i,coord in enumerate(data_list):
		K_data_data[:,i] = bands[0]**2. * np.exp( -0.5 * np.sum(((coord - data_list)/bands[2:])**2., axis=-1) )
		K_data_data[i,i] += bands[1]**2.
	
	inv_K_data_data = linalg.inv(K_data_data)
	
	#Calculate and report the CV joint-log-likelihood estimate
	CV_jll_est = 0.
	for i in xrange(len(data_list)):
		mean_minus_data = np.sum(data_values*inv_K_data_data, axis=-1)[i] / inv_K_data_data[i,i]
		std = np.sqrt(1./inv_K_data_data[i,i])
		
		CV_jll_est += -0.5*np.log10(np.e)*(mean_minus_data/std)**2. - 0.5*np.log10(2.* np.pi* std**2.)
	
	band_values[j] = CV_jll_est
	
#Choose the optimal bandwidths to be those that maximize the CV joint joint-log-likelihood estimate
opt_band_index = np.argmax(band_values)
band_amp = band_coords[opt_band_index,0]
band_data = band_coords[opt_band_index,1]
band_std = band_coords[opt_band_index,2:]
print band_amp,band_data,band_std

#-------------------------------------------------------------

#Now calculate the Gaussian-process covariances for optimal bandwidths
K_data_data = np.ones((len(data_list),len(data_list)))*np.nan
for i,coord in enumerate(data_list):
	K_data_data[:,i] = band_amp**2. * np.exp( -0.5 * np.sum(((coord - data_list)/band_std)**2., axis=-1) )
	K_data_data[i,i] += band_data**2.

K_predict_data = np.ones((len(predict_list),len(data_list)))*np.nan
for i,coord in enumerate(data_list):
	K_predict_data[:,i] = band_amp**2. * np.exp( -0.5 * np.sum(((coord - predict_list)/band_std)**2., axis=-1) )
	
K_predict_predict = np.ones((len(predict_list),len(predict_list)))*np.nan
for i,coord in enumerate(predict_list):
	K_predict_predict[:,i] = band_amp**2. * np.exp( -0.5 * np.sum(((coord - predict_list)/band_std)**2., axis=-1) )
	K_predict_predict[i,i] += band_data**2.

inv_K_data_data = linalg.inv(K_data_data)

#Next calculate the mean and std at each prediction point
predict_means = np.ones(len(predict_list))*np.nan
predict_stds = np.ones(len(predict_list))*np.nan
for i in xrange(len(predict_list)):
	tmp_mean = np.sum(data_values*inv_K_data_data, axis=-1)
	predict_means[i] = np.sum(tmp_mean*K_predict_data[i,:], axis=-1)
	
	tmp_std = np.sum(K_predict_data[i,:]*inv_K_data_data, axis=-1)
	tmp_std = np.sum(tmp_std*K_predict_data[i,:], axis=-1)
	predict_stds[i] = np.sqrt(K_predict_predict[i,i] - tmp_std)
	
#Plot everything
if n_dim == 1:
	myfig100=plt.figure(100)
	plt.fill_between(predict_list[:,0], predict_means - predict_stds, predict_means + predict_stds, color='r',alpha=0.4)
	plt.plot(predict_list[:,0], predict_means, 'r', linewidth=2)
	plt.errorbar(data_list[:,0], data_values, yerr=data_std, fmt='b*', linewidth=2)
	plt.grid(True,which='both')
	plt.show()

if n_dim == 2:
	myfig100=plt.figure(100)
	ax = plt.axes(projection='3d')
	surf = ax.plot_trisurf(predict_list[:,0], predict_list[:,1], predict_means, cmap=cm.jet,linewidth=0)
	ax.scatter(data_list[:,0], data_list[:,1], data_values, c='k')
	myfig100.colorbar(surf)
	plt.show()
