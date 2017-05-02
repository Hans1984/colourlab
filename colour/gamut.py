#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gamut: Colour metric functions. Part of the colour package.

Copyright (C) 2013-2016 Ivar Farup, Lars Niebuhr,
Sahand Lahafdoozian, Nawar Behenam, Jakob Voigt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
import scipy as sci
import colour.data as data

class Gamut:
    """Class for representing colour gamuts computed in various colour spaces.
    """
    def __init__(self, sp, points, gamma=1, center=None):
        """Construct new gamut instance and compute the gamut. To initialize the hull with the convex hull method,
        set gamma != 1, and provide the center for expansion.

        :param sp : colour.Space
            The colour space for computing the gamut.
        :param points : colour.Data
            The colour points for the gamut.
        :param gamma : float
            Decides how much the points are expanded when using modified convex hull initializing.
        :param center : ndarray
            The gamut center. If one is note provided, the geometric center of the points is used.
        """

        self.data = points       # The data points are stored in the original format. Use hull.points for actual points.
        self.space = sp
        self.hull = None         # Initialized by initialize_(modified)convex_hull
        self.vertices = None     # Initialized by initialize_(modified)convex_hull
        self.simplices = None    # Initialized by initialize_(modified)convex_hull
        self.neighbors = None    # Initialized by initialize_(modified)convex_hull
        self.center = None       # Initialized by initialize_(modified)convex_hull

        if gamma == 1:
            self.initialize_convex_hull()
        else:
            self.initialize_modified_convex_hull(gamma, center)
        self.fix_orientation()

    def initialize_convex_hull(self):
        """Initializes the gamuts convex hull in the desired colour space

        :param sp : Space
            The colour space for computing the gamut.
        :param points : Data
            The colour points for the gamut.
        """
        # Calculate the convex hull
        self.hull = spatial.ConvexHull(self.data.get_linear(self.space), qhull_options='QJ')
        self.vertices = self.hull.vertices
        self.simplices = self.hull.simplices
        self.neighbors = self.hull.neighbors
        self.center = self.center_of_mass(self.get_coordinates(self.vertices))

    def initialize_modified_convex_hull(self, gamma, center):
        """Initializes the gamut with the modified convex hull method.

        Thanks to Divakar from stackoverflow.
        http://stackoverflow.com/questions/42763615/proper-python-way-to-work-on-
        original-in-for-loop?noredirect=1#comment72645178_42763615

        :param gamma: float
            The exponent for modifying the radius.
        :param center: ndarray
            Center of expansion.
        """
        # Move all points so that 'center' is origin
        n_data = self.data.get_linear(self.space)
        n_data_backup = n_data                          # Save a copy of the points, unmodified.

        if center is None:
            self.center = self.center_of_mass(n_data)   # If a center was provided, use it.
        else:
            self.center = center                        # If not, use the geometric center as a default.

        shifted = n_data - center                               # Make center the local origin
        r = np.linalg.norm(shifted, axis=1, keepdims=True)      # Get the radius of all points
        n_data = shifted * (r ** gamma / r)                     # Modify the radius.

        # Calculate the convex hull, with the modified radius's
        self.hull = spatial.ConvexHull(n_data)      # Set indexes from modified points.
        self.vertices = self.hull.vertices          # Set indexes from modified points.
        self.simplices = self.hull.simplices        # Set indexes from modified points.
        self.neighbors = self.hull.neighbors        # Set indexes from modified points.
        self.center = center
        self.hull.points = n_data_backup

    def is_inside(self, sp, c_data, t=False):
        """For the given data points checks if points are inn the convex hull

        :param sp : colour.Space
            The colour space for computing the gamut.
        :param c_data : colour.Data
            Data object with the colour points for the gamut.
        :param t : boolean
            True if use the traverse method, false if use the flatten method.
        :return ndarray
            A array shape(c_data.get()-1) which contains True for each point included in the convexHull, else False.
        """

        if t:
            nd_data = c_data.get(sp)                            # Get the data points as ndarray.

            if nd_data.ndim == 1:                               # If only one point was sent.
                return np.array([self.feito_torres(nd_data)])   # Returns 1d boolean-array.

            else:
                indices = np.ones(nd_data.ndim - 1, int) * -1        # Initialize with negative numbers.
                bool_array = np.zeros(np.shape(nd_data)[:-1], bool)  # Create a bool-array with the same shape as the.
                self.traverse_ndarray(nd_data, indices, bool_array)  # nd_data(minus the last dimension).

                return bool_array                              # Returns the boolean array.
        else:
            shape = c_data.get(sp).shape[:-1]                   # Nx...xMx3 color data needs Nx..xM bool array.
            bool_array = np.zeros(shape, bool)                  # Create a bool array for storing the results.
            bool_array = bool_array.flatten()

            n_data = c_data.get_linear(sp)

            for i in range(0, bool_array.shape[0]):  # Call feito
                bool_array[i] = self.feito_torres(n_data[i])

            bool_array = bool_array.reshape(shape)    # Reshape (without last dimension)
            return bool_array

    def traverse_ndarray(self, n_data, indices, bool_array):
        """For the given data points recursively traverse the dimensions to check if points are inn the convexhull.

        :param n_data : ndarray
            An n-dimensional array containing the remaining dimensions to iterate.
        :param indices : array
            The dimensional path to the coordinate.
            Needs to be as long as the (amount of dimensions)-1 in nda and filled with -1's
        :param bool_array : ndarray
            Array containing true/false in last dimension.
        """
        if np.ndim(n_data) != 1:                            # Not yet reached a leaf node
            curr_dim = 0
            for index in np.nditer(indices):                # calculate the dimension number witch we are currently in
                if index != -1:                             # If a dimension is previously iterated the cell will
                    curr_dim += 1                           # have been changed to a non-negative number.

            numb_of_iterations = 0
            for nda_minus_one in n_data:                       # Iterate over the length of the current dimension
                indices[curr_dim] = numb_of_iterations      # Update the path in indices before next recursive call
                self.traverse_ndarray(nda_minus_one, indices, bool_array)
                numb_of_iterations += 1
            indices[curr_dim] = -1                          # should reset the indices array when the call dies

        else:                                               # We have reached a leaf node
            bool_array[(tuple(indices))] = self.feito_torres(n_data)  # Set the boolean array to returned boolean.

    def feito_torres(self, q):
        """ Tests if a point q is inside the Gamut(general polyhedra)

            :param q: ndarray
                Point to be tested for inclusion.
            :return: bool
                True if q is included in the Gamut.
            """
        inclusion = 0
        v_plus = []     # a list of vertices who's original edge contains P, and it's face is POSITIVE oriented
        v_minus = []    # a list of vertices who's original edge contains P, and it's face is NEGATIVE oriented
        origin = np.array([0., 0., 0.])

        for face in self.simplices:                         # Iterate through all the Gamuts facets.
            facet = self.get_coordinates(face)
            a = facet[0]
            b = facet[1]
            c = facet[2]

            s_t = self.sign(np.array([origin, a, b, c]))    # sign of the face's original tetrahedron
            s_nt = s_t*-1
            signs = np.zeros(4)                             # array for indexing the sign values
            zeros = 0

            # Check if q sees the same side of the tetrahedron's facets as origin does. If this is not true,
            # point is not inside.
            signs[0] = self.sign(np.array([q, a, b, c]))
            if signs[0] == s_nt:
                continue
            signs[1] = self.sign(np.array([q, a, c, origin]))
            if signs[1] == s_nt:
                continue
            signs[2] = self.sign(np.array([q, a, origin, b]))
            if signs[2] == s_nt:
                continue
            signs[3] = self.sign(np.array([q, b, origin, c]))
            if signs[3] == s_nt:
                continue

            for i in range(0, 3):
                if signs[i] == 0:             # If sign[i] is zero, q is on the corresponding face of the facet's
                    zeros += 1                # original tetrahedron.

            if signs[0] == 0:                 # True if q is on the current facet.
                return True

            elif zeros == 0:                  # Tetrahedra.
                inclusion += s_t

            elif zeros == 1:                  # Triangle.
                inclusion += 0.5*s_t

            elif zeros == 2:                  # Line.
                inclusion += 0.5*s_t

                if signs[1] == 0 and signs[2] == 0:         # Intersection point is on line is between A and O
                    if s_t > 0 and np.in1d(face[0], v_plus):
                        v_plus.append(face[0])
                        inclusion += s_t
                    elif s_t < 0 and np.in1d(face[0], v_minus):
                        v_minus.append(face[0])
                        inclusion += s_t
                elif signs[1] == 0 and signs[3] == 0:       # Intersection point is on line is between B and O
                    if s_t > 0 and np.in1d(face[1], v_plus):
                        v_plus.append(face[1])
                        inclusion += s_t
                    elif s_t < 0 and np.in1d(face[1], v_minus):
                        v_minus.append(face[1])
                        inclusion += s_t
                elif signs[2] == 0 and signs[3] == 0:       # Intersection point is on line is between C and O
                    if s_t > 0 and np.in1d(face[2], v_plus):
                        v_plus.append(face[2])
                        inclusion += s_t
                    elif s_t < 0 and np.in1d(face[2], v_minus):
                        v_minus.append(face[2])
                        inclusion += s_t

        if inclusion > 0:
            return True
        else:
            return False

    def fix_orientation(self):
        """Fixes the orientation of the facets in the hull, so their normal vector points outwards.
        """

        c = self.center_of_mass(self.get_coordinates(self.vertices))

        for simplex in self.simplices:
            facet = self.get_coordinates(simplex)
            normal = np.cross((facet[1] - facet[0]), facet[2] - facet[0])  # Calculate the facets normal vector.
            if np.dot((facet[0]-c), normal) < 0:            # If the dot product of 'normal' and a vector from the
                                                            # center of the gamut to the facet is negative, the
                                                            # orientation of the facet needs to be fixed.
                a = simplex[2]
                simplex[2] = simplex[0]
                simplex[0] = a

    @staticmethod
    def sign(t):
        """ Calculates the orientation of the tetrahedron.

        :param t: ndarray
            shape(4,3) The four coordinates of the tetrahedron who's signed volume is to be calculated
        :return: int
             1 if tetrahedron is POSITIVE orientated(signed volume > 0)
             0 if volume is 0
            -1 if tetrahedron is NEGATIVE orientated(signed volume < 0)
        """

        matrix = np.array([  # Creating the matrix for calculating a determinant, representing
                           [t[0, 0], t[1, 0], t[2, 0], t[3, 0]],  # the signed volume of the t.
                           [t[0, 1], t[1, 1], t[2, 1], t[3, 1]],
                           [t[0, 2], t[1, 2], t[2, 2], t[3, 2]],
                           [1, 1, 1, 1]])
        return int(np.sign(sci.linalg.det(matrix)))*-1  # Calculates the signed volume and returns its sign.

    def get_coordinates(self, indices):
        """Return the coordinates of the points correlating to the the indices provided.

        :param indices: ndarray
            shape(N,), list of indices
        :return: ndarray
            shape(N, 3)
        """
        return self.hull.points[indices]

    def in_tetrahedron(self, t, p, true_interior=False):
        """Checks if the point P, pointed to by vector p, is inside(including the surface) the tetrahedron
            If 'p' is not guaranteed a true tetrahedron, use interior().

        :param t: ndarray
            The four points of a tetrahedron
        :param p: ndarray
            The point to be tested for inclusion in the tetrahedron.
        :param true_interior: bool
            Activate to exclude the surface of the tetrahedron from the search.
        :return: Bool
            True if q is inside or on the surface of the tetrahedron.
        """

        # If the surface is to be excluded, return False if p is on the surface.
        if true_interior and (self.in_triangle(np.delete(t, 0, 0), p) or
                              self.in_triangle(np.delete(t, 1, 0), p) or
                              self.in_triangle(np.delete(t, 2, 0), p) or
                              self.in_triangle(np.delete(t, 3, 0), p)):
            return False

        # Check if 'p' is in the tetrahedron.
        hull = spatial.Delaunay(t)    # Generate a convexHull representation of the points
        return hull.find_simplex(p) >= 0        # return True if 'p' is a vertex.

    @staticmethod
    def in_line(line, q, true_interior=False):
        """Checks if a point P is on the line segment AB.

        :param line: ndarray
            line segment from point A to point B
        :param q: ndarray
            Vector from A to P
        :return: Bool
        :param true_interior: bool
            Set to True if you want to exclude the end points in the search for inclusion.
        :return: Bool
            True is P in in the line segment from A to P.
        """
        if true_interior and (tuple(q) == tuple(line[0]) or tuple(q) == tuple(line[1])):
            return False

        b = line[1] - line[0]   # Move the line so that A is (0,0,0). 'b' is the vector from A to B.
        p = q - line[0]         # Make the same adjustments to the points. Copy to not change the original q

        # Check if the cross b x p is 0, if not the vectors are not collinear.
        matrix = np.array([[1, 1, 1], b, p, ])
        if np.linalg.det(matrix) != 0:
            return False

        # Check if b and p have opposite directions
        dot_b_p = np.dot(p, b)
        if dot_b_p < 0:
            return False

        # Finally check that p-vector is than shorter b-vector
        if np.linalg.norm(p) > np.linalg.norm(b):
            return False

        return True

    def in_triangle(self, triangle, q, true_interior=False):
        """Takes three points of a triangle in 3d, and determines if the point w is within that triangle.
            This function utilizes the baycentric technique explained here
            https://blogs.msdn.microsoft.com/rezanour/2011/08/07/barycentric-coordinates-and-point-in-triangle-tests/

        :param triangle: ndarray
            An ndarray with shape: (3,3), with points A, B and C being triangle[0]..[2]
        :param q: ndarray
            An ndarray with shape: (3,), the point to be tested for inclusion in the triangle.
        :param true_interior: bool
            If true_interior is set to True, returns False if 'P' is on one of the triangles edges.

        :return: bool
            True if 'w' is within the triangle ABC.
        """

        # If the true interior option is activated, return False if 'q' is on one of the triangles edges.
        if true_interior and (self.in_line(triangle[0:2], q) or
                              self.in_line(triangle[1:3], q) or
                              self.in_line(np.array([triangle[0], triangle[2]]), q)):
            return False

        # Make 'A' the local origin for the points.
        b = triangle[1] - triangle[0]  # 'b' is the vector from A to B
        c = triangle[2] - triangle[0]  # 'c' is the vector from A to C
        p = q - triangle[0]            # 'p' is now the vector from A to the point being tested for inclusion

        # If triangle is actually a line. It is treated as a line.
        if np.array_equal(triangle[0], triangle[1]):
            return self.in_line(np.array([triangle[0], triangle[1]]), p)
        if np.array_equal(triangle[0], triangle[2]):
            return self.in_line(np.array([triangle[0], triangle[2]]), p)
        if np.array_equal(triangle[1], triangle[2]):
            return self.in_line(np.array([triangle[1], triangle[2]]), p)

        b_x_c = np.cross(b, c)         # Calculating the vector of the cross product b x c
        if np.dot(b_x_c, p) != 0:      # If p-vector is not coplanar to b and c-vector, it is not in the triangle.
            return False

        c_x_p = np.asarray(np.cross(c, p))          # Calculating the vector of the cross product c x p
        c_x_b = np.asarray(np.cross(c, b))          # Calculating the vector of the cross product c x b

        if np.dot(c_x_p, c_x_b) < 0:    # If the two cross product vectors are not pointing in the same direction. exit
            return False

        b_x_p = np.asarray(np.cross(b, p))          # Calculating the vector of the cross product b x p

        if np.dot(b_x_p, b_x_c) < 0:  # If the two cross product vectors are not pointing in the same direction. exit
            return False

        denom = np.linalg.norm(b_x_c)
        r = np.linalg.norm(c_x_p) / denom
        t = np.linalg.norm(b_x_p) / denom

        return r + t <= 1

    @staticmethod
    def is_coplanar(p):
        """Checks if the points provided are coplanar. Does not handle more than 4 points.

        :param p: ndarray
            The points to be tested
        :return: bool
            True if the points are coplanar
        """
        if p.shape[0] < 4:  # Less than 4 p guarantees coplanar p.
            return True

        # Make p[0] the local origin, and d, c, and d vectors from origin to the other points.
        b = p[1] - p[0]
        c = p[2] - p[0]
        d = p[3] - p[0]

        # Coplanar if the cross product vector or two vectors dotted with the  last vector is 0.
        return np.dot(d, np.cross(b, c)) == 0

    @staticmethod
    def center_of_mass(points):
        """Finds the center of mass of the points given. To find the "geometric center" of a gamut
        lets points be only the vertices of the gamut.

        Thanks to: http://stackoverflow.com/questions/8917478/center-of-mass-of-a-numpy-array-how-to-make-less-verbose

        :param points: ndarray
            Shape(N, 3), a list of points
        :return: center: ndarray
            Shape(3,), the coordinate of the center of mass.
        """
        cm = points.sum(0) / points.shape[0]
        for i in range(points.shape[0]):
            points[i, :] -= cm
        return cm

    def get_vertices(self, nd_data):
        """Get all hull vertices and save them in a array list.

        :param nd_data : ndarray
            Shape(N, 3) A list of points to return vertices from. The a copy of gamut.points pre-converted
            to a desired colour space.
        :return: ndarray
            The coordinates of the requested vertices
        """
        point_list = []                     # Array list for the vertices.

        for i in self.hull.vertices:        # For loop that goes through all the vertices
            point_list.append(nd_data[i])   # and for each goes to the points and adds the coordinate to the list.

        return np.array(point_list)          # Returns ndarray.

    def plot_surface(self, sp, ax):
        """Plot all the vertices points on the received axel

        :param ax: Axel
            The axel to draw the points on
        :param sp: Space
            The colour space for computing the gamut.
        """
        nd_data = self.data.get_linear(sp)              # Creates a new ndarray with points
        points = self.get_vertices(nd_data)             # ndarray with all the vertices
        x = points[:, 0]
        y = points[:, 1]
        z = points[:, 2]

        x.sort()                                        # Sort the value from smallest to biggest value.
        y.sort()
        z.sort()

        for i in range(self.hull.simplices.shape[0]):   # Iterates and draws all the vertices points
            tri = art3d.Poly3DCollection([self.hull.points[self.hull.simplices[i]]])
            ax.add_collection(tri)                      # Adds created points to the ax

        ax.set_xlim([x[0] - (x[0] * 0.20), x[-1] + x[-1] * 0.20])  # Set the limits for the plot by calculating.
        ax.set_ylim([y[0] - (y[0] * 0.20), y[-1] + y[-1] * 0.20])
        ax.set_zlim([z[0] - (z[0] * 0.20), z[-1] + z[-1] * 0.20])
        plt.show()

    def true_shape(self, points):
        """Removes all points in 'points' the does not belong to it's convex polygon.
            Works with 4 or less coplanar points.

        :param points: ndarray
            Shape(N, 3) Points in 3d
        :return: ndarray
            The vertices of a assuming it is supposed to represent a convex shape
        """

        # Remove duplicate points.
        uniques = []  # Use list while removing
        for arr in points:
            if not any(np.array_equal(arr, unique_arr) for unique_arr in uniques):
                uniques.append(arr)
        uniques = np.array(uniques)              # Convert back to ndarray.

        if uniques.shape[0] < 3:                 # one or two unique points are garaunteed a point or line.
            return uniques

        if uniques.shape[0] == 3:                # If we have 3 points, they are either a triangle or a line.
            i = 0
            while i < 3:
                a = np.delete(uniques, i, 0)
                if self.in_line(a, uniques[i]):  # If a point is on the line segment between two other points
                    return a                     # Return that line segment.
                i += 1
            return uniques                       # Guaranteed to be a triangle.

        i = 0
        while i < 4:
            b = np.delete(uniques, i, 0)
            if self.in_triangle(b, uniques[i]):  # See if any of the points lay inside the triangle formed by the
                return b                         # other points
            i += 1

        return uniques                           # return a convex polygon with 4 vertices

    def in_polygon(self, points, q, true_interior=False):
        """Checks if q is in the polygon formed by pts

        :param points: ndarray
            shape(4, 3). Points on a polygon. Must be coplanar.
        :param q: ndarray
            Point to be tested for inclusion
        :param true_interior: boolean
            Activate to exclude the edges from the search
        :return:
        """
        if true_interior:
            # Divide into two triangles and check their true_interior, and their common edge with is in the true
            # interior or the polygon
            return (self.in_triangle(np.array([points[0], points[1], points[2]]), q, true_interior=True) or
                    self.in_line(np.array([points[1], points[2]]), q, true_interior=True) or
                    self.in_triangle(np.array([points[1], points[2], points[3]]), q, true_interior=True))
        else:
            # Divide in two triangles and see is q is in either.
            return (self.in_triangle(np.array([points[0], points[1], points[2]]), q) or
                    self.in_triangle(np.array([points[1], points[2], points[3]]), q))

    def interior(self, points, q, true_interior=False):
        """ Finds the vertices of pts convex shape, and calls the appropriate function to test for inclusion. 
        Is not designed to work with more than 4 points.
        
        :param points: ndarray
            Shape(n, 3). 0 < n < 5.
        :param q: ndarray
            Point to be tested for inclusion in pts true shape.
        :param true_interior: boolean
            Activate to exclude the edges if pts is actually a triangle or polygon with 4 vertices, or the surface
            if pts is a tetrahedron
        :return: boolean
            True if the point was inside.
        """
        if self.is_coplanar(points):
            true_shape = self.true_shape(points)
            if true_shape.shape[0] == 1:
                return np.allclose(true_shape, q)
            elif true_shape.shape[0] == 2:
                return self.in_line(true_shape, q)
            elif true_shape.shape[0] == 3:
                return self.in_triangle(true_shape, q, true_interior=true_interior)
            elif true_shape.shape[0] == 4:
                return self.in_polygon(true_shape, q, true_interior=true_interior)
            else:
                print("Error: interior received to many points, retuning False")
                return False
        else:
            return self.in_tetrahedron(points, q, true_interior=true_interior)

    @staticmethod
    def get_alpha(q, center, n):
        """Get the Alpha value by computing.

        :param q: ndarray
            The start point.
        :param center: ndarray
            The center is a end point in the color space.
        :param n: ndarray
            The normal and distance value for the simplex
        :return x: float
            Returns alpha value.
        """
        x = (n[3] - center[0] * n[0] - center[1] * n[1] - center[2] * n[2]) / \
            (q[0] * n[0] - center[0] * n[0] + q[1] * n[1] - center[1] * n[1] + q[2] * n[2] - center[2] * n[2])

        return x

    @staticmethod
    def find_plane(points):
        """Find normal point to a plane(simplices) and the distance from p to the cross point.

        :param points: ndarray
            the start point.
        :return n: ndarray
            Returns ndarray with normal points distance. [x, y, z, distance]
        """

        v1 = points[2] - points[0]
        v2 = points[1] - points[0]
        n2 = np.cross(v1, v2)                          # Find cross product of 2 points.
        norm = np.linalg.norm(n2)                      # Find normal point.
        n3 = n2 / norm                                 # Find the distance.

        return np.hstack([n3, np.dot(points[1], n3)])  # Add the distance to numpy array, and return it.

    def intersectionpoint_on_line(self, sp, c_data, center=None):
        """ Returns an array containing the nearest point on the gamuts surface, for every point
            in the c_data object. Cell number i in the returned array corresponding to cell number i from the
            'c_data' parameter. Handles input on the format Nx...xMx3.

        :param sp: colour.space
            The Colour.space
        :param c_data: colour.data.Data
            Colour.data.Data object containing all points.
        :param center : ndarray
            Center point to use when computing the nearest point.
        :return: ndarray
            Shape(3,) containing the nearest point on the gamuts surface.
        """

        if center is None:                          # If no center is defined, use geometric center.
            center = self.center

        re_data = c_data.get_linear(sp)             # Get linearised colour data

        for i in range(0, re_data.shape[0]):        # Do get_nearest_point_on_line
            re_data[i] = self.get_nearest_point_on_line(sp, re_data[i], center)

        return data.Data(sp, np.reshape(re_data, c_data.sh))

    def get_nearest_point_on_line(self, sp, q, center):
        """Finding the Nearest point along a line.

        :param sp: Space
            The colour space for computing the gamut.
        :param q: ndarray
            The start point.
        :param center: ndarray
            The center is a end point in the color space.
        :return: ndarray
            Returns the nearest point.
        """

        new_points = self.data.get_linear(sp)          # Converts gamut to new space
        alpha = []                                     # a list for all the alpha variables we get
        for i in self.hull.simplices:                  # Loops for all the simplexes
            points = []                                # A list for all the points coordinates
            for m in i:                                # Loops through all the index's and find the coordinates
                points.append(new_points[m])
            point = np.array(points)                   # converts to numpy array
            n = self.find_plane(point)                 # Find the normal and distance
            x = self.get_alpha(q, center, n)           # Finds the alpha value
            if 0 <= x <= 1:                            # If alpha between 0 and 1 it gets added to the alpha list
                if self.in_triangle(point, self.line_alpha(x, q, center)):  # And if its in the triangle to
                    alpha.append(x)
        a = np.array(alpha)
        np.sort(a, axis=0)

        a.sort()
        nearest_point = self.line_alpha(a[-1], q, center)

        return nearest_point

    @staticmethod
    def line_alpha(alpha, q, center):
        """Equation for calculating the nearest point.

        :param alpha: float
            The highest given alpha value
        :param q: ndarray
            The start point.
        :param center: ndarray
            The center is a end point in the color space.
        :return: ndarray
            Return the nearest point.
        """
        return alpha * np.array(q) + center - alpha * np.array(center)  # finds the coordinates for the nearest point

    def compress_axis(self, sp, c_data, ax):
        """ Compresses the points linearly in the desired axel and colour space.

        :param sp: colour.space
            The colour space to work in.
        :param c_data: colour.data.Data
            The points to be compressed.
        :param ax: int
            Integer representing which axis to do the compressing.
        :return: colour.data.Data
            Returns a colour.data.Data object with the new points.
        """

        shape = c_data.get(sp).shape   # Save the original shape of the points.
        points = c_data.get_linear(sp)
        p_min = 9001
        p_max = 0

        for p in points:               # Finding the min and max values along given axis of the points to be compressed.
            if p[ax] > p_max:
                p_max = p[ax]
            elif p[ax] < p_min:
                p_min = p[ax]

        g_points = self.get_coordinates(self.vertices)  # Using only vertices to find min and max points of the gamut.
        g_min = 9001
        g_max = 0

        for p in g_points:              # Finding the min and max values along given axis of the points in the gamut.
            if p[ax] > g_max:
                g_max = p[ax]
            if p[ax] < g_min:
                g_min = p[ax]

        delta_p = p_max - p_min         # Calculating the delta values.
        delta_g = g_max - g_min

        b = delta_g / delta_p           # The slope of the line bx + a
        a = g_min - b * p_min           # Finding start value for the line

        for i in range(0, points.shape[0]):          # For every point.
            points[(i, ax)] = b*points[(i, ax)] + a  # Compress the coordinates along the given axis.

        return data.Data(sp, points.reshape(shape))  # Return the points as a colour.data.Data object.

    def clip_nearest(self, sp, c_data):
        """ For each point in c_data return the nearest point on the gamut surface.
        
        :param sp: colour.Space
            A colour space
        :param c_data: colour.Data
            A colour.Data object with the points to use.
        :return:  colour.Data
        """
        # Get linearised colour data
        re_data = c_data.get_linear(sp)

        # Do get_nearest_point_on_line
        for i in range(0, re_data.shape[0]):
            re_data[i] = self.get_clip_nearest(sp, re_data[i])

        return data.Data(sp, np.reshape(re_data, c_data.sh))

    def get_clip_nearest(self, sp, p_outside):
        """ Finds the nearst point in 3D
        
        :param sp: colour.Space
            The colour space for computing the gamut.
        :param p_outside: ndarray
            The start point.
        :return: ndarray
            Returns the nearest point.
        """
        gam = self.data.get_linear(sp)                      # Converts gamut to new space
        new_dis = 9001                                      # High value for use in the if
        point = None

        for i in self.vertices:                             # Goes through all the vertices to find the closest
            distance = np.linalg.norm(p_outside - gam[i])   # Finds the distance for the vertices
            if distance < new_dis:                          # If distance is shorter than previous distance
                new_dis = distance                          # Adds value for new distance
                point_index = i                             # Index for the point
                point = gam[i]                              # Coordinates for the new point

        neighbors = []                                      # List for all the neighbors
        for j in self.simplices:                            # Goes through all the simplices
                                                            # If the simplex has the vertices as a side
            if point_index == j[0] or point_index == j[1] or point_index == j[2]:
                neighbors.append(self.get_coordinates(j))

        a = -9001
        for simplex in neighbors:                           # Goes through all the neighbors
            n = self.find_plane(simplex)                    # Finds normal and distance
            a_new = -n[3] + np.dot(p_outside, n[:3])        # Finds new alpha value
            if np.absolute(a) > np.absolute(a_new):         # If the alpha value is less than the old value
                point_on_plane = (p_outside - a_new * n[:3])    # we find the intersection point
                # If the point is in triangle we return the point
                if self.in_triangle(simplex, point_on_plane):
                    point = point_on_plane

        return point                                    # If we found no points that is in triangle we return the vertex

    def minDE(self, c_data):
        """

        :param c_data: colour.data.Data
            Colour.data.Data object containing all points.
        :return: ndarray
            Returns the nearest point.
        """
        # Colour data in cielab.
        sp = data.space.cielab

        # Get linearised colour data
        re_data = c_data.get_linear(sp)

        # Returns true/fals for points inside/outside as bool array.
        check_data = self.is_inside(sp, c_data)

        # Do get_nearest_point_on_line
        for i, value in np.ndenumerate(check_data):
            if not check_data[i]:
                re_data[i] = self.get_clip_nearest(sp, re_data[i])

        return data.Data(sp, re_data)
