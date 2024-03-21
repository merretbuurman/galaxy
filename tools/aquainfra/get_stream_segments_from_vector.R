
# Get command line arguments, passed by python
args <- commandArgs(trailingOnly = TRUE)
print(paste0('R Command line args: ', args))
in_path = args[1]
layer_name = args[2]
subc_id = args[3]
out_path = args[4]

# Call:
# RScript geopackagetool.R /home/mbuurman/workdata/casestudy_saofra/r.stream.order/order_vect_tiles20d/order_vect_segment_h14v08.gpkg merged 166067836 /tmp/out_geopackagetool.geojson

# Reads an entire, or a subset of a GeoPackage vector file from disk either as a table (data.table), as a directed graph object (igraph), a spatial dataframe (sf) or a SpatVect object (terra).

#read_geopackage(
#  gpkg, #     character. Full path of the GeoPackage file.
#  import_as = "data.table", # character. "data.table", "graph", "sf", or "SpatVect".
#  layer_name = NULL, # Name of the specific data layer to import from the GeoPackage. 
#  subc_id = NULL, # Vector of the sub-catchment (or stream segment) IDs in the form of (c(ID1, ID2, ...) for which the spatial objects or attributes of the GeoPackage should be imported. Optional. 
#  name = "stream" # The attribute table column name of the stream segment ("stream"), sub-catchment ("ID"), basin ("ID") or outlet ("ID") column which is used for subsetting the GeoPackage prior importing. Optional.
#)

print('importing library')
library(hydrographr)
#library(geojsonsf)
library(sf)
print('import done')

#path = '/home/mbuurman/workdata/casestudy_saofra/r.stream.order/order_vect_tiles20d/order_vect_segment_h14v08.gpkg'
#import_as = "data.table"
import_as = 'sf'
#layer_name = 'SELECT'
#layer_name = 'merged'
#subc_id = c(166067836)
subc_id = c(as.numeric(subc_id))

print(paste('Will load subc_id', subc_id, 'of layer', layer_name))

gp = read_geopackage(in_path, import_as, layer_name, subc_id)
print('GeoPackage:')
print(gp)
st_write(gp, out_path)


#gj = sf_geojson(gp)
#print('GeoJSON:')
#print(gj)
#print('That was Geojson!')

# write to file!
#st_write(gj, out_path)

print('Finished')