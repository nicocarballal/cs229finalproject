"""
Psuedcode for data processing

Takes shapefile and ...

Read in shapefile
Create dataframe from shapefile
Sort unique fires into separate dataframes
FOR each fire
	Get final and initial dates
	FOR each day of the fire
		FOR each polygon of the fire
			IF polygon was active during that day
				Append to polygon list
		Create MultiPolygon using polygon list
		Append day and MutliPolygon to new data structure
	Get centriod of first day MultiPolygon
	Assign origin column to data structure with centroid coords
	Normalize all Multiplygon points by origin
	Append completed data structure to new fire list


"""