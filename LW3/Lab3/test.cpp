#include <iostream>
#include <string>
int main() {
    std::string text = "Hello, world!";
    std::string pattern = "world";
    int n = text.length();
    int m = pattern.length();
    int pos = -1;
    for (int i = 0; i <= n - m; ++i) {
        int j;
        for (j = 0; j < m; ++j) {
            if (text[i + j] != pattern[j]) {
                break;
            }
        }
        if (j == m) {
            pos = i;
            break;
        }
    }
    if (pos != -1) {
        std::cout << "Pattern found at position: " << pos << std::endl;
    } else {
        std::cout << "Pattern not found." << std::endl;
    }
    return 0;
}
