# Skeleton-based Shape Decomposition

This code is an implementation of the branchwise skeleton-based decomposition algorithm presented in

Selbach, L., Kowalski, T., Gerwert, K. et al. Shape decomposition algorithms for laser capture microdissection. Algorithms Mol Biol 16, 15 (2021). https://doi.org/10.1186/s13015-021-00193-6

In the context of laser capture microdissection, the goal is to decompose shapes (i.e simple polygons) into fragments of a certain size and shape. This method computes a decomposition based on the skeleton/medial axis of the polygon and allows different constraints as well as optimization goals. 

The decomposition approach can be adapted for different skeletonization methods. However, this implementation is based on the skeleton as computed with the method of

Bai X, Latecki LJ, Liu WY. Skeleton pruning by contour partitioning with discrete curve evolution. IEEE Trans Pattern Anal Mach Intell. 2007 Mar;29(3):449-62. doi: 10.1109/TPAMI.2007.59. PMID: 17224615.

