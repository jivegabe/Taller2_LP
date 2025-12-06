// Código generado por FunLang Compiler
// Lenguaje funcional -> C++

#include <algorithm>
#include <any>
#include <cmath>
#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <queue>
#include <string>
#include <thread>
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

// ============= Runtime de Actores (Básico) =============

// Helper para imprimir any
void print_any(const any& a) {
    if (a.type() == typeid(int)) cout << any_cast<int>(a);
    else if (a.type() == typeid(double)) cout << any_cast<double>(a);
    else if (a.type() == typeid(string)) cout << any_cast<string>(a);
    else if (a.type() == typeid(const char*)) cout << any_cast<const char*>(a);
    else cout << "[any]";
}

void println(const any& x) { print_any(x); cout << endl; }

// Actor simple con cola de mensajes
class Actor {
protected:
    queue<any> mailbox;
    mutex mtx;
    bool running = true;
    thread worker;
    function<void(any)> handler;

public:
    virtual ~Actor() { stop(); }

    void send(any msg) {
        lock_guard<mutex> lock(mtx);
        mailbox.push(msg);
    }

    bool empty() {
        lock_guard<mutex> lock(mtx);
        return mailbox.empty();
    }

    void start() {
        worker = thread([this]() {
            while (running) {
                any msg;
                {
                    lock_guard<mutex> lock(mtx);
                    if (!mailbox.empty()) {
                        msg = mailbox.front();
                        mailbox.pop();
                    } else {
                        this_thread::sleep_for(chrono::milliseconds(10));
                        continue;
                    }
                }
                if (handler) handler(msg);
            }
        });
    }

    void stop() {
        running = false;
        if (worker.joinable()) worker.join();
    }

    void set_handler(function<void(any)> h) { handler = h; }
};

// Sistema de actores simple
class ActorSystem {
    vector<shared_ptr<Actor>> actors;
public:
    template<typename T>
    shared_ptr<T> spawn() {
        auto actor = make_shared<T>();
        actor->start();
        actors.push_back(actor);
        return actor;
    }
    
    void wait_all() {
        // Esperar a que todos los mailboxes estén vacíos
        bool all_empty = false;
        while (!all_empty) {
            all_empty = true;
            for (auto& a : actors) {
                if (!a->empty()) {
                    all_empty = false;
                    break;
                }
            }
            if (!all_empty) this_thread::sleep_for(chrono::milliseconds(10));
        }
        // Pequeña espera para el último mensaje en proceso
        this_thread::sleep_for(chrono::milliseconds(50));
    }
};

ActorSystem actorSystem;

// ============= Fin Runtime de Actores =============

// Funciones
// Actor: printer
class printerActor : public Actor {
public:
    printerActor() {
        set_handler([this](any _msg) { this->handle(_msg); });
    }

    void handle(any _msg) {
        auto msg = _msg;
        println(msg);
    }
};

// Actor: counter
class counterActor : public Actor {
public:
    counterActor() {
        set_handler([this](any _msg) { this->handle(_msg); });
    }

    void handle(any _msg) {
        auto n = _msg;
        println(n);
    }
};


int main() {
    [&]() { auto p = actorSystem.spawn<printerActor>(); auto c = actorSystem.spawn<counterActor>(); p->send("Hola desde actor!"); p->send("Otro mensaje"); c->send(42); println("Mensajes enviados"); return 0; }();
    // Esperar a que los actores procesen todos los mensajes
    actorSystem.wait_all();
    return 0;
}