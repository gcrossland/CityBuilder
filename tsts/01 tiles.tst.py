from citybuilder import Direction, Reldirection, Road, StraightRoadTile, BendingStraightRoadTile, DiagonalRoadTile, StraightToDiagonalRoadTile, DiagonalToStraightRoadTile, TJunctionRoadTile, RectangularShape, BitmapWorld, City
WEST, EAST, NORTH, SOUTH = Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH
SOUTH_EAST, SOUTH_WEST, NORTH_WEST, NORTH_EAST = Direction.SOUTH_EAST, Direction.SOUTH_WEST, Direction.NORTH_WEST, Direction.NORTH_EAST
LEFT, RIGHT = Reldirection.LEFT, Reldirection.RIGHT

def T ():
  x = 75
  z = 75

  rs = []

  r = Road()
  r.init(0, City._INIT_BRANCHISING_STATE)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    t1[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
      if True:
        t3 = t2[-1].getBranchRoad().getTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(TJunctionRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ(), LEFT))
    t1[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    t1[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), RIGHT))
      t2[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
  rs.append((r, True))

  r = Road()
  r.init(0, City._INIT_BRANCHISING_STATE)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(BendingStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
  if True:
    t1 = t0[-1].getBranchRoad().getTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    t1.append(BendingStraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    t1[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
    if True:
      t2 = t1[-1].getBranchRoad().getTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), RIGHT))
      t2.append(BendingStraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      t2[-1].getBranchRoad().init(0, City._INIT_BRANCHISING_STATE)
      if True:
        t3 = t2[-1].getBranchRoad().getTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), LEFT))
        t3.append(StraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ()))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), RIGHT))
        t3.append(BendingStraightRoadTile(t3[-1].getNextDirection(), t3[-1].getNextX(), t3[-1].getNextZ(), LEFT))
  rs.append((r, True))

  r = Road()
  r.init(0, City._INIT_BRANCHISING_STATE)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(EAST, x, z * 2 / 3))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  rs.append((r, False))

  r = Road()
  r.init(0, City._INIT_BRANCHISING_STATE)
  t0 = r.getTiles()
  t0.append(StraightRoadTile(EAST, x, z * 4 / 3))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(StraightToDiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  t0.append(DiagonalRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(DiagonalToStraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  rs.append((r, False))

  for road, renderGenerations in rs:
    world = BitmapWorld(RectangularShape(0, 0, x * 2, int(z * 1.5)))
    road.place(world)
    world.placeMarker(x, z)

    if renderGenerations:
      class DummyCity (City):
        def __init__ (self):
          self._maxGeneration = 3
          self._primaryMainRoads = (road,)
          self._secondaryMainRoads = ()
      c = 0
      for road, generation in DummyCity().getRoads():
        tiles = road.getTiles()
        for i in xrange(0, len(tiles)):
          tile = tiles[i]
          shape = tile.getShape()
          x1 = shape.getBoundingBox().x0 + 2
          z1 = shape.getBoundingBox().z0 + 2
          cStr = "{0:0>2d}".format(c)
          world._d.drawPel(ord(cStr[0]), x1, z1)
          world._d.drawPel(ord(cStr[1]), x1 + 1, z1)
          world._d.drawPel(ord('g'), x1, z1 + 1)
          world._d.drawPel(ord(str(generation)), x1, z1 + 1)
          c += 1

    t("{}", world.getXpm())
