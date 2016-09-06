import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import time
import scipy.optimize as scipy_optimize

########################################################################

###
def calculate_K(bands,data_coords):
	"""
	"""
	K_data_data = np.ones((len(data_coords),len(data_coords)))*np.nan
	for i,coord in enumerate(data_coords):
		K_data_data[i,:] = bands[0]**2. * np.exp( -0.5 * np.sum(((coord - data_coords)/bands[2:])**2., axis=-1) )
		K_data_data[i,i] += bands[1]**2.
		
	return K_data_data

###
def calculate_inv_K(K_data_data):
	"""
	"""
	return linalg.inv(K_data_data)

###
def calculate_partial_K(bands,data_coords,K_data_data):
	"""
	"""
	partial_K_data_data = np.ones((len(bands),len(data_coords),len(data_coords)))*np.nan
	
	partial_K_data_data[0,:,:] = (K_data_data - np.eye(len(data_coords))*bands[1]**2.) * 2./np.absolute(bands[0])
	
	partial_K_data_data[1,:,:] = 2.*np.absolute(bands[1])
	
	for i,coord in enumerate(data_coords):
		partial_K_data_data[2:,i,:] = ((coord[:,np.newaxis]-data_coords.transpose()[:,:])**2./np.absolute(bands[2:,np.newaxis])**3.) * (K_data_data - np.eye(len(data_coords))*bands[1]**2.)[i,:]
	
	return partial_K_data_data
	
###
def calculate_pseudo_log_likelihood(bandwidths,data_coords,data_values):
	"""
	"""
	#Calculte inv_K and partial_K
	K_data_data = calculate_K(bands=bandwidths,data_coords=data_coords)
	inv_K_data_data = calculate_inv_K(K_data_data=K_data_data)
	partial_K_data_data = calculate_partial_K(bands=bandwidths,data_coords=data_coords,K_data_data=K_data_data)
	
	#Calculate alpha
	alpha = np.sum(inv_K_data_data*data_values, axis=-1)
	
	#Calculate Z
	Z = np.ones((len(bandwidths),len(data_coords),len(data_coords)))*np.nan
	for i in xrange(len(data_coords)):
		Z[:,i,:] = np.sum(inv_K_data_data[i,:,np.newaxis]*partial_K_data_data[:,:,:], axis=-2)
	
	#Calculate Z_alpha and Z_inv_K
	Z_alpha = np.ones((len(bandwidths),len(data_coords)))*np.nan
	Z_inv_K = np.ones((len(bandwidths),len(data_coords),len(data_coords)))*np.nan

	Z_alpha[:,:] = np.sum(Z[:,:,:] * alpha[:], axis=-1)
	for i in xrange(len(data_coords)):
		Z_inv_K[:,:,i] = np.sum(Z[:,:,:]*inv_K_data_data[:,i], axis=-1)
				
	#Loop over data to calculate pseudo-log-likelihood and its gradient at each data point
	pseudo_log_like = 0.
	pseudo_log_like_gradient = np.zeros(len(bandwidths))
	for i in xrange(len(data_coords)):
		pseudo_log_like += (-0.5*(alpha[i]**2.)/(inv_K_data_data[i,i]) - 0.5*np.log(2.* np.pi / inv_K_data_data[i,i])) / np.log(10.)
		pseudo_log_like_gradient += (alpha[i]*Z_alpha[:,i] - 0.5*Z_inv_K[:,i,i] - 0.5*(alpha[i]**2.)*Z_inv_K[:,i,i]/inv_K_data_data[i,i]) / (inv_K_data_data[i,i]*np.log(10.))
		
	return -pseudo_log_like, -pseudo_log_like_gradient

########################################################################

if __name__=='__main__':

	#First initialize the needed variables
	n_dim = 1

	data_start = -10
	data_stop = 10
	data_num = 20

	data_std = 1.0

	predict_start = -15
	predict_stop = 15
	predict_num = 100

	band_amp_ranges = np.array([0.1,10.0])
	band_amp_num = 20
	band_data_ranges = np.array([0.1,10.0])
	band_data_num = 20
	band_std_ranges = np.array([[0.1,10.0]])
	band_std_num = np.array([20])

	if len(band_std_ranges) != n_dim or len(band_std_num) != n_dim:
		raise ValueError, "Must provide one and only one bandwidth for each dimension"

	#-------------------------------------------------------------------

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

	#-------------------------------------------------------------------

	#Generate function and noise to produce data
	data_noise = np.random.normal(0,data_std,data_grid_shape)

	data_signal = 20.*np.exp(-data_coords[...,0]**2.)
	#data_signal = 1.*data_coords[...,0]
	#data_signal = 5.*np.sin(0.5*data_coords[...,0])
	#data_signal = 1.*data_coords[...,0] + 1.*data_coords[...,1]
	#data_signal = 1.*data_coords[...,0]**2. + 1.*data_coords[...,1]**2.
	#data_signal = 1.*np.sin(0.5*data_coords[...,0]) + 1.*np.sin(0.5*data_coords[...,1])

	data_values = data_signal + data_noise
	data_values = data_values.reshape(-1)

	#-------------------------------------------------------------------
	
	tref = time.time()

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

	print "Grid: ",time.time() - tref

	print np.max(band_values)
	print calculate_pseudo_log_likelihood(bandwidths=band_coords[opt_band_index],data_coords=data_list,data_values=data_values)

	#-------------------------------------------------------------------

	tref = time.time()

	#Find the optimal bandwidths
	min_object = scipy_optimize.minimize(fun=calculate_pseudo_log_likelihood, x0=band_coords[opt_band_index], args=(data_list,data_values), method='BFGS', jac=True)
	print min_object

	band_amp = min_object['x'][0]
	band_data = min_object['x'][1]
	band_std = min_object['x'][2:]

	print "BFGS: ",time.time() - tref
	

	#-------------------------------------------------------------------

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
	
	#-------------------------------------------------------------------
