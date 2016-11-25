r0 = ConstantRng(0).choice
r1 = ConstantRng(1).choice
c.addBranches(0, True, c.getConstantTargetRangFactory(), r0, (0.125,), (12,), (False,))
c.addBranches(1, False, c.getConstantTargetRangFactory(), r0, (1,), (1,), (False,))
c.extendRoads(1, r0, (8,), (False,))
c.addBranches(1, False, c.getConstantTargetRangFactory(), r1, (1,), (2,), (False,))
