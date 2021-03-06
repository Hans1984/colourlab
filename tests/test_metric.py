#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_metric: Unittests for all functions in the metric module.

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
from colourlab import metric, data, space, tensor

d1 = data.d_regular(space.cielab,
                    np.linspace(20, 80, 10),
                    np.linspace(-50, 50, 11),
                    np.linspace(-50, 50, 11))
d2 = data.Points(space.cielab,
                 d1.get(space.cielab) + 1 / np.sqrt(3))

poincare_space = space.TransformPoincareDisk(space.cielab, 100)

class TestMetrics(unittest.TestCase):
    def test_metrics(self):
        for met in [metric.dE_ab, metric.dE_uv,
                    metric.dE_00, metric.dE_DIN99,
                    metric.dE_DIN99b, metric.dE_DIN99c,
                    metric.dE_DIN99d, metric.dE_E]:
            self.assertTrue(np.max(met(d1, d2) < 5))
        self.assertTrue(np.max(metric.linear(space.cielab, d1, d2, tensor.dE_ab)) < 2)
        self.assertTrue(np.max(metric.poincare_disk(poincare_space, d1, d2) < 2))
