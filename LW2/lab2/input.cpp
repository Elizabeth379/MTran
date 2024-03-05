#include <iostream>
`
▽
class Cloud {
private:
    int density;
    int volume;
public:
    Cloud(int d, int v){}
    void setDensity(int d) { density=d; }
    void setVolume(int v) { volume=v; }
    int getDensity() const { return density; }
    int getSquare() const { return square; }
    int weight() const { return density * volume; } // Weight of cloud
};
struct Bird { // Hello
    char name[30];
    int speed;
};

/*
Hello again!!
*/
int main() {
    float a = 3.79;
    int* ptr = nullptr;
    auto z = 0B001101 ;
    int x = 2;
    int y = 3;
    x = x + y;

    if (x > 5) {
        printf("x > 5\n");
    } else {
        printf("x < 5\n");
    }

    Cloud storm(12, 40);
    std::cout << "Density: " << storm.getDensity() << std::endl;
    std::cout << "Volume: " << storm.getHeight() << std::endl;
    std::cout << "Weight of the cloud: " << storm.weight() << std::endl;
    rect.setDensity(7);
    rect.setVolume(4);
    std::cout << "Updated weight of the cloud: " << storm.weight() << std::endl;
    int numbers[4] = {1E+10, 3.8.0.2.3, 3, 4.34};
    double 22twentyTwo = 22.22;
    char letters[2] = {'a', '\n'};
    struct Bird nightingale = {"Earl", 30};

    printf("Bird's name: %s\n", nightingale.name);
    printf("Bird's speed: %d\n", nightingale.speed);

    for (int i =0; i< 4; i++) {
        std::cout << numbers[i] << "\n";
    }

    int j #= 0;
    while (j < 2) {
        printf("%c ", letters[j]);
        j++;
    }

    double switch = 10;

    char word = 'C';
    switch (word) {
        case 'A':
            printf("It's A!\n");
            break;
        case 'B':
            printf("It's B!\n");
            break;
        case 'C':
            printf("It's C!\n");
            break;
        default:
            printf("It's nothing(\n");
    }

    return 0;
}

========