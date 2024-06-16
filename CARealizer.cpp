#include <vector>
#include <chrono>
#include <ctime>
#include <random>
#include <iostream>
#include <sstream>
#include <fstream>
#include <thread>
#include <cassert>

template<class T>
class Field {
private:
    std::vector< std::vector<T> > _field;
public:
    explicit Field() = default;
    explicit Field(uint32_t height, uint32_t width, T default_val = {}) :
    _field(height, std::vector<T>(width, default_val))
    {}
    ~Field() = default;

    std::vector<T>& operator[](uint32_t row) { return _field[row]; }
    size_t get_height() { return _field.size(); }
    size_t get_width()  { return (_field.size() ? _field[0].size() : 0); }
};

class Timer {
private:
    std::string timer_name;
    std::chrono::time_point<std::chrono::high_resolution_clock> start, end;
    std::ofstream out_stream;
public:

    static std::string current_time() {
        std::time_t t = std::time(0);
        std::tm* now = std::localtime(&t);
        std::stringstream ss; 
        ss << now->tm_hour           << ":"
        << now->tm_min            << "__"
        << now->tm_mday           << "."
        << (now->tm_mon + 1)      << "."
        << (now->tm_year + 1900);

        return ss.str();
    }

    Timer(std::string _timer_name, std::string _output_file_name, std::vector<std::string> info = {}):
    timer_name(_timer_name), out_stream(std::ofstream(_output_file_name, std::ios::app))                    {
        out_stream << "\n[Timer](\"" << _timer_name    << "\") started\n"
                   << "\tDate = \""  << current_time() << "\"\n";
        for (std::string info_el : info) {
            out_stream << "\t" << info_el << "\n";
        }
        out_stream << std::endl;
        start = std::chrono::high_resolution_clock::now();
    }

    ~Timer() {
        end = std::chrono::high_resolution_clock::now();
        int64_t start_int = start.time_since_epoch().count();
        int64_t   end_int =   end.time_since_epoch().count();

        out_stream << "[Timer](\""         << timer_name            << "\") finished\n"
                   << "\tStart(ns)     = " << start_int             << "\n"
                   << "\tEnd(ns)       = " << end_int               << "\n"
                   << "\tDuration(sec) = " << std::fixed << (end_int - start_int) / 1000000000.L;
        out_stream << "\n_____________________________________________________________________________\n";
    }
};

using cell_t  = bool;
using field_t = Field<cell_t>;
using function_t = cell_t(*)(field_t& _field, uint32_t x, uint32_t y);

class CellurarAutomata {
private:
    field_t field;
    function_t judge_function;
public:
    size_t get_height() { return field.get_height(); }
    size_t get_width()  { return field.get_width();  }

    explicit CellurarAutomata(uint32_t height, uint32_t width, function_t f, int32_t seed = 228) {
        field = field_t(height, width);
        srand(seed);
        judge_function = f;

        for (int i = 0; i < field.get_height(); i++) {
            for (int j = 0; j < field.get_width(); j++) {
                field[i][j] = rand() % 2;
            }
        }

    }
    void _make_step(field_t& new_field, uint32_t cnt_steps, uint32_t lowb_height, uint32_t upb_height) {
        for (; cnt_steps > 0; cnt_steps--) {
            for (uint32_t i = lowb_height; i < upb_height; i++) {
                for (uint32_t j = 0; j < field.get_width(); j++) {
                    new_field[i][j] = judge_function(field, i, j);
                }
            }
        }
    }
    void make_step(uint32_t cnt_steps, uint32_t cnt_threads) {
        field_t new_field(field.get_width(), field.get_height());
        std::vector<std::thread> threads(cnt_threads);
        threads.reserve(cnt_threads);
        uint32_t block_size = (field.get_height() + cnt_threads - 1) / cnt_threads;
        for (uint32_t i = 0; i < cnt_threads; i++) {
            uint32_t lb = i * block_size;
            uint32_t ub = lb + block_size;
            ub = std::min(ub, (uint32_t)field.get_height());
            threads[i] = std::thread(_make_step, this, std::ref(new_field), cnt_steps, lb, ub);
        }
        for (uint32_t i = 0; i < cnt_threads; i++) {
            threads[i].join();
        }
        std::swap(field, new_field);
    }
    void print_field(std::string output_file_name) {
        std::ofstream out_stream(output_file_name);
        for (size_t i = 0; i < field.get_height(); i++) {
            for (size_t j = 0; j < field.get_height(); j++) {
                out_stream << field[i][j];
            }
        }
    }
};

std::string make_info(std::string a, std::string b) {
    return a + b;
}

inline cell_t f(field_t& _field, uint32_t x, uint32_t y) {
    int dx[] = {0, 0, 1, 1, 1, -1, -1, -1};
    int dy[] = {-1, 1, -1, 0, 1, -1, 0, 1};

    int status = _field[x][y], cnt_alive = 0;
    for (int i = 0; i < 8; i++) {
        int nx = dx[i] + x;
        int ny = dy[i] + y;
        if (0 <= nx && nx < _field.get_height() && 0 <= ny && ny < _field.get_width()) {
            cnt_alive += _field[nx][ny];
        }
    }

    if (status == 1) {
        return cell_t{ cnt_alive == 2 || cnt_alive == 3 };
    } else {
        return cell_t{ cnt_alive == 3 };          
    }
}

// ./run.exe <height> <width> <cnt_steps> <cnt_threads>
int main(int argc, char *argv[]) {
    assert(argc > 4);
    int height      = std::atoi(argv[1]);
    int width       = std::atoi(argv[2]);
    int cnt_steps   = std::atoi(argv[3]);
    int cnt_threads = std::atoi(argv[4]);

    CellurarAutomata CA(height, width, f);
    std::string size_info_str = make_info("Size = ", std::to_string(CA.get_height()) + " " + std::to_string(CA.get_width()));
    std::string steps_info_str = make_info("Count_steps = ", std::to_string(cnt_steps));
    std::string parallel_info_str = make_info("Count_threads = ", std::to_string(cnt_threads));
    std::string flags_info_str = make_info("Flags = ", "");
{
    Timer timer("timer", "timer_info.txt",
                {size_info_str,
                 steps_info_str,
                 parallel_info_str,
                 flags_info_str});
    CA.print_field("output_start.txt");

    CA.make_step(20, cnt_threads);
    CA.print_field("output_20.txt");

    CA.make_step(20, cnt_threads);
    CA.print_field("output_40.txt");

    CA.make_step(20, cnt_threads);
    CA.print_field("output_60.txt");
}
    return 0;
}