/** Geometry helpers for lateral cephalometry. All public angles are degrees. */
export function angleBetweenLinesDegrees(a, b, c, d) {
  const first = Math.atan2(b.y - a.y, b.x - a.x);
  const second = Math.atan2(d.y - c.y, d.x - c.x);
  const deltaRadians = Math.abs(((first - second + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI);
  const deltaDegrees = deltaRadians * 180 / Math.PI;
  return Math.min(deltaDegrees, 180 - deltaDegrees);
}

export function steinerIncisorAngleDegrees(planeStart, planeEnd, apex, tip) {
  const acute = angleBetweenLinesDegrees(planeStart, planeEnd, apex, tip);
  return acute === null ? null : 180 - acute;
}
