"""
Psuedcode for data processing

Takes shapefile and ...

Read in shapefile
Create dataframe from shapefile
Sort unique fires into separate dataframes
FOR each fire
	Get number of fire days
	FOR each day of the fire
		FOR each row of the fire
			IF row is active during that day
				Append to polygon list
		Create MultiPolygon using polygon list
		Append day and MutliPolygon to new data structure
	Get centriod of first day MultiPolygon
	Assign origin column to data structure with centroid coords
	Normalize all Multiplygon points by origin
	Append completed data structure to new fire list
	

FOR each fire
	Get bounding box of final area
	Determine minimum "pixel" size from smallest difference in coords
	Produce array of discreted longitude and latitude "pixel" points
	Create x array by multiplying number of array coords N by number of fire
		days D. Every N elements of new array should have the date associated
	Create y array of zeros same length as 1st dim of x
	FOR each day of the fire
		FOR each coord in a day
			IF coord is contained by MultiPolygon for that day
				Set y at index to 1


Data for learning
x[i] = [day, long, lat]
y[i] = 0 or 1 (not burning or burning)

"""