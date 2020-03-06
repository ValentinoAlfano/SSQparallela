import pprint
import datetime
# from shapely.geometry import *
import json
# Lettura feed file
# with open('feeds1_n.json') as feed1:
 #       unsorted = json.load(feed1)

# with open(filePoligoni) as polygonData:
 #       polygons = json.load(polygonData)

# Controlla se un punto e o meno in quadratino o poligono


def is_in_Polygon(coordinate_tuple, coordinate_point_tuple):
    """

    :param coordinate_tuple: coordinate dell'area che definiscono il poligono su cui faccio il controllo,vettore di tuple
    :param coordinate_point_tuple: coordinate del punto,tupla
    :return:
    True o False in base al successo o fallimento del controllo
    """

    polygon = Polygon(coordinate_tuple)

    if polygon.contains(Point(coordinate_point_tuple)):
        return True
    else:
        return False


def pnpoly(coordinate_tuple, coordinate_point_tuple):
    i = 0
    j = 0
    c = False
    nvert = len(coordinate_tuple)
    # print(nvert)
    j = nvert-1
    # print(verty[j])
    vertx = []
    verty = []
    testx = coordinate_point_tuple[0]
    testy = coordinate_point_tuple[1]
    for coordinate in coordinate_tuple:
        vertx.append(coordinate[0])
        verty.append(coordinate[1])
    while i < nvert:
        if (((verty[i] > testy) != (verty[j] > testy)) and (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i])):
           c = not c
           # print(c)
        j = i
       # print(i)
        i += 1
       # print(j)
    return c


# is_left(): tests if a point is Left|On|Right of an infinite line.

#   Input: three points P0, P1, and P2
#   Return: >0 for P2 left of the line through P0 and P1
#           =0 for P2 on the line
#           <0 for P2 right of the line
#   See: the January 2001 Algorithm "Area of 2D and 3D Triangles and Polygons"

def is_left(P0, P1, P2):
    return (P1[0] - P0[0]) * (P2[1] - P0[1]) - (P2[0] - P0[0]) * (P1[1] - P0[1])


# wn_PnPoly(): winding number test for a point in a polygon
#     Input:  P = a point,
#             V[] = vertex points of a polygon
#     Return: wn = the winding number (=0 only if P is outside V[])

def wn_PnPoly(P, V):
    wn = 0   # the winding number counter

    # repeat the first vertex at end
    V = tuple(V[:]) + (V[0],)

    # loop through all edges of the polygon
    for i in range(len(V)-1):     # edge from V[i] to V[i+1]
        if V[i][1] <= P[1]:        # start y <= P[1]
            if V[i+1][1] > P[1]:     # an upward crossing
                if is_left(V[i], V[i+1], P) > 0:  # P left of edge
                    wn += 1           # have a valid up intersect
        else:                      # start y > P[1] (no test needed)
            if V[i+1][1] <= P[1]:    # a downward crossing
                if is_left(V[i], V[i+1], P) < 0:  # P right of edge
                    wn -= 1           # have a valid down intersect
    return wn


def Sorting_Areas(polygons, coordinate):

    result = None

    lat = coordinate[0]
    lon = coordinate[1]
    coordinate_tuple_points = (lon, lat)
    check = False

    for feature in polygons['features']:

            coordinate_area = feature['geometry']['coordinates'][0]

            cap = feature['properties']['cap']
            zona = feature['properties']['zona']
            coordinate_tuple = []
            for coordinata in coordinate_area:
                coordinate_tuple.append(tuple(coordinata))
            # pprint.pprint(len(coordinate_tuple))

            # if (is_in_Polygon(coordinate_tuple, coordinate_tuple_points)):
            # if (pnpoly(coordinate_tuple, coordinate_tuple_points)):
            if (wn_PnPoly( coordinate_tuple_points, coordinate_tuple)):
                check = True
                result = cap + " " + zona
                print(result)
            
            if check:
                break
         #  if not check:
         #   result.append(["feeds_out_of_zones"])
    return result
        


def Sorting_AreasKM(squares, coordinate):
    	
    	
    result = None
    lat = coordinate[0]
    lon = coordinate[1]
    coordinate_tuple_points = (lon, lat)
    check = False
    for feature in squares['features']:

            coordinate_area = feature['geometry']['coordinates'][0]
           
            cap = feature['properties']['cap']
            zona = feature['properties']['zona']
            square = feature['properties']['square']
            groups = feature['properties']['group']
            coordinate_tuple = []
            for coordinata in coordinate_area:
                coordinate_tuple.append(tuple(coordinata))
            # pprint.pprint(len(coordinate_tuple)) 
		
	   
   	    	
            # if (is_in_Polygon(coordinate_tuple, coordinate_tuple_points)):
            # if (pnpoly(coordinate_tuple, coordinate_tuple_points)):
            if (wn_PnPoly( coordinate_tuple_points, coordinate_tuple)):
                check = True
                # result = cap + "_" + zona + "_" + str(square)
                new_dict={"cap":cap,"zona":zona,"square":square,"groups":groups}

                print(new_dict)
            if check:
                break
         #  if not check:
         #   result.append(["feeds_out_of_zones"])
    return new_dict
        



