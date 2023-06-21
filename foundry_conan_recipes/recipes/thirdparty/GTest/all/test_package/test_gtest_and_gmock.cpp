#include "gmock/gmock.h"
#include "gtest/gtest.h"

class MyClass {
public:
  virtual ~MyClass() {}
  virtual void MyMethod() = 0;
};

class MockMyClass : public MyClass {
 public:
  MOCK_METHOD(void, MyMethod, (), (override));
};

TEST(cubicTest, myCubeTest)
{
    EXPECT_EQ(1000, 10*10*10);
}

TEST(cubicTest, squareTest)
{
    EXPECT_EQ(100, 10*10);
}

// Tests the linkage of the ReturnNull action.
TEST(MockTest, TestMockCallOnce) {
  MockMyClass mock;

  EXPECT_CALL(mock, MyMethod()).Times(1);
  mock.MyMethod();
}

int main(int argc, char* argv[])
{
    // Offscreen GoogleTest based tests
    ::testing::InitGoogleTest(&argc, argv);
    int errorCode = RUN_ALL_TESTS();
    return errorCode;
}
