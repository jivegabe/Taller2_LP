// Código generado por FunLang Compiler
// Lenguaje funcional -> C++

#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

// ============= Runtime de FunLang =============

// Tipo para listas/arreglos dinámicos
template<typename T>
using List = vector<T>;

// Tipo para matrices
template<typename T>
using Matrix = vector<vector<T>>;

// Funciones de lista
template<typename T>
int length(const List<T>& xs) { return xs.size(); }

template<typename T>
T head(const List<T>& xs) { return xs.front(); }

template<typename T>
List<T> tail(const List<T>& xs) { return List<T>(xs.begin()+1, xs.end()); }

template<typename T>
T last(const List<T>& xs) { return xs.back(); }

template<typename T>
List<T> init(const List<T>& xs) { return List<T>(xs.begin(), xs.end()-1); }

template<typename T>
List<T> take(int n, const List<T>& xs) {
    return List<T>(xs.begin(), xs.begin() + min((size_t)n, xs.size()));
}

template<typename T>
List<T> drop(int n, const List<T>& xs) {
    return List<T>(xs.begin() + min((size_t)n, xs.size()), xs.end());
}

template<typename T>
List<T> reverse_list(const List<T>& xs) {
    List<T> result(xs.rbegin(), xs.rend());
    return result;
}

template<typename T>
List<T> concat(const List<T>& xs, const List<T>& ys) {
    List<T> result = xs;
    result.insert(result.end(), ys.begin(), ys.end());
    return result;
}

template<typename T>
T sum(const List<T>& xs) {
    T result = 0;
    for (const auto& x : xs) result += x;
    return result;
}

template<typename T>
T product(const List<T>& xs) {
    T result = 1;
    for (const auto& x : xs) result *= x;
    return result;
}

template<typename T>
bool elem(const T& x, const List<T>& xs) {
    return find(xs.begin(), xs.end(), x) != xs.end();
}

// Función range [a..b]
List<int> range(int start, int end) {
    List<int> result;
    for (int i = start; i <= end; i++) result.push_back(i);
    return result;
}

// Función range con paso [a,b..c]
List<int> range_step(int start, int next, int end) {
    List<int> result;
    int step = next - start;
    if (step > 0) {
        for (int i = start; i <= end; i += step) result.push_back(i);
    } else if (step < 0) {
        for (int i = start; i >= end; i += step) result.push_back(i);
    }
    return result;
}

// Map
template<typename T, typename F>
auto map_list(F f, const List<T>& xs) {
    List<decltype(f(xs[0]))> result;
    for (const auto& x : xs) result.push_back(f(x));
    return result;
}

// Filter
template<typename T, typename F>
List<T> filter_list(F f, const List<T>& xs) {
    List<T> result;
    for (const auto& x : xs) if (f(x)) result.push_back(x);
    return result;
}

// Foldl
template<typename T, typename R, typename F>
R foldl(F f, R acc, const List<T>& xs) {
    for (const auto& x : xs) acc = f(acc, x);
    return acc;
}

// Funciones de I/O
template<typename T>
void print(const T& x) { cout << x; }

template<typename T>
void println(const T& x) { cout << x << endl; }

string readLine() { string s; getline(cin, s); return s; }
int readInt() { int x; cin >> x; return x; }
double readFloat() { double x; cin >> x; return x; }

// Conversiones
int toInt(double x) { return (int)x; }
int toInt(const string& s) { return stoi(s); }
double toFloat(int x) { return (double)x; }
double toFloat(const string& s) { return stod(s); }
string toString(int x) { return to_string(x); }
string toString(double x) { return to_string(x); }

// Funciones matemáticas adicionales
template<typename T>
T min_val(T a, T b) { return a < b ? a : b; }

template<typename T>
T max_val(T a, T b) { return a > b ? a : b; }

// ============= Fin Runtime =============

// Funciones
template<typename T0, typename T1>
T0 gcd(T0 a, T1 b) {
    return ((b == 0) ? a : gcd(b, (a % b)));
}


int main() {
    [&]() { println("=== Algoritmo de Euclides ==="); auto a1 = 48; auto b1 = 18; print("MCD(48, 18) = "); auto r1 = gcd(a1, b1); println(r1); auto a2 = 56; auto b2 = 98; print("MCD(56, 98) = "); auto r2 = gcd(a2, b2); println(r2); auto a3 = 270; auto b3 = 192; print("MCD(270, 192) = "); auto r3 = gcd(a3, b3); println(r3); return 0; }();
    return 0;
}