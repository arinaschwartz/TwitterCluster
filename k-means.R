#Input: data = an d X n data matrix, d being the dimensionality of the data,
#and n being the number of data points, 
#k = the number of clusters you want
"INITIALIZATION METHOD: Chooses k random data points, and assigns a centroid
to each one."
initialize_centroids = function(data, k){
	n = dim(data)[2]
	d = dim(data)[1]

	random_seed_indices = sample(1:n, k)
	seed_centroids = data[,random_seed_indices]
	return(seed_centroids)
}

"returns a vector containing a given point's distance to all the
centroids indexed by centroid."
assignedCentroid = function(point, centroids){

	distances = sqrt(colSums((centroids - point)^2))

	assigned_centroid = match(min(distances), distances)
	return(assigned_centroid)

}
"returns data matrix with an extra column tacked on, showing the
assigned cluster of that point"
assignClusters = function(data, centroids){
	n = dim(data)[2]
	assigned_centroids = c()
	for (point in 1:n){
		assigned_centroids = c(assigned_centroids,
						assignedCentroid(data[,point], centroids))
	}
	return(rbind(data, assigned_centroids))
}

updateCentroids = function(with_clusters, centroids){
	k = dim(centroids)[2]
	d = dim(with_clusters)[1] - 1
	new_centroids = matrix(nrow = dim(centroids)[1], ncol = dim(centroids)[2])
	for(cluster in c(1:k)){
		this_cluster = with_clusters[,with_clusters[3,] == cluster]
		new_mean = rowMeans(this_cluster)
		new_centroids[,cluster] = new_mean[1:d]
	}
	return(new_centroids)
}




"ONLY WORKS WITH 2-dimensional DATA"
vis = function(data, centroids){
	k = dim(centroids)[1]
	plot(data)

	with_clusters = assignClusters(data, centroids)

	for(cluster in 1:k){
		points(with_clusters[with_clusters[,3] == cluster,][,1:2], pch = 21,
													bg = sample(colours(), 1))

	}

	#points(centroids, pch = 21, bg = sample(colours(), k), cex = 3)

}