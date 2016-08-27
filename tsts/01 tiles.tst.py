from citybuilder import StraightRoadTile, TJunctionRoadTile, NORTH, SOUTH, EAST, WEST, LEFT, RIGHT, RectangularShape, BitmapWorld, City

def T ():
  x = 50
  z = 50

  t0 = []
  t0.append(StraightRoadTile(NORTH, x, z))
  t0.append(StraightRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), LEFT))
  if True:
    t1 = t0[-1].getBranchRoadTiles()
    t1.append(StraightRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), LEFT))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), LEFT))
      if True:
        t3 = t2[-1].getBranchRoadTiles()
        t3.append(StraightRoadTile(t2[-1].getBranchDirection(), t2[-1].getBranchX(), t2[-1].getBranchZ()))
  t0.append(TJunctionRoadTile(t0[-1].getNextDirection(), t0[-1].getNextX(), t0[-1].getNextZ(), RIGHT))
  if True:
    t1 = t0[-1].getBranchRoadTiles()
    t1.append(TJunctionRoadTile(t0[-1].getBranchDirection(), t0[-1].getBranchX(), t0[-1].getBranchZ(), LEFT))
    t1.append(TJunctionRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ(), RIGHT))
    if True:
      t2 = t1[-1].getBranchRoadTiles()
      t2.append(StraightRoadTile(t1[-1].getBranchDirection(), t1[-1].getBranchX(), t1[-1].getBranchZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(StraightRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ()))
      t2.append(TJunctionRoadTile(t2[-1].getNextDirection(), t2[-1].getNextX(), t2[-1].getNextZ(), RIGHT))
    t1.append(StraightRoadTile(t1[-1].getNextDirection(), t1[-1].getNextX(), t1[-1].getNextZ()))

  world = BitmapWorld(RectangularShape(0, 0, x * 2, int(z * 1.5)))
  for tile in t0:
    tile.place(world)
  world.placeMarker(x, z)
  r_c = [0]
  def f (tiles, generation):
    for i in xrange(0, len(tiles)):
      tile = tiles[i]
      shape = tile.getShape()
      assert isinstance(shape, RectangularShape)
      x = shape.x0 + 2
      z = shape.z0 + 2
      cStr = "{0:0>2d}".format(r_c[0])
      world._d.drawPel(cStr[0], x, z)
      world._d.drawPel(cStr[1], x + 1, z)
      world._d.drawPel('g', x, z + 1)
      world._d.drawPel(str(generation), x, z + 1)
      r_c[0] += 1
  City.walkRoadTiles((t0,), 0, f)
  t("{}", "\n".join(world.get()))
