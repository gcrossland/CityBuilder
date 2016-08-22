from citybuilder import StraightRoadTile, TJunctionRoadTile, NORTH, SOUTH, EAST, WEST, RectangularShape, BitmapWorld

def T ():
  x = 50
  z = 50

  t0 = []
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), WEST, 1))
  if True:
    t1 = t0[-1].getBranchRoadTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), NORTH, 2))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), SOUTH, 2))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), EAST, 3))
      if True:
        t3 = t2[-1].getBranchRoadTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), EAST, 1))
  if True:
    t1 = t0[-1].getBranchRoadTiles()
    t1.append(TJunctionRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ(), NORTH, 2))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), SOUTH, 2))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), WEST, 3))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))

  world = BitmapWorld(RectangularShape(0, 0, x * 2, int(z * 1.5)))
  for tile in t0:
    tile.place(world)
  world.placeMarker(x, z)
  t("{}", "\n".join(world.get()))
