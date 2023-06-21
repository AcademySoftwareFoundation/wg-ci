#include <cstring>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

template <typename T>
using deleter_unique_ptr = std::unique_ptr<T, std::function<void(T*)>>;

void free_pcre2_code(pcre2_code* const re)
{
    if (re)
        pcre2_code_free(re);
}

void free_pcre2_match_data(pcre2_match_data* const match_data)
{
    pcre2_match_data_free(match_data);
}

int main()
{
    const char pattern[]{"([0-9]+)-([0-9]+)-([0-9]+)"};
    const char subject[]{"Current date: 2023-01-31"};

    const uint32_t options{0};
    PCRE2_SIZE erroffset;
    int errcode;

    using pcre2_code_ptr = deleter_unique_ptr<pcre2_code>;
    pcre2_code_ptr re_ptr{pcre2_compile(reinterpret_cast<PCRE2_SPTR8>(pattern),
                                        strlen(pattern),
                                        options,
                                        &errcode,
                                        &erroffset,
                                        nullptr),
                          free_pcre2_code};
    if (!re_ptr)
    {
        PCRE2_UCHAR8 buffer[128];
        pcre2_get_error_message(errcode, buffer, sizeof(buffer) - 1);

        std::cerr << "ERROR: " << buffer << " (" << errcode << ")" << std::endl;
        return 1;
    }

    const uint32_t ovecsize{128};
    using pcre2_match_data_ptr = deleter_unique_ptr<pcre2_match_data>;
    pcre2_match_data_ptr match_data_ptr{pcre2_match_data_create(ovecsize, nullptr),
                                        free_pcre2_match_data};

    const int result{pcre2_match(re_ptr.get(),
                                 reinterpret_cast<PCRE2_SPTR8>(subject),
                                 strlen(subject),
                                 0,
                                 options,
                                 match_data_ptr.get(),
                                 nullptr)};
    if (result > 0)
    {
        std::vector<std::string> matches;

        PCRE2_SIZE* const ovector{pcre2_get_ovector_pointer(match_data_ptr.get())};
        for (int i = 0; i < result; ++i)
        {
            const PCRE2_SPTR start{reinterpret_cast<PCRE2_SPTR8>(subject) + ovector[2 * i]};
            const PCRE2_SIZE slen{ovector[2 * i + 1] - ovector[2 * i]};

            matches.push_back(std::string(reinterpret_cast<const char*>(start), slen));
        }

        if (matches.size() != 1 + 3)
        {
            std::cerr << "ERROR: Expected 3 matches; found " << matches.size() << std::endl;
            for (const std::string& match : matches)
            {
                std::cerr << "\t" << match << std::endl;
            }
            return 1;
        }

        if (matches[0] != "2023-01-31" || matches[1] != "2023" || matches[2] != "01" ||
            matches[3] != "31")
        {
            std::cerr << "ERROR: Expected \"2023\", \"01\", and \"31\"; found "
                      << "\"" << matches[1] << "\", "
                      << "\"" << matches[2] << "\", and "
                      << "\"" << matches[3] << "\"" << std::endl;
            return 1;
        }
    }
    else
    {
        std::cerr << "ERROR: Unexpected result: " << result << std::endl;
        return 1;
    }

    return 0;
}
