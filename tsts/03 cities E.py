r = ConstantRng(0).choice
c.addBranches(0, True, c.constantTargetRangFactory, r, (0.125,), (7,), (False,))
c.addBranches(-1, True, c.constantTargetRangFactory, r, (1,), (9,), (False,))
