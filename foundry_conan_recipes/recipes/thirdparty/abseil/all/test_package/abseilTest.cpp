#include "absl/container/flat_hash_set.h"
#include "absl/numeric/int128.h"

int main()
{
    absl::flat_hash_set<absl::uint128> set;
    set.insert(absl::MakeUint128(1, 0));  // 2^64
    set.insert(absl::MakeUint128(2, 0));  // 2^65
    if (set.size() != 2)
        return 1;
    return 0;
}
