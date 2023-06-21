// SPDX-License-Identifier: Apache-2.0
// Copyright 2023 The Foundry Visionmongers Ltd

#include <torchtext/csrc/clip_tokenizer.h>
#include <unordered_map>
#include <string>
#include <iostream>

int main()
{
    const std::unordered_map<std::string, int64_t> bpe_encoder = {{"a", 0},{"b", 1},{"c", 2}};

    const std::unordered_map<std::string, int64_t> bpe_merge_ranks = {{"xyz", 0}};

    const std::string separator = " ";
    const std::unordered_map<int64_t, std::string> byte_encoder = 
    {
        {((int64_t)'a'), "a"},
        {((int64_t)'b'), "b"},
        {((int64_t)'c'), "c"}
    };

    torchtext::CLIPEncoder encoder(bpe_encoder, bpe_merge_ranks, separator, byte_encoder);
    auto result_tok = encoder.Tokenize("a b c");

    for(std::string &s : result_tok)
        std::cout << s << "\n";

    std::cout << std::endl;

    return 0;
}
