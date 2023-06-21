#include <Eigen/Dense>

#if !defined (EIGEN_MPL2_ONLY)
#error You MUST define EIGEN_MPL2_ONLY
#endif
 
int main()
{
    Eigen::MatrixXd m(2,2);
    
    m(0,0) = 3;
    m(1,0) = 2.5;
    m(0,1) = -1;
    m(1,1) = m(1, 0) + m(0, 1);

    return m(1,1) == 1.5 ? EXIT_SUCCESS : EXIT_FAILURE;
}
