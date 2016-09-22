xA, zA = 200, 200
xB, zB = 400, 300
endpoints += [(0, zA), (xA + xB, zA)]
endpoints += [
  # NW right
  (xA + -xA/2, 0),
  (xA + -(xA - 1), 0),
  # NW left
  # SW right
  (0, zA + (zB - 1)),
  # SW left
  (xA + -xA/2, zA + zB),

  # NE left
  (xA + xB/2, 0),
  (xA + (xB - 1), 0),
  # NE right
  # SE left
  (xA + xB, zA + (zB - 1)),
  # SW right
  (xA + xB/2, zA + zB),
]
