#include <algorithm>
#include <iostream>
#include <limits>

#include <muParser.h>

static mu::value_type MySqr(mu::value_type value)
{  
    return value * value;
}

static bool compare(mu::value_type x, mu::value_type y)
{
    return std::fabs(x - y) <= std::numeric_limits<mu::value_type>::epsilon();
}

static mu::value_type calcPi(mu::Parser& p)
{
    p.SetExpr("_pi");
    return p.Eval();
}

int main(int argc, char *argv[])
{
    try
    {
        mu::Parser p;
        mu::value_type const pi = calcPi(p);
        mu::value_type var_a = 1;        
       
        p.DefineVar("a", &var_a); 
        p.DefineFun("MySqr", MySqr); 
        p.SetExpr("MySqr(a)*_pi+min(10,a)");

        for (std::size_t a = 0; a < 100; ++a)
        {
            var_a = static_cast<float>(a);  // Change value of variable a
            
            auto expected = MySqr(var_a) * pi + std::min(static_cast<size_t>(10), a);
            auto value = p.Eval();
            
            if (!compare(value, expected))
            {
                return 1;
            }
        }
    }
    catch (mu::Parser::exception_type &e)
    {
        std::cout << e.GetMsg() << std::endl;
        return 1;
    }
    
    return 0;
}
