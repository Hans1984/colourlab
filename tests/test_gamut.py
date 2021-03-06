#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gamut: Unittests for all functions in the gamut module.

Copyright (C) 2017 Lars Niebuhr, Sahand Lahafdoozian, Nawar Behenam,
Jakob Voigt, Ivar Farup

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of

GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import numpy as np
# import matplotlib.pyplot as plt                 # Used for test_plot, which is commented out.
from colourlab import data, gamut, space

# Global variables.
cube = np.array([[0., 0., 0.],      # 0  vertices
                [10., 0., 0.],      # 1  vertices
                [10., 10., 0.],     # 2  vertices
                [0., 10., 0.],      # 3  vertices
                [5., 5., 5.],       # 4  non vertices
                [4., 6., 2.],       # 5  non vertices
                [10., 10., 10.],    # 6  vertices
                [1., 2., 3.],       # 7  non vertices
                [10., 0., 10.],     # 8  vertices
                [0., 0., 10.],      # 9  vertices
                [0., 10., 10.]])    # 10 vertices
cube_vertices = np.array([0, 1, 2, 3, 6, 8, 9, 10])  # Vertices for the cube above.

line = np.array([[0, 0, 0], [3, 3, 3]]) # Line used in testing.
point_in_line = np.array([1, 1, 1]) # Point inside the line to be tested.
point_not_in_line = np.array([2, 3, 2]) # Point outside the line to be tested.
point_opposite_direction_than_line = np.array([-1, -1, -1])
point_further_away_than_line = np.array([4, 4, 4])

tetrahedron = np.array([[10., 10., 10.], [0., 10., 0.], [0., 0., 0.], [0., 0., 10.]])  # Tetrahedron used in testing.
tetra_p_inside = np.array([2., 3., 4.])               # Point inside the tetrahedron to be tested.
tetra_p_not_inside = np.array([20., 1., 2.])          # Point outside the tetrahedron to be tested.
tetra_p_on_surface = np.array([0., 5., 0.])


tetrahedron_three = np.array([[10, 10, 10], [10, 10, 0], [10, 0, 10], [0, 10, 10]])     # Tetrahedron used in testing.

# Used in test for is_inside
points_1d = np.array([5., 11., 3.])
bool_1d = np.array([False])
points_2d = np.array([[5., 11., 3.], [3., 2., 1.], [11., 3., 4.], [9., 2., 1.]])
bool_2d = np.array([False, True, False, True])
points_3d = np.array([[[3., 1., 2.], [3., 2., 4.], [10., 3., 11.], [14., 3., 2.]]])
bool_3d = np.array([[True, True, False, False]])

triangle = np.array([[0., 0., 0.], [4., 0., 0.], [0., 0., 4.]])
triangle_point_inside = np.array([2., 0., 2.])
triangle_point_not_coplanar = np.array([2., 2., 2.])
triangle_point_coplanar_but_outside = np.array([5., 0., 3.])

# Same triangle as above, move by vector (2,2,2)
triangle2 = np.array([[2., 2., 2.], [6., 2., 2.], [2., 2., 6.]])
triangle2_point_inside = np.array([4., 2., 4.])
triangle2_point_not_coplanar = np.array([4., 4., 4.])
triangle2_point_coplanar_but_outside = np.array([7., 2., 5.])

polyhedron = np.array([[38., 28., 30.], [31., 3., 43.],  [50., 12., 38.], [34., 45., 18.],
                       [22., 13., 29.], [22., 2., 31.],  [26., 44., 35.], [31., 43., 22.],
                       [22., 43., 13.], [13., 43., 11.], [50., 32., 29.], [26., 35., 18.],
                       [43., 3., 11.],  [26., 3., 44.],  [11., 3., 18.],  [18., 3., 26.],
                       [11., 45, 13.],  [13., 45., 29.], [18., 45., 11.], [2., 32., 31.],
                       [29., 2., 22.],  [35., 12., 18.], [18., 12., 34.], [34., 12., 50.],
                       [34., 50., 45.], [45., 50., 29.], [3., 30., 44.],  [29., 32., 2.],
                       [30., 28., 44.], [50., 30., 32.], [37., 12., 35.], [44., 28., 35.],
                       [35., 28., 37.], [32., 30., 31.], [31., 30., 3.],  [38., 30., 50.],
                       [37., 28., 38.], [38., 12., 37.]])


class TestGamut(unittest.TestCase):

    @staticmethod
    def generate_sphere(r, n):
        """Generates a sphere or points. Used in tests to generate gamut, and inclusion points.

        :param r: int
            The radius to the points.
        :param n: int
            Number of points to be generated.
        :return: ndarray
            Numpy array dim(n,3) with the points of the sphere.
        """
        theta = np.random.uniform(0, 2 * np.pi, n)
        phi = np.random.uniform(0, np.pi, n)

        x = r * (np.sin(phi) * np.cos(theta))
        y = r * (np.sin(phi) * np.sin(theta))
        z = r * (np.cos(phi))

        sphere = np.vstack((x, y, z)).T

        return sphere

    def test_constructor(self):
        g = gamut.Gamut(space.srgb, data.Points(space.srgb, cube), gamma=1)
        self.assertTrue(isinstance(g, gamut.Gamut))

        g = gamut.Gamut(space.srgb, data.Points(space.srgb, cube), gamma=.2)
        self.assertTrue(isinstance(g, gamut.Gamut))

        g = gamut.Gamut(space.srgb, data.Points(space.srgb, cube), center=[.5, .5, .5], gamma=1)
        self.assertTrue(isinstance(g, gamut.Gamut))

        g = gamut.Gamut(space.srgb, data.Points(space.srgb, cube), center=[.5, .5, .5], gamma=.2)
        self.assertTrue(isinstance(g, gamut.Gamut))

    def test_gamut_initialize(self):
        c_data = data.Points(space.srgb, cube)                # Generating the colour Points object
        g = gamut.Gamut(space.srgb, c_data)
        self.assertTrue(np.allclose(cube_vertices, g.vertices))  # Check that the gamut's vertices are correct.

    def test_is_inside(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        c_data = data.Points(space.srgb, points_3d)
        a = g.is_inside(space.srgb, c_data, t=True)
        self.assertEqual(a.shape, points_3d.shape[:-1])     # Asserts if shape is reduced by 1dim
        self.assertEqual(a.dtype, bool)                     # Asserts is data type in the array is boolean
        self.assertTrue(np.allclose(a, bool_3d))            # Asserts that the returned values are co

        c_data = data.Points(space.srgb, points_3d)
        a = g.is_inside(space.srgb, c_data, t=False)
        self.assertEqual(a.shape, points_3d.shape[:-1])     # Asserts if shape is reduced by 1dim
        self.assertEqual(a.dtype, bool)                     # Asserts is data type in the array is boolean
        self.assertTrue(np.allclose(a, bool_3d))            # Asserts that the returned values are correct

        c_data = data.Points(space.srgb, points_2d)
        a = g.is_inside(space.srgb, c_data, t=False)
        self.assertEqual(a.shape, points_2d.shape[:-1])     # Asserts if shape is reduced by 1dim
        self.assertEqual(a.dtype, bool)                     # Asserts is data type in the array is boolean
        self.assertTrue(np.allclose(a, bool_2d))            # Asserts that the returned values are correct

        c_data = data.Points(space.srgb, points_1d)
        a = g.is_inside(space.srgb, c_data, t=False)
        self.assertEqual(1, a.size)                         # When only one point is sent, still returned a array
        self.assertEqual(a.dtype, bool)                     # Asserts is data type in the array is boolean
        self.assertTrue(np.allclose(a, bool_1d))            # Asserts that the returned values are co

        c_data = data.Points(space.srgb, points_1d)
        a = g.is_inside(space.srgb, c_data, t=True)
        self.assertEqual(1, a.size)                         # When only one point is sent, still returned a array
        self.assertEqual(a.dtype, bool)                     # Asserts is data type in the array is boolean
        self.assertTrue(np.allclose(a, bool_1d))            # Asserts that the returned values are correct

        c_data = data.Points(space.srgb, self.generate_sphere(15, 100))
        g = gamut.Gamut(space.srgb, c_data)

        c_data = data.Points(space.srgb, self.generate_sphere(10, 15))   # Points lie within the sphere(inclusion = true)
        a = g.is_inside(space.srgb, c_data)
        self.assertTrue(np.allclose(a, np.ones(a.shape)))              # Assert that all points lie within the gamut

        c_data = data.Points(space.srgb, self.generate_sphere(20, 15))   # Points lie outside the sphere(inclusion = true)
        a = g.is_inside(space.srgb, c_data)
        self.assertTrue(np.allclose(a, np.zeros(a.shape)))             # Assert that all points lie without the gamut

    def test_get_vertices(self):
        c_data = data.Points(space.srgb, cube)  # Generating the colour Points object
        g = gamut.Gamut(space.srgb, c_data)
        n1_data = np.array([[0, 0, 0],      # 0  vertices     Array with just the vertices used for comparison.
                           [10, 0, 0],      # 1  vertices
                           [10, 10, 0],     # 2  vertices
                           [0, 10, 0],      # 3  vertices
                           [10, 10, 10],    # 6  vertices
                           [10, 0, 10],     # 8  vertices
                           [0, 0, 10],      # 9  vertices
                           [0, 10, 10]])    # 10 vertices

        vertices = g.get_vertices(cube)
        self.assertTrue(np.array_equiv(n1_data, vertices))    # Compares return array with the known vertices array.

        vertices = g.get_vertices(cube)                       # Calls the function and add the vertices to the array.
        self.assertTrue(np.array_equiv(n1_data, vertices))    # Compares returned array with the known vertices array.

    # # Uncomment and run to see that a gamut is plotted.
    # def test_plot_surface(self):                      # Test for gamut.Gamut.plot_surface
    #     fig = plt.figure()                            # Creates a figure
    #     ax = fig.add_subplot(111, projection='3d')    # Creates a 3D plot ax
    #
    #     c_data = data.Points(space.srgb, polyhedron)    # Generating the colour Points object
    #     g = gamut.Gamut(space.srgb, c_data)           # Creates a new gamut
    #
    #     sp = g.space                                  # Specifies the color space
    #     g.plot_surface(sp, ax)                        # Calls the plot function

    def test_in_line(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        self.assertTrue(g.in_line(np.array([[2, 2, 2], [2, 2, 2]]), np.array([2, 2, 2])))  # All points equal.
        self.assertFalse(g.in_line(line, point_not_in_line))            # Point in NOT on line
        self.assertFalse(g.in_line(line, point_opposite_direction_than_line))    # Point opposite dir then line
        self.assertFalse(g.in_line(line, point_further_away_than_line))          # Point is is further then line
        self.assertTrue(g.in_line(line, point_in_line))                          # Point is on line
        self.assertFalse(g.in_line(np.array([[3, 3, 3], [4, 4, 4]]), np.array([5, 5, 5])))  # Point is on line

        self.assertFalse(g.interior(line, point_not_in_line))            # Point in NOT on line
        self.assertFalse(g.interior(line, point_opposite_direction_than_line))    # Point opposite dir then line
        self.assertFalse(g.interior(line, point_further_away_than_line))          # Point is is further then line
        self.assertTrue(g.interior(line, point_in_line))                          # Point is on line
        self.assertFalse(g.interior(np.array([[3, 3, 3], [4, 4, 4]]), np.array([5, 5, 5])))  # Point is on line

    def test_in_tetrahedron(self):
        c_data = data.Points(space.srgb, tetrahedron)
        g = gamut.Gamut(space.srgb, c_data)

        self.assertTrue(g.in_tetrahedron(tetrahedron, tetra_p_inside))        # Point is on the tetrahedron
        self.assertFalse(g.in_tetrahedron(tetrahedron, tetra_p_not_inside))   # Point is NOT on tetrahedron
        self.assertTrue(g.in_tetrahedron(tetrahedron, tetra_p_on_surface))    # Point is on a simplex(counts as inside)

        self.assertTrue(g.interior(tetrahedron, tetra_p_inside))              # Point is on the tetrahedron
        self.assertFalse(g.interior(tetrahedron, tetra_p_not_inside))         # Point is NOT on tetrahedron
        self.assertTrue(g.interior(tetrahedron, tetra_p_on_surface))

    def test_in_triangle(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        self.assertFalse(g.in_triangle(triangle, triangle_point_not_coplanar))
        self.assertFalse(g.in_triangle(triangle, triangle_point_coplanar_but_outside))
        self.assertTrue(g.in_triangle(triangle, triangle_point_inside))

        self.assertFalse(g.in_triangle(triangle2, triangle2_point_not_coplanar))
        self.assertFalse(g.in_triangle(triangle2, triangle2_point_coplanar_but_outside))
        self.assertTrue(g.in_triangle(triangle2, triangle2_point_inside))

        self.assertFalse(g.interior(triangle, triangle_point_not_coplanar))
        self.assertFalse(g.interior(triangle, triangle_point_coplanar_but_outside))
        self.assertTrue(g.interior(triangle, triangle_point_inside))

        self.assertFalse(g.interior(triangle2, triangle2_point_not_coplanar))
        self.assertFalse(g.interior(triangle2, triangle2_point_coplanar_but_outside))
        self.assertTrue(g.interior(triangle2, triangle2_point_inside))

    def test_sign(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        # The tetrahedron should have a positive signed volume.
        self.assertEqual(1, g.sign(np.array([[-2, 0, 0], [0, -2, 0], [0, 0, 0], [0, 0, 2]])))
        # The tetrahedron should have no volume.
        self.assertEqual(0, g.sign(np.array([[0, 0, 0], [2, 0, 0], [0, 2, 0], [0.5, 0.5, 0]])))
        # The tetrahedron should have a negative signed volume.
        self.assertEqual(-1, g.sign(np.array([[10, 10, 10], [0, 10, 10], [10, 0, 10], [10, 10, 0]])))

    def test_is_coplanar(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        points = np.array([[0, 0, 0], [2, 2, 0], [3, 3, 0], [1, 1, 0]])  # coplanar points
        self.assertTrue(True, g.is_coplanar(points))

        points = np.array([[0, 0, 1], [2, 2, 0], [3, 3, 0], [1, 1, 0]])  # non-coplanar points
        self.assertFalse(False, g.is_coplanar(points))

    def test_center_of_mass(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        cm = g.center_of_mass(g.get_vertices(g.hull.points))   # Get coordinate for center of the cube
        cp = np.array([5., 5., 5.])                            # Point in center of cube.
        self.assertEqual(cp.all(), cm.all())                   # Assert true that the points are the same.

    def test_true_shape(self):

        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        a = np.array([[0, 0, 0], [2, 2, 2], [2, 2, 2]])
        g.true_shape(a)

        # Test remove duplicates
        a = np.array([[0, 0, 0], [2, 2, 2], [0, 0, 0], [2, 2, 2]])
        self.assertEqual(2, g.true_shape(a).shape[0])

        # Test 3 points on the same line should return outer points
        a = np.array([[0, 0, 0], [2, 2, 2], [3, 3, 3]])
        self.assertTrue(np.allclose(g.true_shape(a), np.array([[0, 0, 0], [3, 3, 3]])))

        # Test 4 points that are actually a triangle
        a = np.array([[0, 0, 0], [0, 3, 0], [3, 0, 0], [1, 1, 0]])
        self.assertTrue(np.allclose(g.true_shape(a), np.array([[0, 0, 0], [0, 3, 0], [3, 0, 0]])))

        # Test 4 points that are all other vertices in a convex polygon
        a = np.array([[0, 0, 0], [0, 3, 0], [3, 0, 0], [5, 5, 0]])
        self.assertTrue(np.allclose(g.true_shape(a), np.array([[0, 0, 0], [0, 3, 0], [3, 0, 0], [5, 5, 0]])))

    def test_modified_convex_hull(self):

        # c_data = data.Points(space.srgb, cube)
        # g = gamut.Gamut(space.srgb, c_data)

        test_points = np.array([[0, 0, 0],           # 0  vertices  # Array with just the vertices used for comparison.
                                [10, 0, 0],          # 1  vertices
                                [10, 10, 0],         # 2  vertices
                                [0, 10, 0],          # 3  vertices
                                [10, 10, 10],        # 6  vertices
                                [10, 0, 10],         # 8  vertices
                                [0, 0, 10],          # 9  vertices
                                [0, 10, 10],         # 10 vertices
                                [4.999, 4.999, 0]])  # Only a vertex in modified hull

        c_data = data.Points(space.srgb, test_points)
        g = gamut.Gamut(space.srgb, c_data, gamma=0.2, center=np.array([5, 5, 5]))

        self.assertTrue(g.vertices.shape[0] == 9)

    def test_get_alpha(self):
        c_data = data.Points(space.srgb, cube)    # Generating the colour Points object.
        g = gamut.Gamut(space.srgb, c_data)     # Creates a new gamut.
        d = [0.001, 0.2, 0.2]
        center = [10, 11, 14]
        n = [5, 3, 2, 9]
        a = g.get_alpha(d, center, n)

    def test_find_plane(self):
        p_data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        c_data = data.Points(space.srgb, cube)    # Generating the colour Points object.
        g = gamut.Gamut(space.srgb, c_data)     # Creates a new gamut.

        d = g.find_plane(p_data)
        r = np.array([-0.57735027, -0.57735027, -0.57735027, -0.57735027])
        np.alltrue(d == r)

    def test_compress(self):
        c_data = data.Points(space.srgb, cube)  # Generating the colour Points object.
        g = gamut.Gamut(space.srgb, c_data)  # Creates a new gamut.

        col_data = data.Points(space.srgb, np.array([[15, 15, 15], [8, 8, 8], [5, 5, 5], [1, 1, 1], [-5, -5, -5]]))
        re_data = g.compress_axis(space.srgb, col_data, 2).get_flattened(space.srgb)

        fasit_data = np.array([[15, 15, 10], [8, 8, 6], [5, 5, 5], [1, 1, 3], [-5, -5, 0]])

        self.assertTrue(np.allclose(fasit_data, re_data))

    def test_intersectionpoint_in_line(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        points = np.array([[15, 5, 5], [5, 15, 5], [5, 5, 15]])                   # points to map
        mod_points = np.array([[10, 5, 5], [5, 10, 5], [5, 5, 10]])               # wanted result

        c_data = data.Points(space.srgb, points)                                    # data.Points object
        re_data = g.intersection_in_line(space.srgb, c_data)                      # data.Points object returned

        self.assertTrue(np.allclose(re_data.get_flattened(space.srgb), mod_points))  # assert that the points are changed

    def test_HPminDE(self):
        c_data = data.Points(space.cielab, cube + np.array([0, -5, -5]))
        g = gamut.Gamut(space.cielab, c_data)

        points = np.array([[0, 8, 8], [4, 0, 9], [4, 4, 3], [0, 10, 0], [15, 1, 0]])
        fasit = np.array([[0, 5, 5], [4, 0, 5], [4, 4, 3], [0, 5, 0], [10, 1, 0]])
        c_data = data.Points(space.cielab, points)
        re_data = g.HPminDE(c_data)
        re_data = re_data.get_flattened(space.cielab)
        self.assertTrue(np.allclose(fasit, re_data))

    def test_minDE(self):
        sphere = self.generate_sphere(6, 10)
        sphere = sphere + np.array([5, 5, 5])
        c_sphere = data.Points(space.cielab, sphere)

        g_cube = data.Points(space.cielab, cube)
        g = gamut.Gamut(space.cielab, g_cube)
        mapped_im = g.minDE(c_sphere)

        result = True
        for index, value in np.ndenumerate(mapped_im.get_flattened(space.cielab)):
            if value > 10:
                result = False
        self.assertTrue(result)

    def test_clip_nearest(self):
        c_data = data.Points(space.srgb, cube)
        g = gamut.Gamut(space.srgb, c_data)

        points = np.array([[5, 5, 15], [5, 5, 15], [5, 5, 15]])                   # points to map
        mod_points = np.array([[5, 5, 10], [5, 5, 10], [5, 5, 10]])               # wanted result

        c_data = data.Points(space.srgb, points)                                    # data.Points object
        re_data = g.clip_nearest(space.srgb, c_data)                              # data.Points object returned

        self.assertTrue(np.allclose(re_data.get_flattened(space.srgb), mod_points))  # assert that the points are changed



if __name__ == '__main__':
    unittest.main(exit=False)
