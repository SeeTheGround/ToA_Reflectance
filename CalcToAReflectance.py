"""
    CalcToAReflectance.py version: 0.3 (7 December 2020), Last Updated: 7 December 2020 by: David J. Cartwright davidcartwright@hotmail.com
        Created and tested on ArcPro 2.6.2

    https://github.com/SeeTheGround/ToA_Reflectance

    This script calculates the Top of Atmosphere Reflectance of LANDSAT8 Images(Bands) by getting the parameters from an MTL File; OPtionaly scales the results; saves the file and adds to the current map.
    
"""

P_RASTER = 0            # Raster File [Raster] - Path to target Raster
P_BAND = 1              # Raster File's Band [Long] - Band represented by LANDSAT8 Raster File
P_MTL_FILE = 2          # Meta Data File [File] - Path to target's MetaData (MTL File)
P_OUTPUT_LOCATION = 3   # Output Location
P_RESCALE = 4   # Output Location

raster = arcpy.GetParameter(P_RASTER)
raster = raster.value
band = arcpy.GetParameter(P_BAND)
meta_data_file = arcpy.GetParameter(P_MTL_FILE)
meta_data_file = meta_data_file.value
output_location = arcpy.GetParameter(P_OUTPUT_LOCATION)
rescale = arcpy.GetParameter(P_RESCALE)

arcpy.env.workspace = output_location

sun_elevation = "SUN_ELEVATION"
ref_mb_prefix = "REFLECTANCE_MULT_BAND_"
ref_ab_prefix = "REFLECTANCE_ADD_BAND_"

mb_string = ref_mb_prefix + str(band)
ab_string = ref_ab_prefix + str(band)


meta_data = open(meta_data_file, 'r').read()

for line in meta_data.strip().split('\n'):
    if mb_string in line:
        rmb = float(line.split()[2])
    if ab_string in line:
        rab = float(line.split()[2])
    if sun_elevation in line:
        se = math.radians(float(line.split()[2]))
        
arcpy.AddMessage(f"{mb_string}: {rmb}, {ab_string}: {rab}, {sun_elevation}: {se}")

arcpy.AddMessage("Calculating Top of Atmosphere Reflection...")
in_raster = raster
out_raster = ((arcpy.Raster(in_raster) * rmb) + rab) / math.sin(se)

out_raster = arcpy.sa.SetNull(out_raster, out_raster, "VALUE < 0")

if rescale > 0 :
    arcpy.AddMessage("Rescaling Raster")
    out_raster = out_raster * rescale
    

arcpy.AddMessage("Saving Raster")
save_filename = raster.split("\\")[-1][:-4] + "_ToA.TIF"
out_raster.save(save_filename)

arcpy.AddMessage("Adding Raster to current map")
try:
    aprx = arcpy.mp.ArcGISProject('CURRENT')
    activeMap = aprx.activeMap
    activeMap.addDataFromPath(f"{output_location.value}\\{save_filename}")


except:
    arcpy.AddError("Could not add Raster to current map.")