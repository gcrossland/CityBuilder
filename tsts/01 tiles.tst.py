from citybuilder import Road, StraightRoadTile, BendingStraightRoadTile, TJunctionRoadTile, NORTH, SOUTH, EAST, WEST, LEFT, RIGHT, RectangularShape, BitmapWorld, City

def T ():
  x = 75
  z = 75

  rs = []

  r = Road(0)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT, 1))
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT, 2))
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT, 2))
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT, 3))
      if True:
        t3 = t2[-1].getBranchRoad().getTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT, 1))
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(TJunctionRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ(), LEFT, 2))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT, 2))
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), RIGHT, 3))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
  rs.append(r)

  r = Road(0)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT, 1))
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT, 2))
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), RIGHT))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT, 3))
      if True:
        t3 = t2[-1].getBranchRoad().getTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), LEFT))
        t3.append(StraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ()))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), RIGHT))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), LEFT))
  rs.append(r)

  for road in rs:
    world = BitmapWorld(RectangularShape(0, 0, x * 2, int(z * 1.5)))
    road.place(world)
    world.placeMarker(x, z)
    r_c = [0]
    def f (road):
      tiles = road.getTiles()
      for i in xrange(0, len(tiles)):
        tile = tiles[i]
        shape = tile.getShape()
        x = shape.getBoundingBox().x0 + 2
        z = shape.getBoundingBox().z0 + 2
        cStr = "{0:0>2d}".format(r_c[0])
        world._d.drawPel(cStr[0], x, z)
        world._d.drawPel(cStr[1], x + 1, z)
        world._d.drawPel('g', x, z + 1)
        world._d.drawPel(str(road.getGeneration()), x, z + 1)
        r_c[0] += 1
      return True
    City.walkRoadTiles((road,), f)
    t("{}", world.getXpm())
