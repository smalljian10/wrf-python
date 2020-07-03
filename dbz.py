import numpy as np
import cartopy.feature as cfeature
from netCDF4 import Dataset
from cartopy.feature import NaturalEarthFeature
from cartopy import crs
from cartopy.io.shapereader import Reader
from matplotlib.cm import get_cmap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import cm
from matplotlib import pyplot as plt
from wrf import (getvar,interplevel,latlon_coords,get_cartopy,to_np,cartopy_xlim,cartopy_ylim)

#reading wrf_out file
file_path = './wrfout_d01_2019-07-27_00:00:00'
f = Dataset(file_path)

#get time and transform UT to BJT
time = getvar(f,'times',timeidx=2)
t = to_np(time)
ti = str(t)
bj=str(int(ti[11:13])+8)
bjt = ti.replace(ti[11:13],bj)
BJT = bjt[0:19]

#get dbz from wrf_out file
dbz = getvar(f,'dbz',timeidx=3)

#get dbz in the specified height
z = getvar(f,'z')
dbz_ht = interplevel(dbz,z,2065.2)

#get the latitude and longitude points
lats,lons = latlon_coords(dbz_ht)

#get the cartopy mapping object
cart_proj = get_cartopy(dbz_ht)

#creat a figure
fig = plt.figure(figsize=(10,7.5))

#set the geoaxes to the projection used by wrf
ax = plt.axes(projection=cart_proj)

#####################add background map###############################
#define a function
def add_shape(source, projection):
    return cfeature.ShapelyFeature(Reader(source).geometries(), projection, facecolor='none')
#add cities
proj=crs.PlateCarree()
city_source = '/yin_raid/xin/github/pyXZ/XZ_maps/shapefiles/cnmap/china_city.shp'
cities=add_shape(city_source,proj)
ax.add_feature(cities,linewidth=0.5,edgecolor='black')
#add provinces
province_source = '/yin_raid/xin/github/pyXZ/XZ_maps/shapefiles/cnmap/china_province.shp'
provinces=add_shape(province_source,proj)
ax.add_feature(provinces,linewidth=0.5,edgecolor='red')
#add coastline
ax.coastlines('50m',linewidth=0.8)
##########################################################################

#custom color map
colors = ["#CCCCCC", "#00CCFF", "#0066FF", "#0033CC", "#00FF66",
          "#33CC66", "#009900", "#FFFF66", "#FFCC33", "#FF9900",
          "#FF6666", "#FF3333", "#CC0000", "#FF00FF", "#CD00CD",
          "#800080"]

cmap_name = 'dbz'
n_bins = np.arange(-5, 80, 5)
cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=16)
cm.register_cmap(name=cmap_name,cmap=cmap)

#define levels
levels = np.arange(-5,70,5)

#plot the filled contours for the dbz
plt.contourf(to_np(lons),to_np(lats),to_np(dbz_ht),levels,transform=crs.PlateCarree(),cmap=get_cmap('dbz'))

#add a color bar
plt.colorbar(ax=ax,shrink=.98,label='dbz')

#set the map bounds
ax.set_xlim(cartopy_xlim(dbz_ht))
ax.set_ylim(cartopy_ylim(dbz_ht))

#add title
plt.title('Radar Reflectivity From Similation'+'\n'+BJT)

#save picture
plt.savefig('./dbz.png')
