# This calculates the perpendicular line of a given line and a point
def calcPerpendicularSlopeLineIntercept(lineM, lineB, pointX, pointY):
  # the perpendicular slope is the negative reciprocal of original m
  mPerpendicular = -1 / lineM
  bPerpendicular = 0 # as unknown at this time
  print('mPerpendicular:', mPerpendicular)
  print('bPerpendicular:', bPerpendicular)


  # This is the formula for the perpendicular line
  # m = (y2 - y1) / (x2 - x1)

  #y = mx+b
  #y2 = m2x2+b2

  # m2 = -(1/m)
  # m2 = -.74
  # b2 = y2 - m2x2
  # b2 = 300 - -(1/1.3566433566433567) * 900
  # b2 = 964

  # y1 = 1.4*x+-130
  # y2 = -.74*x2+964

  # 1.4*x-130 = -.74*x+964
  # 1.4x+.74x = 964+130
  # 2.14x = 1090
  # x=1090/2.14

  # the perpendicular slope is the negative reciprocal of original m
  secondm = -(1/lineM)
  secondb = pointY - (secondm*pointX)
  print('secondm', secondm)
  print('secondb', secondb)

  interceptX = (secondb - lineB) / (lineM - secondm)
  interceptY = secondm * interceptX + secondb

  print('interceptX', interceptX)
  print('interceptY', interceptY)

  intInterceptX = int(interceptX)
  intInterceptY = int(interceptY)

  interceptPoint = [intInterceptX, intInterceptY] #expecting this number
  return interceptX, interceptY
  # return {
  #   interceptX: interceptX,
  #   interceptY: interceptY,

  # }
  # return interceptPoint