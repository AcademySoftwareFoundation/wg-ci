#include <boost/locale/localization_backend.hpp>
#include <iostream>
#include <algorithm>

int main()
{
    auto manager = boost::locale::localization_backend_manager::global();
    const auto backends = manager.get_all_backends();
    auto icu_it = std::find(begin(backends), end(backends), "icu");
    if (icu_it == std::end(backends))
    {
        return 0;
    }
    std::cerr << "Found the 'icu' in locale backends. Do not compile boost with icu, and disable icu in boost locale." << std::endl;
    std::cerr << "All backends found:" << std::endl;
    for (const auto &backend : backends)
    {
        std::cerr << "\t" << backend << std::endl;
    }
    return 1;
}
