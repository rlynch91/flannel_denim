import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import time
import scipy.optimize as scipy_optimize

########################################################################

###
def calculate_K_data_data(bands,data_coords):
	"""
	"""
	K_data_data = np.ones((len(data_coords),len(data_coords)))*np.nan
	for i,coord in enumerate(data_coords):
		K_data_data[i,:] = bands[0]**2. * np.exp( -0.5 * np.sum(((coord - data_coords)/bands[2:])**2., axis=-1) )
		K_data_data[i,i] += bands[1]**2.
		
	return K_data_data

###
def calculate_K_predict_data(bands,predict_coords,data_coords):
	"""
	"""
	K_predict_data = np.ones((len(predict_coords),len(data_coords)))*np.nan
	for i,coord in enumerate(predict_coords):
		K_predict_data[i,:] = bands[0]**2. * np.exp( -0.5 * np.sum(((coord - data_coords)/bands[2:])**2., axis=-1) )
	
	return K_predict_data

###
def calculate_K_predict_predict(bands,predict_coords):
	"""
	"""
	K_predict_predict = np.ones((len(predict_coords),len(predict_coords)))*np.nan
	for i,coord in enumerate(predict_coords):
		K_predict_predict[i,:] = bands[0]**2. * np.exp( -0.5 * np.sum(((coord - predict_coords)/bands[2:])**2., axis=-1) )
		K_predict_predict[i,i] += bands[1]**2.
		
	return K_predict_predict

###
def calculate_inv_K_data_data(K_data_data):
	"""
	"""
	return linalg.inv(K_data_data)

###
def calculate_partial_K_data_data(bands,data_coords,K_data_data):
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
	#Calculte inv_K
	K_data_data = calculate_K_data_data(bands=bandwidths,data_coords=data_coords)
	inv_K_data_data = calculate_inv_K_data_data(K_data_data=K_data_data)
	
	#Calculate alpha
	alpha = np.sum(inv_K_data_data*data_values, axis=-1)
					
	#Loop over data to calculate pseudo-log-likelihood at each data point
	pseudo_log_like = 0.
	for i in xrange(len(data_coords)):
		pseudo_log_like += (-0.5*(alpha[i]**2.)/(inv_K_data_data[i,i]) - 0.5*np.log(2.* np.pi / inv_K_data_data[i,i])) / np.log(10.)
			
	return -pseudo_log_like
	
###
def calculate_pseudo_log_likelihood_and_gradient(bandwidths,data_coords,data_values):
	"""
	"""
	#Calculte inv_K and partial_K
	K_data_data = calculate_K_data_data(bands=bandwidths,data_coords=data_coords)
	inv_K_data_data = calculate_inv_K_data_data(K_data_data=K_data_data)
	partial_K_data_data = calculate_partial_K_data_data(bands=bandwidths,data_coords=data_coords,K_data_data=K_data_data)
	
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

###
def calculate_predict_dist(bandwidths,data_values,data_coords,predict_coords):
	"""
	"""
	#First calculate the full K values
	K_data_data = calculate_K_data_data(bands=bandwidths,data_coords=data_coords)
	K_predict_data = calculate_K_predict_data(bands=bandwidths,predict_coords=predict_coords,data_coords=data_coords)
	K_predict_predict = calculate_K_predict_predict(bands=bandwidths,predict_coords=predict_coords)
	inv_K_data_data = calculate_inv_K_data_data(K_data_data=K_data_data)
	
	#Next calculate the mean and std at each prediction point
	tmp_mean_vector = np.sum(inv_K_data_data[:,:]*data_values[:], axis=-1)
	predict_means = np.sum(K_predict_data[:,:]*tmp_mean_vector[:], axis=-1)
	
	predict_stds = np.ones(len(predict_coords))*np.nan
	for i in xrange(len(predict_coords)):		
		tmp_std = np.sum(inv_K_data_data[:,:]*K_predict_data[i,:], axis=-1)
		tmp_std = np.sum(K_predict_data[i,:]*tmp_std[:], axis=-1)
		predict_stds[i] = np.sqrt(K_predict_predict[i,i] - tmp_std)
	
	return predict_means, predict_stds
	

########################################################################

if __name__=='__main__':

	#First initialize the needed variables
	n_dim = 1

	data_start = -3
	data_stop = 3
	data_num = 100

	data_std = 1.0

	predict_start = -15
	predict_stop = 15
	predict_num = 100

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

	#data_signal = 2.*np.exp(-data_coords[...,0]**2.)
	#data_signal = 1.*data_coords[...,0]**2.
	data_signal = 5.*np.sin(0.5*data_coords[...,0])
	#data_signal = 1.*data_coords[...,0] + 1.*data_coords[...,1]
	#data_signal = 1.*data_coords[...,0]**2. + 1.*data_coords[...,1]**2.
	#data_signal = 1.*np.sin(0.5*data_coords[...,0]) + 1.*np.sin(0.5*data_coords[...,1])
	#data_signal = 2.*np.exp(-(data_coords[...,0]**2. + data_coords[...,1]**2.))

	data_values = data_signal + data_noise
	data_values = data_values.reshape(-1)

	#-------------------------------------------------------------------

	tref = time.time()
	
	x0 = np.ones(n_dim+2)

	#Find the optimal bandwidths
	min_object = scipy_optimize.minimize(fun=calculate_pseudo_log_likelihood, x0=x0, args=(data_list,data_values), method='Nelder-Mead', jac=False)
	opt_bands = min_object['x']
	
	print 'Nelder-Mead',min_object
	print calculate_pseudo_log_likelihood_and_gradient(bandwidths=min_object['x'],data_coords=data_list,data_values=data_values)
	print "Optimization time: ",time.time() - tref
	
	#-------------------------------------------------------------------

	#Calculate the mean and std at each prediction point
	predict_means,predict_stds = calculate_predict_dist(bandwidths=opt_bands,data_values=data_values,data_coords=data_list,predict_coords=predict_list)
		
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
