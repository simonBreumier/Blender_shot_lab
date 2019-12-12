"""
Finds the top and left cameras intrinsinc and distortion matrices and the rotation/translation matrix between the
cameras and the sample
"""
from calib_len import get_cam_matrix
from find_sample_ori import get_transfo_mat
import numpy as np

print("Getting cameras matrix")
mtx_top, dist_top = get_cam_matrix("../lens_dist_calib")
mtx_left, dist_left = get_cam_matrix("../lens_dist_calib")

print("Getting reference frame transformations")
R_top, T_top = get_transfo_mat("../sources/tilted_top.png", mtx_top, dist_top)
R_left, T_left = get_transfo_mat("../sources/tilted_left.png", mtx_left, dist_left)

print("Saving results in res")
np.savetxt("res/mtx_top", mtx_top)
np.savetxt("res/mtx_left", mtx_left)
np.savetxt("res/dist_top", dist_top)
np.savetxt("res/dist_left", dist_left)
np.savetxt("res/R_top", R_top)
np.savetxt("res/R_left", R_left)
np.savetxt("res/T_top", T_top)
np.savetxt("res/T_left", T_left)