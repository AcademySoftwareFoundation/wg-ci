
#include <tbb/concurrent_vector.h>
int main()
{
	tbb::concurrent_vector<int> vector;
	vector.push_back(1);
	return 0;
}