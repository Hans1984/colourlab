#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_data: Unittests for all functions in the data module.

Copyright (C) 2017 Ivar Farup

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import numpy as np
import matplotlib
from colourlab import data, space

# Test data

col1 = np.array([.5, .5, .5])
col2 = np.array([[.5, .5, .5]])
col3 = np.array([[1e-10, 1e-10, 1e-10],
                 [.95, 1., 1.08],
                 [.5, .5, .5]])
col4 = np.array([[[1e-10, 1e-10, 1e-10],
                  [.95, 1., 1.08],
                  [.5, .5, .5]],
                 [[1e-10, 1e-10, 1e-10],
                  [.95, 1., 1.08],
                  [.5, .5, .5]]])

vec1 = .1 * np.random.rand(col1.shape[0])
vec2 = .1 * np.random.rand(col2.shape[0],
                           col2.shape[1])
vec3 = .1 * np.random.rand(col3.shape[0],
                           col3.shape[1])
vec4 = .1 * np.random.rand(col4.shape[0],
                           col4.shape[1],
                           col4.shape[2])

tens1 = np.eye(3)
tens2 = np.array([np.eye(3)])
tens3 = np.array([np.eye(3), np.eye(3), np.eye(3)])
tens4 = np.array([[np.eye(3), np.eye(3), np.eye(3)],
                  [np.eye(3), np.eye(3), np.eye(3)]])

d1 = data.Points(space.xyz, col1)
d2 = data.Points(space.xyz, col2)
d3 = data.Points(space.xyz, col3)
d4 = data.Points(space.xyz, col4)

v1 = data.Vectors(space.xyz, vec1, d1)
v2 = data.Vectors(space.xyz, vec2, d2)
v3 = data.Vectors(space.xyz, vec3, d3)
v4 = data.Vectors(space.xyz, vec4, d4)

t1 = data.Tensors(space.xyz, tens1, d1)
t2 = data.Tensors(space.xyz, tens2, d2)
t3 = data.Tensors(space.xyz, tens3, d3)
t4 = data.Tensors(space.xyz, tens4, d4)


# Tests

class TestPoints(unittest.TestCase):

    def test_get(self):
        self.assertEqual(d1.get(space.xyz).shape, (3, ))
        self.assertEqual(d2.get(space.xyz).shape, (1, 3))
        self.assertEqual(d3.get(space.xyz).shape, (3, 3))
        self.assertEqual(d4.get(space.xyz).shape, (2, 3, 3))

    def test_get_flattened(self):
        self.assertEqual(d1.get_flattened(space.xyz).shape, (1, 3))
        self.assertEqual(d2.get_flattened(space.xyz).shape, (1, 3))
        self.assertEqual(d3.get_flattened(space.xyz).shape, (3, 3))
        self.assertEqual(d4.get_flattened(space.xyz).shape, (6, 3))

    def test_implicit_convert(self):
        lab1 = d1.get(space.cielab)
        lab2 = d2.get(space.cielab)
        lab3 = d3.get(space.cielab)
        lab4 = d4.get(space.cielab)
        dd1 = data.Points(space.cielab, lab1)
        dd2 = data.Points(space.cielab, lab2)
        dd3 = data.Points(space.cielab, lab3)
        dd4 = data.Points(space.cielab, lab4)
        self.assertTrue(np.allclose(col1, dd1.get(space.xyz)))
        self.assertTrue(np.allclose(col2, dd2.get(space.xyz)))
        self.assertTrue(np.allclose(col3, dd3.get(space.xyz)))
        self.assertTrue(np.allclose(col4, dd4.get(space.xyz)))

    def test_new_white_point(self):
        self.assertTrue(
            np.allclose(
                data.white_D50.get(space.cielab),
                data.white_D65.new_white_point(
                    space.xyz,
                    data.white_D65,
                    data.white_D50).get(space.cielab)))


class TestVectors(unittest.TestCase):

    def test_get(self):
        self.assertEqual(v1.get(space.xyz).shape, (3, ))
        self.assertEqual(v2.get(space.xyz).shape, (1, 3))
        self.assertEqual(v3.get(space.xyz).shape, (3, 3))
        self.assertEqual(v4.get(space.xyz).shape, (2, 3, 3))

    def test_get_flattened(self):
        self.assertEqual(v1.get_flattened(space.xyz).shape, (1, 3))
        self.assertEqual(v2.get_flattened(space.xyz).shape, (1, 3))
        self.assertEqual(v3.get_flattened(space.xyz).shape, (3, 3))
        self.assertEqual(v4.get_flattened(space.xyz).shape, (6, 3))

    def test_implicit_convert(self):
        lab1 = v1.get(space.cielab)
        lab2 = v2.get(space.cielab)
        lab3 = v3.get(space.cielab)
        lab4 = v4.get(space.cielab)
        vv1 = data.Vectors(space.cielab, lab1, d1)
        vv2 = data.Vectors(space.cielab, lab2, d2)
        vv3 = data.Vectors(space.cielab, lab3, d3)
        vv4 = data.Vectors(space.cielab, lab4, d4)
        self.assertTrue(np.allclose(vec1, vv1.get(space.xyz)))
        self.assertTrue(np.allclose(vec2, vv2.get(space.xyz)))
        self.assertTrue(np.allclose(vec3, vv3.get(space.xyz)))
        self.assertTrue(np.allclose(vec4, vv4.get(space.xyz)))


class TestTensors(unittest.TestCase):

    def test_get(self):
        self.assertEqual(t1.get(space.xyz).shape, (3, 3))
        self.assertEqual(t2.get(space.xyz).shape, (1, 3, 3))
        self.assertEqual(t3.get(space.xyz).shape, (3, 3, 3))
        self.assertEqual(t4.get(space.xyz).shape, (2, 3, 3, 3))

    def test_get_flattened(self):
        self.assertEqual(t1.get_flattened(space.xyz).shape, (1, 3, 3))
        self.assertEqual(t2.get_flattened(space.xyz).shape, (1, 3, 3))
        self.assertEqual(t3.get_flattened(space.xyz).shape, (3, 3, 3))
        self.assertEqual(t4.get_flattened(space.xyz).shape, (6, 3, 3))

    def test_implicit_convert(self):
        self.assertEqual(t1.get(space.srgb).shape, (3, 3))
        self.assertEqual(t2.get(space.srgb).shape, (1, 3, 3))
        self.assertEqual(t3.get(space.srgb).shape, (3, 3, 3))
        self.assertEqual(t4.get(space.srgb).shape, (2, 3, 3, 3))

    def test_get_ellipse_parameters(self):
        ell1 = t1.get_ellipse_parameters(space.xyz)
        ell2 = t2.get_ellipse_parameters(space.xyz)
        ell3 = t3.get_ellipse_parameters(space.xyz)
        ell4 = t4.get_ellipse_parameters(space.xyz)
        self.assertEqual(ell1.shape, (1, 3))
        self.assertEqual(ell2.shape, (1, 3))
        self.assertEqual(ell3.shape, (3, 3))
        self.assertEqual(ell4.shape, (6, 3))

    def test_get_ellipses(self):
        ell1 = t1.get_ellipses(space.xyz)
        ell2 = t2.get_ellipses(space.xyz)
        ell3 = t3.get_ellipses(space.xyz)
        ell4 = t4.get_ellipses(space.xyz)
        self.assertEqual(len(ell1), 1)
        self.assertEqual(len(ell2), 1)
        self.assertEqual(len(ell3), 3)
        self.assertEqual(len(ell4), 6)
        self.assertIsInstance(ell1[0], matplotlib.patches.Ellipse)
        self.assertIsInstance(ell2[0], matplotlib.patches.Ellipse)
        self.assertIsInstance(ell3[0], matplotlib.patches.Ellipse)
        self.assertIsInstance(ell4[0], matplotlib.patches.Ellipse)


class TestFunctions(unittest.TestCase):

    def test_d_functions(self):
        for func in [data.d_XYZ_31, data.d_XYZ_64, data.d_Melgosa]:
            d = func()
            self.assertIsInstance(d, data.Points)
        for arg in ['all', 'real', '1929']:
            d, n, l = data.d_Munsell(arg)
            self.assertIsInstance(n, list)
            self.assertIsInstance(l, np.ndarray)
            self.assertIsInstance(d, data.Points)
        try:
            d, n, l = data.d_Munsell('dummy')
        except Exception as e:
            self.assertIsInstance(e, RuntimeError)

    def test_d_regular(self):
        d = data.d_regular(space.xyz, np.linspace(0, 1, 10),
                           np.linspace(0, 1, 10), np.linspace(0, 1, 10))
        self.assertIsInstance(d, data.Points)
        dd = d.get(space.xyz)
        self.assertEqual(dd.shape, (1000, 3))

    def test_g_functions(self):
        for func in [data.g_MacAdam, data.g_three_observer,
                     data.g_Melgosa_Lab, data.g_Melgosa_xyY]:
            g = func()
            self.assertIsInstance(g, data.Tensors)
        for arg in ['P', 'A', '2']:
            g = data.g_BFD(arg)
            self.assertIsInstance(g, data.Tensors)

    def test_m_functions(self):
        r = data.m_rit_dupont()
        self.assertIsInstance(r, dict)
        r = data.m_rit_dupont_T50()
        self.assertIsInstance(r, dict)
