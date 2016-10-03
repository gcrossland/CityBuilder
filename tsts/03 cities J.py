r0 = ConstantRng(0).choice
r1 = ConstantRng(1).choice
c.addBranches(0, True, r0, (0.125,), (12,))
c.addBranches(1, True, r0, (1,), (1,))
c.extendRoads(-1, r0, (8,))
