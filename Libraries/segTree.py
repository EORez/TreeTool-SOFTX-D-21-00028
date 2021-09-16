import pclpy
import numpy as np

def FloorRemove(points, setMaxWindowSize = 20, setSlope = 1.0, setInitialDistance = 0.5, setMaxDistance = 3.0):
    PointCloud = points
    ind = pclpy.pcl.vectors.Int()
    pmf = pclpy.pcl.segmentation.ApproximateProgressiveMorphologicalFilter.PointXYZ()
    pmf.setInputCloud(PointCloud)
    pmf.setMaxWindowSize(setMaxWindowSize)
    pmf.setSlope(setSlope)
    pmf.setInitialDistance(setInitialDistance)
    pmf.setMaxDistance(setMaxDistance)
    pmf.extract(ind)

    ext = pclpy.pcl.filters.ExtractIndices.PointXYZ()
    ground = pclpy.pcl.PointCloud.PointXYZ()
    Nogroundpoints = pclpy.pcl.PointCloud.PointXYZ()
    ext.setInputCloud(PointCloud)
    ext.setIndices(ind)
    ext.filter(ground)
    ext.setNegative(True)
    ext.filter(Nogroundpoints)

    return Nogroundpoints.xyz, ground.xyz

def RadiusOutlierRemoval(points , MinN=6, Radius=0.4, Organized=True):
    ROR = pclpy.pcl.filters.RadiusOutlierRemoval.PointXYZ()
    cloud = pclpy.pcl.PointCloud.PointXYZ(points)
    ROR.setInputCloud(cloud)
    ROR.setMinNeighborsInRadius(MinN)
    ROR.setRadiusSearch(Radius)
    ROR.setKeepOrganized(Organized)
    FilteredROR = pclpy.pcl.PointCloud.PointXYZ()
    ROR.filter(FilteredROR)
    return FilteredROR.xyz

def ExtractNormals(points, search_radius = 0.1):
    cloud = pclpy.pcl.PointCloud.PointXYZ(points)
    segcloudNor = pclpy.pcl.features.NormalEstimationOMP.PointXYZ_Normal()
    tree = pclpy.pcl.search.KdTree.PointXYZ()
    segcloudNor.setInputCloud(cloud)
    segcloudNor.setSearchMethod(tree)
    segcloudNor.setRadiusSearch(search_radius)
    normals = pclpy.pcl.PointCloud.Normal()
    segcloudNor.compute(normals)
    return normals


def euclidean_cluster_extract(points, tolerance=2, min_cluster_size=20, max_cluster_size=25000):
    filtered_points = pclpy.pcl.segmentation.EuclideanClusterExtraction.PointXYZ()
    kd_tree = pclpy.pcl.search.KdTree.PointXYZ()
    points_to_cluster = pclpy.pcl.PointCloud.PointXYZ(points)
    
    kd_tree.setInputCloud(points_to_cluster)
    filtered_points.setInputCloud(points_to_cluster)
    filtered_points.setClusterTolerance(tolerance)
    filtered_points.setMinClusterSize(min_cluster_size)
    filtered_points.setMaxClusterSize(max_cluster_size)
    filtered_points.setSearchMethod(kd_tree)

    point_indexes = pclpy.pcl.vectors.PointIndices()
    filtered_points.extract(point_indexes)

    cluster_list = [points_to_cluster.xyz[i2.indices] for i2 in point_indexes]
    return cluster_list

def RegionGrowing(Points, Ksearch=30, minc=20, maxc=100000, nn=30, smoothness=30.0, curvature=1.0):
    segcloud = pclpy.pcl.PointCloud.PointXYZ(Points)
    segcloudNor = pclpy.pcl.features.NormalEstimation.PointXYZ_Normal()
    tree = pclpy.pcl.search.KdTree.PointXYZ()

    segcloudNor.setInputCloud(segcloud)
    segcloudNor.setSearchMethod(tree)
    segcloudNor.setKSearch(Ksearch)
    normals = pclpy.pcl.PointCloud.Normal()
    segcloudNor.compute(normals)
    
    RGF = pclpy.pcl.segmentation.RegionGrowing.PointXYZ_Normal()
    RGF.setInputCloud(segcloud)
    RGF.setInputNormals(normals)
    RGF.setMinClusterSize(minc)
    RGF.setMaxClusterSize(maxc)
    RGF.setSearchMethod(tree)
    RGF.setNumberOfNeighbours(nn)
    RGF.setSmoothnessThreshold(smoothness / 180.0 * np.pi)
    RGF.setCurvatureThreshold(curvature)

    clusters = pclpy.pcl.vectors.PointIndices()
    RGF.extract(clusters)
    
    ppclusters = [segcloud.xyz[i2.indices] for i2 in clusters]
    return ppclusters


def segment(points, model=pclpy.pcl.sample_consensus.SACMODEL_LINE, method=pclpy.pcl.sample_consensus.SAC_RANSAC, miter=1000, distance=0.5, rlim=[0,0.5]):   
    segcloud = pclpy.pcl.PointCloud.PointXYZ(points)
    cylseg = pclpy.pcl.segmentation.SACSegmentation.PointXYZ()

    cylseg.setInputCloud(segcloud)
    cylseg.setDistanceThreshold(distance)
    cylseg.setOptimizeCoefficients(True)
    cylseg.setMethodType(method)
    cylseg.setModelType(model)
    cylseg.setMaxIterations(miter)
    cylseg.setRadiusLimits(rlim[0],rlim[1])
    pI = pclpy.pcl.PointIndices()
    Mc = pclpy.pcl.ModelCoefficients()
    cylseg.segment(pI,Mc)
    return pI.indices, Mc.values

def segment_normals(points, searchRadius=20, model=pclpy.pcl.sample_consensus.SACMODEL_LINE, method=pclpy.pcl.sample_consensus.SAC_RANSAC, normalweight=0.0001, miter=1000, distance=0.5, rlim=[0,0.5]):
    segNormals = ExtractNormals(points, searchRadius)
    
    segcloud = pclpy.pcl.PointCloud.PointXYZ(points)
    cylseg = pclpy.pcl.segmentation.SACSegmentationFromNormals.PointXYZ_Normal()

    cylseg.setInputCloud(segcloud)
    cylseg.setInputNormals(segNormals)
    cylseg.setDistanceThreshold(distance)
    cylseg.setOptimizeCoefficients(True)
    cylseg.setMethodType(method)
    cylseg.setModelType(model)
    cylseg.setMaxIterations(miter)
    cylseg.setRadiusLimits(rlim[0],rlim[1])
    cylseg.setNormalDistanceWeight(normalweight)
    pI = pclpy.pcl.PointIndices()
    Mc = pclpy.pcl.ModelCoefficients()
    cylseg.segment(pI,Mc)
    return pI.indices, Mc.values


def findstemsLiDAR(pointsXYZ):
    Nogroundpoints,ground = FloorRemove(pointsXYZ)
    flatpoints = np.hstack([Nogroundpoints[:,0:2],np.zeros_like(Nogroundpoints)[:,0:1]])

    RRFpoints = RadiusOutlierRemoval(flatpoints)
    notgoodpoints = Nogroundpoints[np.isnan(RRFpoints[:,0])]
    goodpoints = Nogroundpoints[np.bitwise_not(np.isnan(RRFpoints[:,0]))]

    cluster_list = EucladeanClusterExtract(goodpoints)
    RGclusters = []
    for i in cluster_list:
        ppclusters = RegionGrowing(i)
        RGclusters.append(ppclusters)

    models = []
    stemsR = []
    for i in RGclusters:
        for p in i:
            indices, model = segment_normals(p)
            prop = len(p[indices])/len(p)
            if len(indices)>1 and prop>0. and np.arccos(np.dot([0,0,1],model[3:6]))<.6:
                points = p[indices]
                PC,_,_ = Plane.getPrincipalComponents(points)
                if PC[0]/PC[1]>10:
                    stemsR.append(points)
                    models.append(model)
    return stemsR,models

def voxelize(points,leaf = 0.1):
    if (type(points) == pclpy.pcl.PointCloud.PointXYZRGB):
        Cloud = points
        VF = pclpy.pcl.filters.VoxelGrid.PointXYZRGB()
        VFmm = pclpy.pcl.PointCloud.PointXYZRGB()
    else:
        Cloud = pclpy.pcl.PointCloud.PointXYZ(points)
        VF = pclpy.pcl.filters.VoxelGrid.PointXYZ()
        VFmm = pclpy.pcl.PointCloud.PointXYZ()
    
    VF.setLeafSize(leaf,leaf,leaf)
    VF.setInputCloud(Cloud)
    
    VF.filter(VFmm)
    if type(points) == pclpy.pcl.PointCloud.PointXYZRGB:
        return VFmm
    else:
        return VFmm.xyz
    
