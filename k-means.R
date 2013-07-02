"Input: data = an d X n data matrix, d being the dimensionality of the data,
and n being the number of data points, k = the number of clusters you want"

kMeans = function(data, k, threshold){
	data = normalizeData(data)
	seed_centroids = initializeCentroids(data, k)
	final_clusters = assignAndUpdate(data, seed_centroids, threshold)
	return(final_clusters)
}

summaryStats = function(final_list){
	data = final_list[[1]]
	k = dim(data)[2]
	d = dim(data)[1] - 1
	centroids = final_list[[2]]
	for(i in 1:dim(centroids)[2]){
		sprintf("Percentage of players in cluster %i:", i)
		this_cluster = data[,data[d+1,] == i]
		percentage = dim(this_cluster)[2]/dim(data)[2]
		print(percentage)
	}
}

assignAndUpdate = function(data, centroids, threshold, iter_count = 1){

	with_clusters = assignClusters(data, centroids)
	new_centroids = updateCentroids(with_clusters, centroids)
	distances_moved = sqrt(colSums((new_centroids - centroids)^2))
	check_distances = distances_moved < threshold

	if(sum(check_distances) == length(check_distances)){
		print("Clusters converged. Number of iterations: ")
		print(iter_count)
		return(assignClusters(data, new_centroids))
	}
	#recursion
	iter_count = iter_count + 1
	assignAndUpdate(data, new_centroids, threshold, iter_count)
}


"INITIALIZATION METHOD: Chooses k random data points, and initializes a
seed centroid at each one."
initializeCentroids = function(data, k){
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
	new_centroids = as.data.frame(matrix(nrow = dim(centroids)[1], ncol = dim(centroids)[2]))
	for(cluster in c(1:k)){
		this_cluster = as.data.frame(with_clusters[,with_clusters[d+1,] == cluster])
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

normalizeData = function(data){
	just_numbers = data
	just_numbers[is.na(just_numbers)] = 0
	colMaxes = apply(just_numbers, 2, max)
	colMins = apply(just_numbers, 2, min)
	normalizer = colMaxes - colMins

	for(i in 1:dim(just_numbers)[1]){
		just_numbers[i,] = (just_numbers[i,] - colMins)/normalizer
	}
	return(just_numbers)
}