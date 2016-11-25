r0 = ConstantRng(0).choice
r1 = ConstantRng(1).choice
c.addBranches(0, True, c.constantTargetRangFactory, r0, (0.125,), (12,), (False,))
c.addBranches(1, True, c.constantTargetRangFactory, r0, (1,), (1,), (False,))
c.extendRoads(-1, r0, (8,), (False,))
