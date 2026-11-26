/** Geometry helpers for lateral cephalometry. All public angles are degrees. */
export function angleBetweenLinesDegrees(a, b, c, d) {
  const firstX = b.x - a.x, firstY = b.y - a.y;
  const secondX = d.x - c.x, secondY = d.y - c.y;
  if (Math.hypot(firstX, firstY) === 0 || Math.hypot(secondX, secondY) === 0) return null;
  const first = Math.atan2(firstY, firstX);
  const second = Math.atan2(secondY, secondX);
  const deltaRadians = Math.abs(((first - second + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI);
  const deltaDegrees = deltaRadians * 180 / Math.PI;
  return Math.min(deltaDegrees, 180 - deltaDegrees);
}

export function steinerIncisorAngleDegrees(planeStart, planeEnd, apex, tip) {
  const acute = angleBetweenLinesDegrees(planeStart, planeEnd, apex, tip);
  return acute === null ? null : 180 - acute;
}
