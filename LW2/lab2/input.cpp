#include <iostream>
#include constants.h
class Rectangle {
private:
    int width;
    int height;
public:
    Rectangle(int w, int h){}
    void setWidth(int w) { width= w; }
    void setHeight(int h) { height=h; }
    int getWidth() const { return width; }
    int getHeight() const { return height; }
    int area() const { return width * height; } // comments
};
int main() {
    Rectangle rect(5, 3);
    std::cout << "Width: " << rect.getWidth() << std::endl;
    std::cout << "Height: " << rect.getHeight() << std::endl;
    std::cout << "Area of the rectangle: " << rect.area() << std::endl;
    rect.setWidth(7);
    rect.setHeight(4);
    std::cout << "Updated area of the rectangle: " << rect.area() << std::endl;
    return 0;
}