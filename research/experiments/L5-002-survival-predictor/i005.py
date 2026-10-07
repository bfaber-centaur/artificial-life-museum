"""I005 rear deletion (L5-002 pre-registration): an unseen disturbance for the out-of-sample check.

Zero every cell within s*R of the point 0.5 R behind the centroid (c - 0.5 R h),
in Lane 4's creature frame. Importing this module registers it as
alm.disturb.INTERVENTIONS["I005"].
"""
from alm import disturb


def i005_rear_deletion(A, frame, s, R, behind=0.5):
    px = frame.cx - behind * R * frame.hx
    py = frame.cy - behind * R * frame.hy
    dx, dy = disturb.offsets(A.shape, px, py)
    out = A.copy()
    out[dx ** 2 + dy ** 2 < (s * R) ** 2] = 0.0
    return out


disturb.INTERVENTIONS.setdefault("I005", i005_rear_deletion)
