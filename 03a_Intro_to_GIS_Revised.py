#!/usr/bin/env python
# coding: utf-8

# # Intro to GIS with Python
# ## What is GIS?
# GIS stands for _geographic information system_. Colloquially, it's the process of presenting and analyzing data on maps. GIS allows us to visualize and characterize the nature of spatially distributed data, including weather, infrastructure, and populations. As you can imagine, this is key for disaster response scenarios for both diagnosing the situation, as well as planning and monitoring the response.
# 
# There are dozens of different GIS software options, both free and commercial. In this course, we will focus on free, python-based tools and packages. The principles taught in this course should carry over to most common GIS implementations. 
# 

# In[1]:


import geopandas as gpd
import contextily as ctx # for basemaps
from shapely.geometry import Point, LineString, Polygon
from matplotlib import pyplot as plt
import folium


# ## Reading in Vector data
# For this lesson we are using data in the ESRI [Shapefile](https://doc.arcgis.com/en/arcgis-online/reference/shapefiles.htm) format. 
# 
# Geopandas supports reading a number of different GIS vector file formats: https://geopandas.org/en/stable/docs/user_guide/io.html
# 
# Geopandas uses [fiona](https://fiona.readthedocs.io/en/stable/fiona.html) to handle reading and writing vector file types.

# In[2]:


# print out the supported file types
import fiona; fiona.supported_drivers


# In[ ]:





# We will first look at some flood risk assessment data from the Philippines. This data is originally from the Humanitarian Data Exchange: https://data.humdata.org/dataset/wfp-geonode-ica-philippines-flood-risk
# 
# It is currently stored in this folder as a .zip, which we will unzip using the command-line `unzip` command with the argument `-d` to provide a destination folder name for the unzipped files.

# In[3]:


get_ipython().system('unzip phl_ica_floodrisk_geonode_mar2014.zip -d philippines_flood_risk')


# In[3]:


# path to shapefile
filepath = "philippines_flood_risk/phl_ica_floodrisk_geonode_mar2014.shp"

# Read file using gpd.read_file()
data = gpd.read_file(filepath)


# In[4]:


data.head() #look at top entries - looks like a pandas dataframe


# In[5]:


data.columns


# In[6]:


# Note the column 'geometry' is full of shapely Polygon objects
type(data['geometry'].iloc[0])


# Note that the data are in (lon, lat) ordering --- this is because the convention is (x, y) for computers, but (lat, lon) for coordinates. This is a frequent cause of error.

# In[7]:


data['geometry']


# In[8]:


# geopandas adds useful attributes to the geodataframe, such as the ability to get bounds
# of all the geometry data
data.bounds


# In[9]:


# similary, we can get attributes such as boundary
data.boundary


# ## Coordinate reference systems
# 
# There are many different coordinate reference systems (CRS), which refer to different ways of indicating where on the earth you are referring to when you give a coordinate. Different CRS use different models of the earth's surface, map projections, units, and origin points (where 0,0 is). The discussion of the specifics is beyond the scope of this course. 
# 
# For the purposes of this course, we will primarily use the two following:
# 
# ### WGS 84: https://epsg.io/4326
# ```
# The CRS used by the GPS system
# units: degrees
# 0,0 is the intersection of greenwich meridian and equator
# epsg code: 4326
# ```
# 
# ### Web Mercator: https://epsg.io/3857
# ```
# The CRS used by most web maps, such as Google maps, OSM, Bing, etc.
# Not accurate at high latitudes >85 degrees, <-85 degrees
# units: meters
# 0,0 is intersection of greensich meridian and equator
# epsg code: 3857
# ```
# 

# In[10]:


data.crs


# In[11]:


# area will warn you if you're trying to do area calculations in geographic CRS
data.area


# In[12]:


data_in_3857 = data.to_crs('epsg:3857')
data_in_3857.area


# ## Exercises
# Using the polygon objects in the `geometry` column of the data frame:
# - create a new column called `area` which represent the areas of each row in the shapefile
# - What are the max, min, median, and quartiles values of the areas?

# In[ ]:





# ## Plotting
# Geopandas provides a useful `.plot()`  function which creates a matplotlib figure and returns an axes object.
# 
# There's a ton of additional libraries that provide more plotting functionality, and we'll explore a few of them here. There's no "correct" set of libraries to use for GIS in python, and it's up to you to figure out which ones fit the best into your workflow.
# 
# The `cmap` option to the `.plot()` function allows you to pass in a [matplotlib colormap name](https://matplotlib.org/gallery/color/colormap_reference.html), which are collections of colors used to visualize data

# In[14]:


# we can use the built-in geopandas plot function to visualize
ax = data.plot(figsize=(10,5), alpha=0.6, cmap='Set2')


# currently the colors are assigned arbitrarily. However, we can also use colors to encode information. 
# 
# Let's first use colors to categorize by endangerment status. To do so, we pass the `column` argument to `plot()`. For reference, we also set `legend=True`

# In[15]:


ax = data.plot(figsize=(10,10), alpha=0.6, cmap='Set2', column='FloodText', legend=True)


# Another common use of colors to encode data is to represent numerical data in an area with colors. This is known as a [choropleth](https://en.wikipedia.org/wiki/Choropleth_map).
# 
# Let's use this to encode the areas of each region

# In[16]:


#then pass the area column as an argument
ax = data.plot(figsize=(10,5), alpha=0.6, cmap='Reds', column='FloodClass', legend=True)

# adding a title to the map
ax.set_title('Flood Classes in the Philippines', fontsize=15)

# adding labels to the axes
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)

plt.show()


# The data by itself looks just like a bunch of blobs. Let's put it on a map for context
# 
# [Contextily](https://github.com/geopandas/contextily) is a library for creating basemaps. It pulls data from a host of different basemap providers - see [documentation](https://contextily.readthedocs.io/en/latest/) for more details.
# 

# In[17]:


# the data is currently in WGS84 (epsg:4326)
data.crs


# In[18]:


ax = data.plot(figsize=(10,8), column='FloodText', legend=True) 
# now we add a basemap. ctx finds a basemap for a background from
# an online repository.
# It assumes the data is in web mercator (epsg:3857) unless you specify otherwise
ctx.add_basemap(ax, crs=data.crs, source=ctx.providers.Gaode.Normal)


# In[19]:


# we can set bounds using matplotlib
ax = data.plot(figsize=(10,5), cmap='Set2', column='FloodText')
ax.set_xlim([115,130])
ax.set_ylim([-0,25])
ctx.add_basemap(ax, crs=data.crs, source=ctx.providers.OpenStreetMap.Mapnik)


# We can use different background styles:
# ![tile styles](https://contextily.readthedocs.io/en/latest/_images/tiles.png).
# 
# Note that some styles only contain labels or lines.

# In[20]:


# to look at all of the different providers, check:
ctx.providers


# previews of the different basemap styles can be viewed at: http://leaflet-extras.github.io/leaflet-providers/preview/ 

# In[21]:


ax = data.plot(figsize=(10,5), alpha=0.6, column='FloodText', legend=True)
# to specify the type of basemap, specify the source argument
# the syntax is ctx.providers.{provider name}.{provider style}
ctx.add_basemap(ax, crs=data.crs, source=ctx.providers.Gaode.Normal)
# you can add labels independently of the background
ctx.add_basemap(ax, crs=data.crs, source=ctx.providers.CartoDB.DarkMatterOnlyLabels)


# In[22]:


# we can download background tiles as images for quicker loading (don't need to keep redownloading)
# let's use the bounds of the dataframe
w,s,e,n = data.total_bounds
data.total_bounds


# the function bounds2img takes coordinates and [zoom level](https://wiki.openstreetmap.org/wiki/Zoom_levels) and downloads the corresponding tiles of the map as images

# In[23]:


img, ext = ctx.bounds2img(w, s, e, n, 6, ll=True, source=ctx.providers.Gaode.Normal) #ll means coordinates are in lat-lon
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.imshow(img, extent=ext)
# bounds2img returns things in epsg:3857, so we need to plot the data in the same crs
data.to_crs(epsg=3857).plot(ax=ax, cmap='Set3', alpha=0.8)
ax_bounds = data.to_crs(epsg=3857).total_bounds
ax.set(xlim=[ax_bounds[0], ax_bounds[2]],ylim=[ax_bounds[1], ax_bounds[3]])
plt.axis('off')
plt.savefig('watercolor_example.png')


# ## Explore Interface
# Geopandas also as an interactive interface for plotting maps using the `.explore()` function. The interface uses [folium](https://python-visualization.github.io/folium/) to plot an interactive map.
# 
# For full documentation on the `.explore()` function, see https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html

# In[24]:


# choose a column to visualize by passing in the column name
m = data.explore('FloodClass')
m # folium map object


# You can set the basemap using the `tiles` keyword argument and providing an [xyzproviders](https://xyzservices.readthedocs.io/en/stable/api.html#xyzservices.TileProvider) TileProvider. 
# 
# See the gallery preview of all available providers [here](https://xyzservices.readthedocs.io/en/stable/gallery.html). Note that some require an API key with the given provider

# In[26]:


import xyzservices.providers as xyz
xyz


# In[27]:


data.explore('FloodClass', tiles=xyz.CartoDB.Voyager)


# You can plot multiple layers of data onto the same map by passing the `folium` object into the `m=` keyword argument of `.explore()`. We will use another dataframe of health site locations in the philippines as our second layer.

# In[28]:


health_sites_gdf = gpd.read_file('philippines_healthsites.geojson', driver='GeoJSON')
health_sites_gdf


# In[29]:


# note that .explore() doesn't like timestamp objects
health_sites_gdf.explore()


# In[30]:


health_sites_gdf.dtypes


# In[31]:


# we can cast that column to string to get around it
health_sites_gdf['changeset_timestamp'] = health_sites_gdf['changeset_timestamp'].astype(str)


# In[32]:


# plotting both on the same folium map
m = data.explore('FloodClass', tiles=xyz.CartoDB.Voyager)
# you can select just a subset of columns to include
m = health_sites_gdf[['name',
                      'amenity',
                      'addr_street',
                      'addr_city',
                      'addr_postcode',
                      'healthcare',
                      'geometry']].explore(m=m)
m


# In[36]:


# you can set the dimensions of a map by creating a 
# folium object to initially draw on
data_centroid = data.dissolve().centroid.values[0] # dissolve combines all the geometries into one collection
m = folium.Map(location=(data_centroid.y, data_centroid.x),
               zoom_start=5,
                height=600, width=500) # in pixels
m = data.explore('FloodClass',
                 tiles=xyz.CartoDB.Voyager,
                 m=m,
                 name='Flood Class')
# you can select just a subset of columns to include
m = health_sites_gdf[['name',
                      'amenity',
                      'addr_street',
                      'addr_city',
                      'addr_postcode',
                      'healthcare',
                      'geometry']].explore(m=m,
                                          name='healthcare') # name of layer
# add a layer control menu
folium.LayerControl().add_to(m)
m


# ## Writing to a different file
# 
# First we'll make a directory for outputting data to. We use the `mkdir` command which makes an empty folder. The `-p` option will skip it if the directory already exists

# In[15]:


get_ipython().system('mkdir output_data -p')


# In[16]:


# let's write the first 20 rows of the shapefile to a new file
outfp = "output_data/data_selection.json"

# Select first 20 rows
selection = data[0:20]

# Write those rows into a new file - we will use the GeoJSON file type
selection.to_file(outfp, driver='GeoJSON')


# ## Converting shapes to GeoDataFrames
# You can use Shapely geometric objects to create a GeoDataFrame from scratch. 

# In[37]:


# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()

# add a geometry column (necessary for shapefile)
newdata['geometry'] = None

# Let's see what we have at the moment
print(newdata)


# In[38]:


# Coordinates of the MIT main campus in Decimal Degrees
coordinates = [(-71.092562, 42.357602), ( -71.080155, 42.361553), ( -71.089817, 42.362584), (-71.094688, 42.360198)]

# Create a Shapely polygon from the coordinate-tuple list
poly = Polygon(coordinates)

# Let's see what we have
poly


# In[39]:


# Insert the polygon into 'geometry' -column at index 0
newdata.loc[0, 'geometry'] = poly
newdata


# In[40]:


newdata.loc[0, 'location'] = 'MIT main campus'
newdata


# Before exporting the data it is necessary to set the coordinate reference system (projection) for the GeoDataFrame. 

# In[41]:


# Set the GeoDataFrame's coordinate system to WGS84 (i.e. epsg code 4326)
newdata = newdata.set_crs('epsg:4326')

# Let's see how the crs definition looks like
newdata.crs


# In[42]:


outfp = "output_data/MIT_campus.shp"

# Write the data into that Shapefile
newdata.to_file(outfp)


# In[43]:


# Let's plot it
ax = newdata.to_crs(epsg=3857).plot(figsize=(10,5),alpha = 0.5, color='#FF55FF')
ctx.add_basemap(ax, source=xyz.CartoDB.Voyager)
ax.set_axis_off() # remove the x-y axes
plt.savefig('MIT_main_campus_poly.png')


# # Exercise
# Find an interesting GIS dataset and:
# - visualize some raw data
# - ask an interesting analysis question about it:
#   - intersections, sizes, quantities
#   - relationships
#   - e.g. which latitudes contain the most endangered species? what countries have the most ports per km of coastline?
# - Visualize some of your analysis
# You can use the location you've chosen for your location fan-cam as a place of interest! 
# 
# Note that since geopandas is built on pandas, all of your knowledge from pandas should also carry over!
# 
# As per usual, we'll ask a few volunteers to present their results.
# 
# Here are some resources to look for GIS datasets:
# - Cambridge, MA GIS data: http://cambridgegis.github.io/gisdata.html
# - Awesome GIS data: https://github.com/sshuair/awesome-gis#data
# - Humanitarian Data Exchange: https://data.humdata.org/
# - Data.gov: https://www.data.gov/
# Search for GeoJSON and/or Shapefile file types.
# 
# One tool to help draw GIS polygons is https://geojson.io; you can export your polygon as a geojson and upload it to your jupyter instance to access from jupyter.

# In[ ]:





# ### Covid-19 Resources
# For those interested in how GIS can be used to analyze the pandemic, here are some ideas and data:
# 
# *   Visualize raw data collected from sources around the world about the state of the pandemic
# *   Explore connections between various factors and come up with a hypothesis for your research. Some ideas could be connecting COVID data in different counties to socioeconomy, age, or building architecture data. Remember, mapping data speaks louder than graphs or datasets.
# *   Present your findings to the rest of the class and come up with a possible solution to the problem or connection that you explored
# 
# COVID-19 Datasets:
# * COVID-19 Dataset (Kaggle): www.kaggle.com/imdevskp/corona-virus-report
# * New York Times Dataset: https://github.com/nytimes/covid-19-data
# * JHU Dataset: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data
# *  Feel free to explore more area specific datasets or datasets which outline other conditions. These are just suggestions.
# 
# To make your research connections, be sure to explore population and demographic datasets of different counties around the country. Be creative with your research!
